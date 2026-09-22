"""
Deterministic Verification engine.

Decides whether a Finding is promoted to "confirmed" or stays
"potential" — based on evidence quality signals, NEVER on the raw LLM
confidence score alone. This is the project's core evidence-driven
principle made concrete and inspectable.

The rules here are intentionally simple and explainable (a 7th-semester
viva should be able to walk through exactly why a finding was or
wasn't confirmed) rather than a black-box score.
"""
from dataclasses import dataclass

from app.services.code_analysis.normalizer import map_confidence


@dataclass
class VerificationResult:
    verified: bool
    confidence: float
    verification_method: str
    reason: str


# A finding is only eligible for "confirmed" when ALL of these hold:
MIN_ANALYZER_CONFIDENCE = 0.6   # Semgrep/Bandit's own reported confidence, mapped to 0-1
MIN_RAG_MATCHES = 1              # at least one relevant security-knowledge chunk was retrieved
MIN_LLM_CONFIDENCE = 0.6         # the LLM's own self-reported confidence (only used as one input, not the decider)
REQUIRE_LLM_SUCCESS = True       # the LLM call must not have fallen back to the generic error path


def verify_static_finding(
    *,
    raw_analyzer_confidence: str | None,
    rag_chunk_count: int,
    llm_confidence: float,
    llm_call_succeeded: bool,
    has_source_location: bool,
) -> VerificationResult:
    """
    Verifies a source-code (static) finding.

    Combines: (1) the deterministic analyzer's own confidence rating,
    (2) whether real security knowledge was actually retrieved for it
    (vs. the LLM reasoning from nothing), (3) whether the LLM call
    itself succeeded, and (4) whether a real source location exists —
    per the project's "file + line number strongly preferred" rule.
    """
    analyzer_confidence = map_confidence(raw_analyzer_confidence)
    reasons: list[str] = []
    failed_criteria: list[str] = []

    if analyzer_confidence < MIN_ANALYZER_CONFIDENCE:
        failed_criteria.append(f"analyzer confidence {analyzer_confidence:.2f} < {MIN_ANALYZER_CONFIDENCE}")
    else:
        reasons.append(f"analyzer reported confidence {analyzer_confidence:.2f}")

    if rag_chunk_count < MIN_RAG_MATCHES:
        failed_criteria.append("no relevant security knowledge retrieved")
    else:
        reasons.append(f"{rag_chunk_count} relevant security-knowledge chunk(s) retrieved")

    if REQUIRE_LLM_SUCCESS and not llm_call_succeeded:
        failed_criteria.append("LLM explanation failed (fallback used)")
    elif llm_confidence < MIN_LLM_CONFIDENCE:
        failed_criteria.append(f"LLM self-reported confidence {llm_confidence:.2f} < {MIN_LLM_CONFIDENCE}")
    else:
        reasons.append(f"LLM self-reported confidence {llm_confidence:.2f}")

    if not has_source_location:
        failed_criteria.append("no reliable source location (file/line) available")
    else:
        reasons.append("source location available")

    verified = len(failed_criteria) == 0

    # Blended confidence: weighted toward the deterministic analyzer
    # signal, not the LLM's self-assessment, per the project's
    # "do not use LLM confidence alone" principle.
    blended_confidence = round((analyzer_confidence * 0.6) + (llm_confidence * 0.4), 2)

    if verified:
        reason = "Verified: " + "; ".join(reasons) + "."
    else:
        reason = "Not verified — " + "; ".join(failed_criteria) + "."

    return VerificationResult(
        verified=verified,
        confidence=blended_confidence,
        verification_method="static_evidence",
        reason=reason,
    )


# Dynamic checks report their own confidence directly (HIGH/MEDIUM/LOW,
# already reflecting how strong a heuristic each check is — e.g. missing
# headers is deterministic/HIGH, IDOR comparison is a heuristic/LOW).
MIN_DYNAMIC_CONFIDENCE = 0.6


def verify_dynamic_finding(
    *,
    raw_check_confidence: str | None,
    rag_chunk_count: int,
    llm_confidence: float,
    llm_call_succeeded: bool,
    has_endpoint_location: bool,
) -> VerificationResult:
    """
    Verifies a dynamic (web) finding. Mirrors verify_static_finding's
    structure but uses the dynamic check's own reported confidence
    (from dynamic_checks.py) instead of Semgrep/Bandit's.
    """
    check_confidence = map_confidence(raw_check_confidence)
    reasons: list[str] = []
    failed_criteria: list[str] = []

    if check_confidence < MIN_DYNAMIC_CONFIDENCE:
        failed_criteria.append(f"check confidence {check_confidence:.2f} < {MIN_DYNAMIC_CONFIDENCE}")
    else:
        reasons.append(f"dynamic check reported confidence {check_confidence:.2f}")

    if rag_chunk_count < MIN_RAG_MATCHES:
        failed_criteria.append("no relevant security knowledge retrieved")
    else:
        reasons.append(f"{rag_chunk_count} relevant security-knowledge chunk(s) retrieved")

    if REQUIRE_LLM_SUCCESS and not llm_call_succeeded:
        failed_criteria.append("LLM explanation failed (fallback used)")
    elif llm_confidence < MIN_LLM_CONFIDENCE:
        failed_criteria.append(f"LLM self-reported confidence {llm_confidence:.2f} < {MIN_LLM_CONFIDENCE}")
    else:
        reasons.append(f"LLM self-reported confidence {llm_confidence:.2f}")

    if not has_endpoint_location:
        failed_criteria.append("no endpoint/URL location available")
    else:
        reasons.append("endpoint location available")

    verified = len(failed_criteria) == 0
    blended_confidence = round((check_confidence * 0.6) + (llm_confidence * 0.4), 2)

    if verified:
        reason = "Verified: " + "; ".join(reasons) + "."
    else:
        reason = "Not verified — " + "; ".join(failed_criteria) + "."

    return VerificationResult(
        verified=verified,
        confidence=blended_confidence,
        verification_method="dynamic_evidence",
        reason=reason,
    )
