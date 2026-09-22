"""
The Security Agent — CodeShieldAI's single reasoning orchestrator.

Per the project's design: ONE agent, not a multi-agent swarm. It wires
together the deterministic tools (Semgrep/Bandit via Observations),
RAG retrieval, LLM explanation, and the deterministic Verifier into
the explicit flow:

    observe -> prioritize -> generate_hypothesis -> select_controlled_test
    -> execute_test -> collect_evidence -> verify -> create_finding

For SOURCE CODE, "select_controlled_test" / "execute_test" are honest
no-ops: there is no live application to test against, so the agent
reviews static evidence rather than executing a test. The hooks exist
here so Phase 5's dynamic checks (Playwright/HTTPX, against an
authorized live target) can plug into the same flow without changing
this architecture — see execute_test()'s docstring.
"""
import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.finding import Finding, FindingStatus
from app.models.observation import Observation
from app.services.code_analysis.normalizer import map_confidence, map_severity
from app.services.llm.security_explainer import explain_observation
from app.services.rag.retriever import retrieve_context
from app.services.security_agent.verifier import verify_dynamic_finding, verify_static_finding

logger = logging.getLogger(__name__)

# How many prioritized observations get a full LLM+verification pass per
# scan, to bound scan duration / API usage on large codebases.
MAX_OBSERVATIONS_PER_SCAN = 25

_SEVERITY_RANK = {"ERROR": 3, "HIGH": 3, "WARNING": 2, "MEDIUM": 2, "INFO": 1, "LOW": 1}


@dataclass
class AgentResult:
    finding: Finding
    hypothesis: str
    test_performed: bool
    verified: bool


class SecurityAgent:
    def __init__(self, db: Session):
        self.db = db

    # --- observe -------------------------------------------------------
    def observe(self, observations: list[Observation]) -> list[Observation]:
        """Pass-through, named explicitly to make the reasoning flow
        traceable — this is the agent's input: raw tool signals."""
        return observations

    # --- prioritize ------------------------------------------------------
    def prioritize(self, observations: list[Observation]) -> list[Observation]:
        """Highest tool-reported severity first, so a large codebase's
        most concerning signals get the LLM+verification pass, not
        just the first N observations Semgrep/Bandit happened to emit."""
        ranked = sorted(
            observations,
            key=lambda o: _SEVERITY_RANK.get((o.raw_severity or "").upper(), 0),
            reverse=True,
        )
        return ranked[:MAX_OBSERVATIONS_PER_SCAN]

    # --- generate_hypothesis --------------------------------------------
    def generate_hypothesis(self, observation: Observation) -> str:
        """A plain-language hypothesis derived directly from the tool
        observation — NOT from the LLM. This is what gets verified."""
        if observation.source == "dynamic":
            location = f"{observation.http_method or 'GET'} {observation.endpoint or 'unknown endpoint'}"
            if observation.parameter:
                location += f" (parameter: {observation.parameter})"
        else:
            location = observation.file or "unknown file"
            if observation.line:
                location += f":{observation.line}"

        return (
            f"{observation.source} rule '{observation.rule_id or 'unknown'}' suggests a potential "
            f"{observation.message.strip().rstrip('.')} at {location}."
        )

    # --- select_controlled_test / execute_test --------------------------
    def select_controlled_test(self, observation: Observation) -> str:
        """Static observations get a structured evidence review (no
        live target to test). Dynamic observations already ran their
        controlled test in services/web_analysis/dynamic_checks.py —
        this just names which one, for the reasoning timeline."""
        if observation.source == "dynamic":
            return observation.rule_id or "dynamic_check"
        return "static_evidence_review"

    def execute_test(self, observation: Observation, test_name: str) -> dict[str, Any]:
        """For dynamic observations, the controlled test has ALREADY
        run (by dynamic_checks.py, before the observation was ever
        created) — this reports that honestly rather than re-running
        it. For static observations, there is no live target, so no
        test is performed — the agent reviews static evidence instead."""
        if observation.source == "dynamic":
            return {"performed": True, "test_name": test_name, "reason": "controlled dynamic check already executed"}
        return {"performed": False, "test_name": test_name, "reason": "static analysis only — no live target to test"}

    # --- collect_evidence -------------------------------------------------
    def collect_evidence(self, observation: Observation, rag_chunks: list[dict[str, Any]]) -> list[Evidence]:
        """Builds Evidence rows (not yet persisted — caller commits)."""
        if observation.source == "dynamic":
            primary_evidence = Evidence(
                evidence_type="dynamic_analysis",
                source="dynamic_check",
                content=(
                    f"Test: {observation.rule_id or 'n/a'}\n"
                    f"Method: {observation.http_method or 'GET'}\n"
                    f"URL: {observation.endpoint or 'unknown'}\n"
                    f"Parameter: {observation.parameter or 'n/a'}\n"
                    f"Observed behavior: {observation.message}\n"
                    f"Response context:\n{observation.code_snippet or '(not captured)'}"
                ),
            )
        else:
            primary_evidence = Evidence(
                evidence_type="static_analysis",
                source=observation.source,
                content=(
                    f"Rule: {observation.rule_id or 'n/a'}\n"
                    f"Message: {observation.message}\n"
                    f"Location: {observation.file or 'unknown'}"
                    f"{f':{observation.start_line}-{observation.end_line}' if observation.start_line else ''}\n"
                    f"Code:\n{observation.code_snippet or '(not available)'}"
                ),
            )
        evidence = [primary_evidence]
        for chunk in rag_chunks:
            evidence.append(
                Evidence(
                    evidence_type="security_knowledge",
                    source=chunk.get("title"),
                    content=(f"{chunk.get('cwe') or ''} {chunk.get('owasp') or ''}\n\n{chunk.get('text')}").strip(),
                )
            )
        return evidence

    # --- verify -------------------------------------------------------
    def verify(self, observation: Observation, rag_chunks: list[dict[str, Any]], llm_result: dict[str, Any]):
        llm_succeeded = "error" not in llm_result and "reasoning" in llm_result and "Fallback" not in (
            llm_result.get("reasoning") or ""
        )
        try:
            llm_confidence = float(llm_result.get("confidence", 0.0))
        except (TypeError, ValueError):
            llm_confidence = 0.0

        if observation.source == "dynamic":
            return verify_dynamic_finding(
                raw_check_confidence=observation.raw_confidence,
                rag_chunk_count=len(rag_chunks),
                llm_confidence=llm_confidence,
                llm_call_succeeded=llm_succeeded,
                has_endpoint_location=bool(observation.endpoint),
            )

        return verify_static_finding(
            raw_analyzer_confidence=observation.raw_confidence,
            rag_chunk_count=len(rag_chunks),
            llm_confidence=llm_confidence,
            llm_call_succeeded=llm_succeeded,
            has_source_location=bool(observation.file and observation.line),
        )

    # --- reasoning timeline (for the "AI Security Reasoning" UI section) ---
    def build_reasoning_steps(
        self,
        observation: Observation,
        hypothesis: str,
        test_result: dict[str, Any],
        llm_result: dict[str, Any],
        verification,
    ) -> str:
        import json

        steps = [
            {"label": "Observation", "text": observation.message},
            {"label": "Hypothesis", "text": hypothesis},
            {"label": "Test", "text": test_result.get("reason", "")},
            {
                "label": "Evidence",
                "text": (
                    f"{observation.source} evidence collected"
                    + (f" from {observation.file}" if observation.file else "")
                    + (f" against {observation.endpoint}" if observation.endpoint else "")
                ),
            },
            {"label": "Verification", "text": verification.reason},
            {"label": "Conclusion", "text": llm_result.get("reasoning") or llm_result.get("description") or ""},
        ]
        return json.dumps(steps)

    # --- create_finding -------------------------------------------------
    def create_finding(
        self,
        observation: Observation,
        llm_result: dict[str, Any],
        verification,
        evidence: list[Evidence],
        language: str | None,
        hypothesis: str = "",
        test_result: dict[str, Any] | None = None,
    ) -> Finding:
        valid_severities = {"informational", "low", "medium", "high", "critical"}
        llm_severity = (llm_result.get("severity") or "").lower()
        severity = llm_severity if llm_severity in valid_severities else map_severity(observation.raw_severity)

        is_dynamic = observation.source == "dynamic"

        finding = Finding(
            scan_id=observation.scan_id,
            title=(llm_result.get("title") or f"{observation.source} finding: {observation.rule_id}")[:255],
            category=(llm_result.get("category") or "Uncategorized")[:100],
            severity=severity,
            confidence=verification.confidence,
            description=llm_result.get("description"),
            # Static location (null for dynamic findings — never fabricated)
            file=None if is_dynamic else observation.file,
            line=None if is_dynamic else (observation.start_line or observation.line),
            start_line=None if is_dynamic else (observation.start_line or observation.line),
            end_line=None if is_dynamic else observation.end_line,
            start_column=None if is_dynamic else observation.start_column,
            end_column=None if is_dynamic else observation.end_column,
            code_snippet=observation.code_snippet,
            # Dynamic location (null for static findings)
            endpoint=observation.endpoint if is_dynamic else None,
            http_method=observation.http_method if is_dynamic else None,
            parameter=observation.parameter if is_dynamic else None,
            analyzer=observation.source,
            rule_id=observation.rule_id,
            impact=llm_result.get("impact"),
            recommendation=llm_result.get("remediation"),
            cwe_id=llm_result.get("cwe_id"),
            owasp_category=llm_result.get("owasp_category"),
            verified=verification.verified,
            verification_method=verification.verification_method,
            verification_reason=verification.reason,
            reasoning_steps=self.build_reasoning_steps(
                observation, hypothesis, test_result or {}, llm_result, verification
            ),
            status=FindingStatus.CONFIRMED if verification.verified else FindingStatus.POTENTIAL,
        )
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)

        for ev in evidence:
            ev.finding_id = finding.id
            self.db.add(ev)
        self.db.commit()

        return finding

    # --- full flow for one observation -------------------------------
    def run_for_observation(self, observation: Observation, language: str | None) -> AgentResult:
        hypothesis = self.generate_hypothesis(observation)
        test_name = self.select_controlled_test(observation)
        test_result = self.execute_test(observation, test_name)

        rag_chunks = retrieve_context(observation.rule_id, observation.message, language=language, top_k=3)

        llm_result = explain_observation(
            source=observation.source,
            rule_id=observation.rule_id,
            message=observation.message,
            file=observation.file,
            line=observation.start_line or observation.line,
            endpoint=observation.endpoint,
            http_method=observation.http_method,
            parameter=observation.parameter,
            code_snippet=observation.code_snippet,
            raw_severity=observation.raw_severity,
            language=language,
            rag_context=rag_chunks,
        )

        verification = self.verify(observation, rag_chunks, llm_result)
        evidence = self.collect_evidence(observation, rag_chunks)
        finding = self.create_finding(
            observation, llm_result, verification, evidence, language,
            hypothesis=hypothesis, test_result=test_result,
        )

        observation.processed = True
        self.db.commit()

        return AgentResult(
            finding=finding,
            hypothesis=hypothesis,
            test_performed=test_result["performed"],
            verified=verification.verified,
        )
