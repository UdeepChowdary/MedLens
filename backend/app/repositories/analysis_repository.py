"""Repository handling Analysis job and Extracted Entity persistence."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import Analysis, ExtractedEntityModel


class AnalysisRepository:
    """Encapsulates data operations for ephemeral scan analyses and token audits."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, analysis: Analysis) -> Analysis:
        """Persists new analysis record."""
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        """Fetches analysis with its extracted entities and sources."""
        stmt = (
            select(Analysis)
            .where(Analysis.id == analysis_id)
            .options(
                selectinload(Analysis.entities),
                selectinload(Analysis.sources),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_entities(self, entities: List[ExtractedEntityModel]) -> None:
        """Batch saves extracted OCR and ML tokens."""
        self.session.add_all(entities)
        await self.session.commit()
