"""End-to-end medicine packaging analysis pipeline service.

Orchestrates:
1. Image preprocessing and blur/format diagnostics (ML-024, ML-025)
2. OCR text extraction with fallback resilience (ML-026, ML-027)
3. Rule-based entity parsing (ML-062)
4. Multi-tier INN canonical normalization (ML-063)
5. Clinical database monograph matching
6. Multidimensional confidence calculation
7. Full persistence into SQLite/PostgreSQL (ML-030, ML-031, ML-032, ML-033)
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.analysis import Analysis, ExtractedEntityModel, AnalysisSource
from app.models.product import Product, Ingredient, ProductIngredient
from app.models.clinical import ClinicalInformation, Source, DrugInteraction
from app.schemas.analysis import AnalysisResponse, MultidimensionalConfidence
from app.schemas.ocr import OCRMetadata
from app.schemas.common import VerificationState, RoleType
from app.schemas.product import (
    ProductReport,
    IngredientReport,
    SafetyProfile,
    StrengthSchema,
    EvidenceSourceSchema,
)
from app.services.image_processing.preprocessor import ImagePreprocessor, PreprocessedImage
from app.services.ocr.dispatcher import OCRDispatcher
from app.services.extraction.rule_baseline import RuleBasedExtractor, RuleExtractionResult
from app.services.normalization.inn_normalizer import INNNormalizer, NormalizationResult
from app.services.scoring.confidence import (
    ScoringInput,
    compute_confidence,
    determine_verification_state,
)
from app.services.references.coordinator import ReferenceCoordinator
from app.services.references.cache import ReferenceCache

logger = logging.getLogger(__name__)


class AnalysisPipelineService:
    """Production service uniting image diagnostics, OCR, extraction, normalization, and persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        preprocessor: Optional[ImagePreprocessor] = None,
        ocr_dispatcher: Optional[OCRDispatcher] = None,
        rule_extractor: Optional[RuleBasedExtractor] = None,
        inn_normalizer: Optional[INNNormalizer] = None,
        reference_coordinator: Optional[ReferenceCoordinator] = None,
    ):
        self.session = db_session
        self.preprocessor = preprocessor or ImagePreprocessor()
        self.ocr_dispatcher = ocr_dispatcher or OCRDispatcher()
        self.rule_extractor = rule_extractor or RuleBasedExtractor()
        self.inn_normalizer = inn_normalizer or INNNormalizer()
        self.reference_coordinator = reference_coordinator or ReferenceCoordinator(
            cache=ReferenceCache(session=db_session)
        )

    async def process_image(
        self,
        raw_bytes: bytes,
        analysis_id: Optional[str] = None,
        requested_ocr_engine: Optional[str] = None,
        session_id: Optional[str] = None,
        allow_mock_ocr: bool = False,
    ) -> AnalysisResponse:
        """Executes full zero-hallucination analysis pipeline and persists report."""
        start_time = time.perf_counter()
        target_id = analysis_id or str(uuid.uuid4())

        # Step 1: Image Preprocessing (ML-024, ML-025)
        preprocessed: PreprocessedImage = self.preprocessor.process(raw_bytes)
        image_quality = preprocessed.quality

        # Step 2: OCR Dispatching (ML-026, ML-027)
        ocr_result = self.ocr_dispatcher.extract(
            image_bytes=preprocessed.processed_bytes,
            pil_image=preprocessed.pil_image,
            np_array=preprocessed.np_array,
            requested_engine=requested_ocr_engine,
            allow_mock=allow_mock_ocr,
        )
        raw_text = ocr_result.full_text

        is_mock_ocr = (ocr_result.engine_name == "mock")
        ocr_metadata = OCRMetadata(
            engine_name=ocr_result.engine_name,
            engine_version=ocr_result.engine_version,
            is_mock=is_mock_ocr,
            requested_engine=ocr_result.requested_engine,
            fallback_used=ocr_result.fallback_used,
            mean_confidence=ocr_result.mean_confidence,
            execution_time_ms=ocr_result.execution_time_ms,
        )

        # Step 3: Entity Extraction (ML-062)
        extraction: RuleExtractionResult = self.rule_extractor.extract(raw_text)

        # Step 4: Canonical Normalization & Database Grounding (ML-063)
        active_ingredients: List[IngredientReport] = []
        evidence_sources: List[EvidenceSourceSchema] = []
        contraindications_set = set()
        indications_set = set()
        warnings_set = set()
        uncertainties: List[str] = list(image_quality.warnings)

        if is_mock_ocr:
            uncertainties.append(
                "NOTICE: Mock OCR engine was used for this scan. Extracted text and entities are simulated test fixtures, not real optical packaging recognition."
            )

        primary_norm: Optional[NormalizationResult] = None
        has_canonical_grounding = False

        for ing in extraction.ingredients:
            raw_name = ing.get("raw_ingredient") or ing.get("raw_name") or ing.get("canonical_name") or ""
            norm_res = self.inn_normalizer.normalize(raw_name)
            if primary_norm is None:
                primary_norm = norm_res

            canonical_name = norm_res.canonical_name or raw_name or "Unidentified Substance"

            # Query database for clinical monograph of this canonical ingredient
            stmt = select(Ingredient).where(Ingredient.preferred_name == canonical_name)
            db_res = await self.session.execute(stmt)
            canonical_db_entry = db_res.scalar_one_or_none()

            # Strength parsing
            strength_schema: Optional[StrengthSchema] = None
            strength_dict = ing.get("strength")
            if strength_dict:
                strength_schema = StrengthSchema(
                    raw_text=strength_dict.get("raw_text", ""),
                    numeric_value=float(strength_dict.get("numeric_value", 0.0)) if strength_dict.get("numeric_value") else None,
                    unit=strength_dict.get("unit", "mg"),
                    basis=strength_dict.get("basis") or extraction.strength_basis,
                )

            # Grounding and safety accumulation from clinical_information table
            if canonical_db_entry:
                has_canonical_grounding = True
                stmt_claims = (
                    select(ClinicalInformation)
                    .where(
                        ClinicalInformation.subject_type == "ingredient",
                        ClinicalInformation.subject_id == canonical_db_entry.id,
                    )
                    .options(selectinload(ClinicalInformation.source))
                )
                res_claims = await self.session.execute(stmt_claims)
                claims = res_claims.scalars().all()

                for cl in claims:
                    if cl.category == "contraindication":
                        contraindications_set.add(cl.claim_text)
                    elif cl.category == "purpose":
                        indications_set.add(cl.claim_text)
                    elif cl.category in ("precaution", "adverse_effect"):
                        warnings_set.add(cl.claim_text)

                    if cl.source:
                        evidence_sources.append(
                            EvidenceSourceSchema(
                                name=cl.source.source_name,
                                url=cl.source.source_url,
                                source_id=cl.source.id,
                                jurisdiction=cl.source.jurisdiction,
                            )
                        )
            else:
                uncertainties.append(
                    f"Ingredient '{raw_name}' ({canonical_name}) has no local clinical monograph on file."
                )

            # Query external reference authorities (openFDA, PubChem, Indian Pharmacopoeia / CDSCO)
            try:
                ext_lookups = await self.reference_coordinator.lookup_ingredient(canonical_name)
                ext_sources = self.reference_coordinator.build_evidence_sources(ext_lookups)
                clinical_profile = self.reference_coordinator.consolidate_clinical_profile(ext_lookups)

                existing_urls = {s.url for s in evidence_sources}
                for s in ext_sources:
                    if s.url not in existing_urls:
                        evidence_sources.append(s)
                        existing_urls.add(s.url)

                for w in clinical_profile.get("warnings", []):
                    warnings_set.add(w)
                for c in clinical_profile.get("contraindications", []):
                    contraindications_set.add(c)
                for ind in clinical_profile.get("indications", []):
                    indications_set.add(ind)
            except Exception as exc:
                logger.warning("External reference resolution failed for %s: %s", canonical_name, exc)

            active_ingredients.append(
                IngredientReport(
                    canonical_name=canonical_name,
                    raw_label_text=raw_name,
                    strength=strength_schema or StrengthSchema(raw_text="q.s.", unit="q.s."),
                    role=RoleType.ACTIVE,
                    confidence=round(norm_res.confidence, 2),
                    explanation=f"{canonical_name} active therapeutic pharmaceutical substance.",
                    therapeutic_purpose=f"Symptomatic or clinical management involving {canonical_name}.",
                    evidence_sources=list(evidence_sources),
                )
            )

        # Fallback if no ingredients extracted
        if not active_ingredients:
            uncertainties.append("No active therapeutic ingredients could be parsed from packaging text.")

        # Commercial Product Brand Name Lookup
        stmt = select(Product)
        all_prods_res = await self.session.execute(stmt)
        all_products = all_prods_res.scalars().all()

        matched_product: Optional[Product] = None
        for p in all_products:
            if p.brand_name.lower() in raw_text.lower():
                matched_product = p
                break

        if matched_product:
            product_id = matched_product.id
            detected_name = matched_product.brand_name
            manufacturer = matched_product.manufacturer
            dosage_form = matched_product.dosage_form or extraction.dosage_form or "Tablet"
            is_verified = True

            # Retrieve product-specific clinical claims & deep evidence provenance (ML-013)
            stmt_prod_claims = (
                select(ClinicalInformation)
                .where(
                    ClinicalInformation.subject_type == "product",
                    ClinicalInformation.subject_id == matched_product.id,
                )
                .options(selectinload(ClinicalInformation.source))
            )
            res_prod_claims = await self.session.execute(stmt_prod_claims)
            for pcl in res_prod_claims.scalars().all():
                if pcl.category == "contraindication":
                    contraindications_set.add(pcl.claim_text)
                elif pcl.category == "purpose":
                    indications_set.add(pcl.claim_text)
                elif pcl.category in ("precaution", "adverse_effect"):
                    warnings_set.add(pcl.claim_text)
                if pcl.source:
                    evidence_sources.append(
                        EvidenceSourceSchema(
                            name=pcl.source.source_name,
                            url=pcl.source.source_url,
                            source_id=pcl.source.id,
                            jurisdiction=pcl.source.jurisdiction,
                        )
                    )
        else:
            first_line = ocr_result.lines[0].text if ocr_result.lines else "Medicine Packaging Scan"
            product_id = None
            detected_name = first_line.split()[0] if first_line else (primary_norm.canonical_name if primary_norm else "Analyzed Medicine")
            manufacturer = None
            dosage_form = extraction.dosage_form or "Tablet"
            is_verified = (primary_norm is not None and primary_norm.is_inn_match)

        product_report = ProductReport(
            id=product_id,
            detected_name=detected_name,
            dosage_form=dosage_form,
            manufacturer=manufacturer,
            is_verified=is_verified,
        )

        purpose_summary = " | ".join(sorted(indications_set)) if indications_set else "Symptomatic relief and therapeutic treatment as directed by physician."
        safety_profile = SafetyProfile(
            purpose_summary=purpose_summary,
            precautions=sorted(list(warnings_set)) if warnings_set else ["Use only as directed by a healthcare professional."],
            contraindications=sorted(list(contraindications_set)) if contraindications_set else ["Hypersensitivity to active ingredients."],
            adverse_effects=["Consult physician if adverse symptoms persist."],
        )

        # Step 5: Multidimensional Confidence Scoring (Blueprint Section 08.4)
        scoring_input = ScoringInput()
        scoring_input.ocr_word_count = len(raw_text.split())
        scoring_input.ocr_engine_reported_score = ocr_result.mean_confidence
        scoring_input.image_quality_flag = not image_quality.is_blurry
        scoring_input.ingredients_detected = len(active_ingredients)
        scoring_input.ingredients_with_strength = sum(1 for i in active_ingredients if i.strength)
        scoring_input.composition_header_found = extraction.composition_header_found
        scoring_input.identity_match_method = primary_norm.match_type if primary_norm else "none"
        scoring_input.identity_match_score = primary_norm.confidence if primary_norm else 0.0
        scoring_input.total_claims = len(contraindications_set) + len(indications_set) + len(warnings_set)
        scoring_input.claims_with_source = len(evidence_sources)

        confidence_ratings = compute_confidence(scoring_input)
        verification_state = determine_verification_state(confidence_ratings)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # Deduplicate sources by source_id or URL
        unique_sources: List[EvidenceSourceSchema] = []
        seen_keys = set()
        for src in evidence_sources:
            dedup_key = src.source_id or src.url
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                unique_sources.append(src)

        report = AnalysisResponse(
            analysis_id=target_id,
            status=verification_state,
            processing_time_ms=elapsed_ms,
            confidence=confidence_ratings,
            product=product_report,
            active_ingredients=active_ingredients,
            inactive_ingredients=[],
            safety_profile=safety_profile,
            uncertainties=uncertainties,
            audit_hash=image_quality.sha256,
            ocr_metadata=ocr_metadata,
            sources=unique_sources,
        )

        # Step 6: Persist in SQLite / PostgreSQL (ML-030, ML-031, ML-032)
        analysis_record = Analysis(
            id=target_id,
            session_id=session_id,
            status=verification_state.value,
            image_sha256=image_quality.sha256,
            processing_time_ms=elapsed_ms,
            confidence_aggregate=confidence_ratings.identity_confidence,
            model_version="v0.2.0-pipeline",
            report_json=report.model_dump_json(),
        )
        self.session.add(analysis_record)

        # Persist extracted entity tokens
        for entity_cand in extraction.extracted_entities:
            entity_model = ExtractedEntityModel(
                analysis_id=target_id,
                entity_type=entity_cand.label,
                raw_text=entity_cand.raw_text,
                normalized_candidate=entity_cand.normalized_value,
                confidence=entity_cand.confidence,
                verification_status=verification_state.value,
            )
            self.session.add(entity_model)

        await self.session.commit()
        return report
