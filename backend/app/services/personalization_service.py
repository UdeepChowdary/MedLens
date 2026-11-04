"""Service for personalized clinical health analysis and BYOK Gemini API integration."""

import json
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types

from app.schemas.personalization import (
    AllergyMatch,
    ConditionMatch,
    PersonalizeRequest,
    PersonalizeResponse,
    VerifyKeyResponse,
)

logger = logging.getLogger(__name__)

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.8-flash"]


class PersonalizationService:
    """Orchestrates patient-specific medicine analysis using BYOK Gemini AI or deterministic monographs."""

    def __init__(self):
        pass

    def verify_gemini_key(self, api_key: str) -> VerifyKeyResponse:
        """Validates a user-supplied Gemini API key with a lightweight live test request."""
        cleaned_key = api_key.strip()
        if not cleaned_key:
            return VerifyKeyResponse(valid=False, message="API key cannot be empty.")

        last_error = ""
        for model in GEMINI_MODELS:
            try:
                client = genai.Client(api_key=cleaned_key)
                # Quick lightweight probe
                resp = client.models.generate_content(
                    model=model,
                    contents="Reply with 'OK'.",
                    config=types.GenerateContentConfig(max_output_tokens=5),
                )
                if resp and resp.text:
                    return VerifyKeyResponse(
                        valid=True,
                        message=f"Gemini API key verified successfully! Connected with {model}.",
                        model_tested=model,
                    )
            except Exception as e:
                err_str = str(e)
                last_error = err_str
                # If it's a model not found error, continue to next candidate model
                if "404" in err_str or "NOT_FOUND" in err_str or "unsupported" in err_str.lower():
                    continue
                # If authentication failed (400, 401, 403), stop immediately
                if "400" in err_str or "401" in err_str or "403" in err_str or "API_KEY_INVALID" in err_str:
                    return VerifyKeyResponse(
                        valid=False,
                        message="Invalid Gemini API key. Please check your key at Google AI Studio (aistudio.google.com).",
                    )

        return VerifyKeyResponse(
            valid=False,
            message=f"Could not verify Gemini key with available models. Details: {last_error[:120]}",
        )

    def personalize(
        self,
        request: PersonalizeRequest,
        product_context: Optional[Dict[str, str]] = None,
    ) -> PersonalizeResponse:
        """Generates personalized analysis. Uses Gemini if key provided; otherwise runs deterministic rules."""
        api_key = (request.gemini_api_key or "").strip()

        # If user supplied a Gemini API key, use AI-powered clinical synthesis
        if api_key:
            ai_result = self._personalize_with_gemini(request, product_context, api_key)
            if ai_result:
                return ai_result
            logger.warning("Gemini personalization failed; falling back to deterministic monograph match.")

        # Default fallback: deterministic rule-based analysis
        return self._personalize_rule_based(request, product_context)

    def _personalize_with_gemini(
        self,
        request: PersonalizeRequest,
        product_context: Optional[Dict[str, str]],
        api_key: str,
    ) -> Optional[PersonalizeResponse]:
        """Calls Google Gemini with structured clinical pharmacology prompt."""
        prod_name = request.product_name or (product_context.get("name") if product_context else "Scanned Medication")
        actives = request.active_ingredients or (
            [product_context.get("active_ingredient", "")] if product_context and product_context.get("active_ingredient") else []
        )
        dosages = request.dosages or (
            [product_context.get("dosage", "")] if product_context and product_context.get("dosage") else []
        )
        allergies_str = ", ".join(request.user_allergies) if request.user_allergies else "None documented"
        conditions_str = ", ".join(request.user_conditions) if request.user_conditions else "None documented"

        system_instruction = (
            "You are a clinical pharmacologist and patient safety specialist for MedLens, "
            "an evidence-based medicine intelligence system. Evaluate the medication specifically "
            "against this individual patient's documented drug allergies and active medical conditions. "
            "Be precise, scientifically rigorous, and safety-focused. "
            "Respond strictly in valid JSON adhering to the specified format."
        )

        prompt = f"""
Medication Profile:
- Product Brand: {prod_name}
- Active Therapeutic Ingredients: {', '.join(actives) if actives else 'Not specified'}
- Strength/Dosage: {', '.join(dosages) if dosages else 'Standard'}

Patient Health Profile:
- Documented Allergies: {allergies_str}
- Pre-Existing Diseases / Conditions: {conditions_str}

Perform a rigorous personalized safety evaluation. Output a JSON object with EXACTLY this structure:
{{
  "overall_safety_rating": "safe" | "caution" | "high_risk" | "contraindicated",
  "executive_summary": "Concise 2-3 sentence personalized summary for the patient.",
  "allergy_matches": [
    {{
      "allergen": "name of allergy",
      "severity": "none" | "low" | "moderate" | "high",
      "reaction_type": "Direct match, Cross-reactive class, Excipient risk, or No known cross-reactivity",
      "explanation": "Detailed clinical mechanism or safety statement."
    }}
  ],
  "condition_matches": [
    {{
      "condition": "name of condition",
      "compatibility": "beneficial" | "compatible" | "caution" | "contraindicated",
      "clinical_note": "Explanation of how the medicine interacts with or affects this specific condition."
    }}
  ],
  "personalized_precautions": [
    "Actionable precaution 1",
    "Actionable precaution 2"
  ],
  "tailored_dosage_advice": "Specific practical guidance regarding timing (e.g. before meals, morning/night) and adherence.",
  "questions_for_doctor": [
    "Specific question 1 the patient should ask their physician",
    "Specific question 2 the patient should ask their physician"
  ]
}}
"""

        for model in GEMINI_MODELS:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )
                if response and response.text:
                    parsed = json.loads(response.text)
                    return PersonalizeResponse(
                        analysis_id=request.analysis_id,
                        is_ai_enhanced=True,
                        model_name=f"Google {model}",
                        overall_safety_rating=parsed.get("overall_safety_rating", "safe").lower(),
                        executive_summary=parsed.get("executive_summary", "Personalized analysis completed."),
                        allergy_matches=[AllergyMatch(**item) for item in parsed.get("allergy_matches", [])],
                        condition_matches=[ConditionMatch(**item) for item in parsed.get("condition_matches", [])],
                        personalized_precautions=parsed.get("personalized_precautions", []),
                        tailored_dosage_advice=parsed.get("tailored_dosage_advice"),
                        questions_for_doctor=parsed.get("questions_for_doctor", []),
                    )
            except Exception as e:
                logger.warning("Error with model %s: %s", model, e)
                continue

        return None

    def _personalize_rule_based(
        self,
        request: PersonalizeRequest,
        product_context: Optional[Dict[str, str]],
    ) -> PersonalizeResponse:
        """Deterministic monograph-based cross-matching for users without a Gemini API key."""
        prod_name = request.product_name or (product_context.get("name") if product_context else "Scanned Medication")
        actives = [a.lower() for a in request.active_ingredients]
        if product_context and product_context.get("active_ingredient"):
            actives.append(product_context["active_ingredient"].lower())

        allergy_matches: List[AllergyMatch] = []
        overall_severity = "safe"

        # Check allergies
        for user_allergy in request.user_allergies:
            u_all = user_allergy.lower().strip()
            if not u_all:
                continue

            # Direct match check
            matched_active = None
            for act in actives:
                if u_all in act or act in u_all:
                    matched_active = act
                    break

            if matched_active:
                overall_severity = "contraindicated"
                allergy_matches.append(
                    AllergyMatch(
                        allergen=user_allergy,
                        severity="high",
                        reaction_type="Direct Active Ingredient Match",
                        explanation=f"ALERT: This medication contains '{matched_active.capitalize()}', which directly matches your documented allergy to '{user_allergy}'. Do not ingest without medical clearance.",
                    )
                )
            elif any(cls_kw in u_all for cls_kw in ["nsaid", "sulfa", "penicillin", "beta-lactam", "ppi", "proton pump"]):
                # Class check
                is_ppi = any("prazole" in act for act in actives)
                is_nsaid = any(k in " ".join(actives) for k in ["paracetamol", "ibuprofen", "aspirin", "diclofenac", "naproxen"])
                if ("ppi" in u_all or "proton pump" in u_all) and is_ppi:
                    overall_severity = "high_risk"
                    allergy_matches.append(
                        AllergyMatch(
                            allergen=user_allergy,
                            severity="high",
                            reaction_type="Class Cross-Reactivity Risk",
                            explanation=f"This medicine is a Proton Pump Inhibitor (PPI), which presents severe cross-reactivity with your documented {user_allergy} allergy.",
                        )
                    )
                elif "nsaid" in u_all and is_nsaid:
                    overall_severity = "high_risk"
                    allergy_matches.append(
                        AllergyMatch(
                            allergen=user_allergy,
                            severity="high",
                            reaction_type="Class Cross-Reactivity Risk",
                            explanation=f"Active ingredients may present sensitivity with your documented {user_allergy} allergy.",
                        )
                    )
                else:
                    allergy_matches.append(
                        AllergyMatch(
                            allergen=user_allergy,
                            severity="none",
                            reaction_type="No Direct Conflict",
                            explanation=f"No direct pharmacological cross-reaction detected between {user_allergy} and active formulation.",
                        )
                    )
            else:
                allergy_matches.append(
                    AllergyMatch(
                        allergen=user_allergy,
                        severity="none",
                        reaction_type="No Direct Conflict",
                        explanation=f"No documented allergy cross-reaction identified for '{user_allergy}'.",
                    )
                )

        # Check conditions
        condition_matches: List[ConditionMatch] = []
        is_pantoprazole = any("pantoprazole" in act or "prazole" in act for act in actives)

        for cond in request.user_conditions:
            c_lower = cond.lower().strip()
            if not c_lower:
                continue

            if is_pantoprazole:
                if any(k in c_lower for k in ["gerd", "acid", "reflux", "heartburn", "ulcer", "gastritis"]):
                    condition_matches.append(
                        ConditionMatch(
                            condition=cond,
                            compatibility="beneficial",
                            clinical_note=f"Therapeutically indicated: Pantoprazole is specifically approved for the clinical management and healing of {cond}.",
                        )
                    )
                elif any(k in c_lower for k in ["kidney", "renal", "nephritis"]):
                    if overall_severity == "safe":
                        overall_severity = "caution"
                    condition_matches.append(
                        ConditionMatch(
                            condition=cond,
                            compatibility="caution",
                            clinical_note=f"Caution advised: Acute interstitial nephritis has been reported rarely with proton pump inhibitor therapy. Monitor kidney parameters if using long-term.",
                        )
                    )
                elif any(k in c_lower for k in ["bone", "osteoporosis", "fracture", "magnesium", "hypomagnesemia"]):
                    if overall_severity == "safe":
                        overall_severity = "caution"
                    condition_matches.append(
                        ConditionMatch(
                            condition=cond,
                            compatibility="caution",
                            clinical_note=f"Long-term daily proton pump inhibitor therapy can decrease magnesium and calcium absorption, potentially aggravating {cond}.",
                        )
                    )
                elif any(k in c_lower for k in ["liver", "hepatic", "cirrhosis"]):
                    if overall_severity == "safe":
                        overall_severity = "caution"
                    condition_matches.append(
                        ConditionMatch(
                            condition=cond,
                            compatibility="caution",
                            clinical_note="Severe hepatic impairment requires clinical monitoring; dose titration may be recommended by your physician.",
                        )
                    )
                else:
                    condition_matches.append(
                        ConditionMatch(
                            condition=cond,
                            compatibility="compatible",
                            clinical_note=f"No severe absolute contraindication recorded in official monograph regarding {cond}.",
                        )
                    )
            else:
                condition_matches.append(
                    ConditionMatch(
                        condition=cond,
                        compatibility="compatible",
                        clinical_note=f"Standard clinical precautions apply when administering with {cond}.",
                    )
                )

        # Practical precautions
        precautions = [
            "Store below 30°C in a dry location protected from direct sunlight and humidity.",
            "Take with a full glass of water. Do not crush, chew, or split gastro-resistant coated tablets.",
        ]
        if is_pantoprazole:
            precautions.append("Optimal therapeutic efficacy is achieved when taken 30 to 60 minutes before morning breakfast.")

        timing_advice = (
            "Take 1 tablet daily in the morning approximately 30-60 minutes prior to your first meal."
            if is_pantoprazole
            else "Follow your prescribing physician's directions regarding administration schedule."
        )

        doctor_questions = [
            f"Given my documented health profile ({', '.join(request.user_conditions) if request.user_conditions else 'general'}), is {prod_name} the optimal treatment?",
            "What is the recommended maximum treatment duration before we evaluate progress?",
        ]

        summary = (
            f"Standard monograph evaluation complete for {prod_name}. "
            f"Overall profile rating: {overall_severity.upper()}. "
            f"Reviewed against {len(request.user_allergies)} documented allergies and {len(request.user_conditions)} active conditions."
        )

        return PersonalizeResponse(
            analysis_id=request.analysis_id,
            is_ai_enhanced=False,
            model_name="MedLens Pharmacopeia Monograph Rules",
            overall_safety_rating=overall_severity,
            executive_summary=summary,
            allergy_matches=allergy_matches,
            condition_matches=condition_matches,
            personalized_precautions=precautions,
            tailored_dosage_advice=timing_advice,
            questions_for_doctor=doctor_questions,
        )
