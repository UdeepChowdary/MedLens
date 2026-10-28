"""SQLite-backed cache repository for external API lookups with 7-day TTL."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_factory
from app.models.reference import ExternalReferenceCache
from app.services.references.base import ReferenceData

logger = logging.getLogger(__name__)


class ReferenceCache:
    """Manages TTL-governed cached responses from external pharmacopeial and chemical APIs."""

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._lock = asyncio.Lock()

    @staticmethod
    def make_cache_key(source: str, drug_name: str) -> str:
        """Derives deterministic composite key."""
        return f"{source.strip().lower()}:{drug_name.strip().lower()}"

    async def get(self, source: str, drug_name: str) -> Optional[ReferenceData]:
        """Retrieves cached ReferenceData if present and unexpired."""
        cache_key = self.make_cache_key(source, drug_name)
        now = datetime.now(timezone.utc)

        async with self._lock:
            if self._session:
                return await self._get_with_session(self._session, cache_key, now)

            async with async_session_factory() as session:
                return await self._get_with_session(session, cache_key, now)

    async def _get_with_session(
        self, session: AsyncSession, cache_key: str, now: datetime
    ) -> Optional[ReferenceData]:
        stmt = select(ExternalReferenceCache).where(ExternalReferenceCache.key == cache_key)
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()

        if record is None:
            return None

        # Check expiration
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            logger.info("Cache entry expired for %s; purging", cache_key)
            await session.delete(record)
            await session.commit()
            return None

        try:
            return ReferenceData.model_validate_json(record.data_json)
        except Exception as exc:
            logger.warning("Failed to deserialize cached ReferenceData for %s: %s", cache_key, exc)
            return None

    async def set(
        self,
        source: str,
        drug_name: str,
        data: ReferenceData,
        ttl_days: int = 7,
    ) -> None:
        """Saves or updates cached ReferenceData with specified TTL."""
        cache_key = self.make_cache_key(source, drug_name)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=ttl_days)
        payload_json = data.model_dump_json()

        async with self._lock:
            if self._session:
                await self._set_with_session(self._session, cache_key, source, drug_name, payload_json, expires_at)
                return

            async with async_session_factory() as session:
                await self._set_with_session(session, cache_key, source, drug_name, payload_json, expires_at)
                await session.commit()

    async def _set_with_session(
        self,
        session: AsyncSession,
        cache_key: str,
        source: str,
        drug_name: str,
        payload_json: str,
        expires_at: datetime,
    ) -> None:
        stmt = select(ExternalReferenceCache).where(ExternalReferenceCache.key == cache_key)
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            record.data_json = payload_json
            record.expires_at = expires_at
        else:
            record = ExternalReferenceCache(
                key=cache_key,
                source=source.strip().lower(),
                drug_name=drug_name.strip(),
                data_json=payload_json,
                expires_at=expires_at,
            )
            session.add(record)

        await session.flush()

    async def invalidate(self, source: str, drug_name: str) -> bool:
        """Explicitly purges a cached entry."""
        cache_key = self.make_cache_key(source, drug_name)
        stmt = delete(ExternalReferenceCache).where(ExternalReferenceCache.key == cache_key)

        async with self._lock:
            if self._session:
                result = await self._session.execute(stmt)
                await self._session.commit()
                return result.rowcount > 0

            async with async_session_factory() as session:
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0

    async def cleanup_expired(self) -> int:
        """Purges all expired entries from cache table."""
        now = datetime.now(timezone.utc)
        stmt = delete(ExternalReferenceCache).where(ExternalReferenceCache.expires_at < now)

        async with self._lock:
            if self._session:
                result = await self._session.execute(stmt)
                await self._session.commit()
                return result.rowcount

            async with async_session_factory() as session:
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.rowcount

        async with async_session_factory() as session:
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
