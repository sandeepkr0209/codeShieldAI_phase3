# CodeShieldAI

**Phase 1 — Foundation**

CodeShieldAI is an evidence-driven, AI-assisted security analysis platform. It combines
deterministic static/dynamic analysis tools with LLM reasoning (via Groq) and, in later
phases, Retrieval-Augmented Generation over security knowledge (OWASP, CWE, CAPEC) to
produce vulnerability findings that are backed by real evidence rather than LLM guesswork.

This is a 7th-semester B.Tech AIML minor project, built incrementally, phase by phase.

> **This is Phase 1 only.** It contains the full-stack foundation — project/scan/finding
> data model, REST API, a modern dashboard UI, and a working Groq LLM integration test.
> **It does not yet contain any actual code or web analysis engine.** Semgrep, Bandit,
> Tree-sitter, Playwright, RAG, and the Security Agent are implemented in later phases
> (see [Current Phase](#current-phase--future-phases) below).

---

## What CodeShieldAI is

A platform that will eventually:
- Ingest source code (ZIP / GitHub) or an authorized web application URL
- Run deterministic static/dynamic analysis (Semgrep, Bandit, Tree-sitter, Playwright, HTTPX)
- Retrieve relevant security knowledge via RAG (OWASP / CWE / CAPEC)
- Use an LLM (via Groq) to reason over evidence, generate hypotheses, and explain findings
- Verify findings against actual evidence before reporting them
- Present findings with severity, confidence, evidence, CWE/OWASP mapping, and remediation
- Generate a structured security report

The core principle: **Observation → Hypothesis → Controlled Test → Evidence → Verification
→ Finding → Explanation → Remediation.** The LLM reasons over evidence; it is never treated
as a standalone vulnerability oracle.

## Architecture

```
React + TypeScript (Vite, Tailwind)
        │  REST (fetch via a centralized API client)
        ▼
FastAPI Backend
    ├── API layer (routes)
    ├── Service layer (projects, scans, findings)
    ├── LLMProvider abstraction → GroqProvider
    └── SQLAlchemy → PostgreSQL
```

Phase 1 deliberately does NOT include: Semgrep/Bandit/Tree-sitter integration, Playwright/HTTPX
crawling, RAG ingestion or vector search, the Security Agent, or any vulnerability testing.
Those are Phase 2 through Phase 6. See the project's master context document for the full
phase breakdown.

## Technology Stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, Lucide icons

**Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Groq SDK

**Testing:** pytest (backend), Vitest + React Testing Library (frontend)

## Folder Structure

```
codeshieldai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config, logging
│   │   ├── api/routes/      # health, projects, scans, findings, reports, ai
│   │   ├── db/               # SQLAlchemy engine/session
│   │   ├── models/          # Project, Scan, Finding, Evidence, Report
│   │   ├── schemas/         # Pydantic request/response models
│   │   └── services/        # projects, scans, findings, llm (GroqProvider)
│   ├── alembic/              # migrations (initial schema included)
│   ├── tests/                # pytest suite
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/            # Dashboard, Projects, ProjectDetail, Scans, ScanDetails,
    │   │                     # Findings, FindingDetail, Reports, KnowledgeBase, Settings
    │   ├── layouts/          # Sidebar, Topbar, AppLayout
    │   ├── components/       # SeverityBadge, StatusBadge, StatCard, EmptyState, etc.
    │   ├── services/api.ts   # centralized API client
    │   └── types/
    ├── package.json
    └── .env.example
```

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- PostgreSQL 14+ running locally
- A Groq API key from https://console.groq.com (optional for everything except the
  `/api/ai/test` endpoint and the Settings page's "Test connection" button)

## PostgreSQL Setup

```bash
# Using psql
psql -U postgres
CREATE DATABASE codeshieldai;
CREATE USER codeshield WITH PASSWORD 'codeshield';
GRANT ALL PRIVILEGES ON DATABASE codeshieldai TO codeshield;
\q
```

Adjust the credentials to match `DATABASE_URL` in `backend/.env` (or change `.env` to match
whatever you created).

## Environment Setup

```bash
cd backend
cp .env.example .env
# Edit .env: set DATABASE_URL if different, and GROQ_API_KEY if you have one

cd ../frontend
cp .env.example .env
# Edit .env if your backend runs on a different host/port
```

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Database Migration

```bash
# From backend/, with venv activated and .env configured
alembic upgrade head
```

This creates the `projects`, `scans`, `findings`, `evidence`, and `reports` tables.

## Running the Application

**Backend** (from `backend/`, venv activated):
```bash
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

**Frontend** (from `frontend/`, in a separate terminal):
```bash
npm install
npm run dev
```
App: http://localhost:5173

## Testing

**Backend:**
```bash
cd backend
pytest
```
Backend tests use an in-memory SQLite database (via fixtures in `tests/conftest.py`), so
they run without needing PostgreSQL.

**Frontend:**
```bash
cd frontend
npm run test
```

## Expected URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/health |

## Troubleshooting

- **`alembic upgrade head` fails to connect** — verify PostgreSQL is running and
  `DATABASE_URL` in `backend/.env` matches your actual user/password/database name.
- **CORS errors in the browser** — confirm `FRONTEND_ORIGIN` in `backend/.env` matches
  the URL the frontend is actually served from (default `http://localhost:5173`).
- **"GROQ_API_KEY is not configured" on `/api/ai/test`** — set `GROQ_API_KEY` in
  `backend/.env` and restart the backend. Everything else in Phase 1 works without it.
- **`npm install` errors on peer deps** — try `npm install --legacy-peer-deps`.
- **Enum type already exists errors on `alembic upgrade head` after a failed run** — drop
  the partially-created enum types manually or drop and recreate the database, then re-run.

## Current Phase & Future Phases

**✅ Phase 1 — Foundation:** FastAPI + React scaffolding, PostgreSQL schema, project/scan/finding/evidence/report data model, Groq integration test endpoint, full dashboard UI with realistic empty states, centralized API client, tests, docs.

**✅ Phase 2 — Source Code Intelligence + RAG (this codebase):** ZIP upload and public GitHub repository import (both with path-traversal/size-limit protection), language detection, Tree-sitter structural extraction (functions/classes/imports), controlled Semgrep + Bandit subprocess execution, an Observation model distinct from confirmed Findings, a local RAG pipeline (Markdown knowledge docs → chunking → sentence-transformers embeddings → ChromaDB) covering the initial OWASP/CWE scope (SQLi, XSS, Broken Access Control/IDOR, Security Misconfiguration), an LLM structured-explanation step that grounds findings in retrieved knowledge, a background scan pipeline with granular progress (queued → extracting → parsing → static_analysis → ai_analysis → completed/failed), and frontend additions: drag-and-drop upload, GitHub import, a live analysis-progress stepper, a source explorer, and a "Security Knowledge" section on finding detail showing the RAG sources used.

**✅ Security-agent hardening + authentication:** Fixed a critical SQLAlchemy enum bug (see below), formalized the pipeline into an explicit `SecurityAgent` (observe → prioritize → hypothesize → test → evidence → verify → finding), added a deterministic Verifier (findings are only "confirmed" when evidence quality passes explicit checks — never on raw LLM confidence), added source line/column ranges to findings, added analyzer-availability detection so scans honestly report "completed with limited analysis," and added full email/password + Google OAuth authentication with per-user project ownership.

**✅ Dynamic web analysis + reporting (this update):** A real `web_application` scan pipeline — Playwright-based reconnaissance (pages, links, forms, JS resources) with graceful single-URL HTTPX fallback when Playwright isn't installed; a strict same-origin `ScanScope` (max pages/requests/duration, request timeouts, redirect limits, rate limiting) the Security Agent cannot bypass; four controlled, non-destructive dynamic checks (missing security headers, reflected-XSS via a harmless inert marker, SQL-error-based indicators via a single quote, and a deliberately low-confidence IDOR heuristic); an application map (`WebPage`/`Endpoint` tables) surfaced in the UI; HTML security report generation with the full 16-section structure; and an explicit "AI Security Reasoning" timeline (Observation → Hypothesis → Test → Evidence → Verification → Conclusion) persisted per finding and rendered in Finding Detail. Findings, Dashboard, and Finding Detail pages were also restructured to use real severity/status data and match the spec's exact section layout.

**✅ Product-grade UI/UX redesign (this update):** A new design system (deep navy/charcoal palette, restrained cyan accent, dense typography scale, technical component classes in `index.css`) replacing the earlier generic-dashboard look. A public marketing site now lives at `/` — accessible without authentication — with a hero, an illustrative (clearly labeled, non-live) product preview, the full analysis workflow diagram, capability sections, a "why an LLM alone isn't enough" trust section, and an FAQ; the authenticated workspace moved to `/dashboard` and friends. Dashboard rebuilt into a "security posture workspace" (open/critical/high counts, a real severity chart, a Project Health table) instead of four generic stat cards. Projects converted from cards to a searchable, sortable table. A new Attack Surface page aggregates discovered endpoints across scans with a detail drawer. A lightweight project-name search lives in the topbar, plus a real breadcrumb. `ProtectedRoute` now preserves the original destination via `?redirect=` so a deep link survives a login round-trip. First-time users (no projects yet) get a short onboarding screen instead of an empty grid.

**Not yet implemented:**
- Source-code/dynamic correlation (mapping a discovered web endpoint back to the exact backend source line that handles it) — each scan type produces its own findings independently; nothing cross-references a source-code finding with a live web finding yet
- A true IDE-style split-pane source viewer (repo tree + code + finding context side-by-side) with a file tree and full-text search — Finding Detail shows file/line/code snippet inline, which is a lighter version
- An attack-surface topology/graph view — Attack Surface is a filterable table + detail drawer, not a visual graph
- A full in-app multi-page report navigator (Executive Summary / Findings / Evidence / Remediation as app tabs) — the HTML report download covers the same content in one document instead
- A live, safe "explore demo" mode with sandboxed sample data on the public site — deliberately skipped rather than risk any ambiguity with "never invent data to make the UI look populated"; the public site's product preview is a static, clearly-labeled illustration instead
- A true keyboard-driven command palette (⌘K) — the topbar search is a simple project-name dropdown, not a cross-entity indexed search with keyboard navigation
- Comprehensive responsive-design audit across the full breakpoint range (Tailwind's responsive utilities are used throughout, but not verified against all 11 specified breakpoints — no browser available here to test)
- PDF report export (HTML works; PDF was explicitly deprioritized per spec: "HTML must work first")
- Refresh-token rotation on the frontend (backend `/api/auth/refresh` exists and works; the frontend doesn't yet call it automatically when an access token expires — currently the user simply has to log in again after ~30 minutes)
- Rate limiting on login attempts

No scan performs unverified analysis and no fake/mock findings are ever generated — every Finding traces back to a real Semgrep/Bandit Observation plus (when available) real retrieved RAG context, and defaults to `potential` status rather than being auto-confirmed.

---

## Phase 2 additions

### New dependencies (already in `requirements.txt`)
```
python-multipart==0.0.20       # required for ZIP file upload
tree-sitter==0.23.2
tree-sitter-languages==1.10.2
semgrep==1.97.0
bandit==1.8.0
chromadb==0.5.23
sentence-transformers==3.3.1   # pulls in torch — first install may take a while
```
Re-run `pip install -r requirements.txt` (with your venv activated) to pick these up.

### New environment variables
None required — Phase 2 runs entirely locally (local embeddings, local vector store, local file storage under `backend/storage/`). `GROQ_API_KEY` from Phase 1 is still used for the structured explanation step; if unset, findings still get created using a rule-based fallback (see `security_explainer.py`), just without the LLM's natural-language explanation.

### Database migration
```bash
cd backend
alembic upgrade head
```
This adds `source_files`, `observations`, two new columns on `scans` (`current_stage`, `error_message`), and a new `potential` value on the `finding_status` enum.

### RAG initialization (one-time, or whenever knowledge docs change)
```bash
cd backend
python -m app.services.rag.ingestion
```
This chunks and embeds the Markdown knowledge documents in `app/services/rag/knowledge_data/` into a local ChromaDB store at `backend/storage/chroma/`. The Knowledge Base page will show 0 indexed chunks until you run this.

**Do this before running scans** — without it, findings still get created (using the rule-based fallback + raw observation), just without retrieved OWASP/CWE context.

### System dependencies
Semgrep and Bandit are installed as Python packages via `requirements.txt` and invoked as subprocesses — no separate system install needed. `tree-sitter-languages` ships prebuilt grammars, so no compiler toolchain is required either.

### Run instructions
Same as Phase 1:
```bash
# backend/
uvicorn app.main:app --reload --port 8000
# frontend/
npm run dev
```

### Test commands
```bash
cd backend
pytest
```
New Phase 2 tests cover: ZIP path-traversal/size-limit rejection, language detection, Semgrep/Bandit normalization, the LLM structured-explanation fallback path, RAG chunking/frontmatter parsing, RAG retrieval shaping (mocked), GitHub URL parsing, and the source-upload API endpoint end-to-end (with storage redirected to a temp directory).

### Troubleshooting
- **First scan is slow** — the first call to the embedding model downloads `all-MiniLM-L6-v2` (~80MB) from Hugging Face; subsequent runs are fast and fully local.
- **"No source code found for this project"** — upload a ZIP or import a GitHub repo (via the Project page) *before* starting a source-code scan; scans read from `backend/storage/projects/{id}/source/`.
- **Semgrep/Bandit produce no findings** — check the backend logs; both runners log a warning and return an empty result set (rather than failing the scan) if the binary isn't on PATH or times out.
- **GitHub import fails with 400** — only public repositories are supported (no auth), and only `https://github.com/owner/repo` style URLs.
- **Knowledge Base page shows 0 indexed chunks** — run the RAG initialization command above.

### Implemented features
ZIP upload (safe extraction) · public GitHub import · language detection · Tree-sitter structure extraction · Semgrep + Bandit (controlled subprocess) · Observation model (raw, unconfirmed signals) · local RAG (Markdown → chunks → embeddings → ChromaDB) · LLM structured explanation grounded in retrieved knowledge · background scan pipeline with live progress · Finding generation defaulting to `potential` status · Source Explorer UI · Analysis Progress stepper UI · "Security Knowledge" (RAG sources) on Finding Detail · Knowledge Base page with real stats.

### Intentionally deferred features
Full multi-language Tree-sitter coverage beyond Python/JS/TS/Java/Go · CAPEC and OWASP API Security Top 10 knowledge docs (only the 4 initial-scope categories are seeded) · dynamic web application testing · HTML/PDF report export · a rich code viewer with inline line-level markers.

---

## Security Agent, Verification & Authentication (latest update)

### The critical enum bug — what it was and why it mattered
SQLAlchemy's `Enum()` column type, by default, writes a Python enum member's **name** (e.g. `GITHUB`) to the database, not its **value** (`github`) — unless `values_callable` is supplied. Every persisted enum column in this project (`Project.target_type`, `Scan.status`, `Scan.scan_type`, `Finding.severity`, `Finding.status`, `User.auth_provider`) now passes `values_callable=lambda obj: [e.value for e in obj]` so the ORM writes/reads the same lowercase values the database enum types actually store. No migration was needed for the original three columns (the Postgres enum types were already hand-authored with lowercase values); this was purely an application-code fix.

### How the Security Agent works
`app/services/security_agent/agent.py` implements one `SecurityAgent` class (not a multi-agent swarm) with explicit, separately-callable methods matching the observe → hypothesize → test → evidence → verify → finding flow:

1. **observe()** — takes the raw `Observation` rows Semgrep/Bandit produced.
2. **prioritize()** — ranks them by the tool's own reported severity, capping at 25 per scan so a large codebase doesn't run away with LLM calls.
3. **generate_hypothesis()** — a plain-language hypothesis built directly from the observation (not the LLM) — this is the thing later verified.
4. **select_controlled_test() / execute_test()** — for source code, honestly a no-op ("static analysis only — no live target to test"); this is the exact hook a future dynamic-analysis pass would fill in for a live authorized URL.
5. **collect_evidence()** — builds `Evidence` rows: one for the raw static-analysis observation, one per retrieved RAG knowledge chunk.
6. **verify()** — calls the deterministic Verifier (see below).
7. **create_finding()** — writes the `Finding` row, with `status = confirmed` only if verification passed, else `potential`.

### How verification works (never LLM confidence alone)
`app/services/security_agent/verifier.py` checks four independent signals before a finding can be `confirmed`:
- the analyzer's own reported confidence (mapped to 0–1) meets a minimum threshold,
- at least one relevant security-knowledge chunk was actually retrieved via RAG (not an empty retrieval),
- the LLM call succeeded (didn't fall back to the generic error path) and its self-reported confidence meets a minimum,
- a real source location (file + line) exists.

All four must pass. The blended confidence score stored on the finding is weighted 60% toward the deterministic analyzer signal and only 40% toward the LLM's self-assessment — deliberately, so the LLM can't unilaterally decide something is confirmed.

### How source line numbers are obtained
Semgrep's JSON output includes `start`/`end` line **and column** for every match — captured directly into `Observation.start_line/end_line/start_column/end_column` and copied onto the resulting `Finding`. Bandit only reliably reports a single `line_number` (and sometimes a `line_range`); its column/end-line fields are left `null` rather than guessed. The frontend never fabricates a location it wasn't given.

### Analyzer-availability detection ("completed" vs "completed with limited analysis")
`app/services/security_agent/dependency_check.py` runs at the start of every scan, checking whether Semgrep, Bandit, tree-sitter-languages, ChromaDB, sentence-transformers, and a configured Groq key are actually available. Missing tools are skipped (not crashed on) and recorded as a pipe-separated warning string on `Scan.warnings`, surfaced in the UI on the scan detail page — a scan is never silently reported as fully analyzed when a tool was missing.

### Authentication system
- **Email + password**: Argon2-hashed passwords (via `passlib`), never logged or stored in plaintext.
- **Google OAuth 2.0**: hand-implemented against Google's documented endpoints (`services/auth/google_oauth.py`) — no extra SDK dependency. **Requires your own credentials** from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) (OAuth Client ID → Web application → redirect URI `http://localhost:8000/api/auth/google/callback`). Without `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` set, `/api/auth/google` returns a clear 503 rather than failing silently.
- **Tokens**: short-lived JWT access token (30 min) + longer-lived refresh token (30 days), both issued as `HttpOnly` cookies — never exposed to frontend JS. `COOKIE_SECURE=false` for local HTTP dev; set to `true` once served over HTTPS.
- **Ownership**: `Project.user_id` (nullable). Every project/scan/finding/report/source-file route filters by `(user_id == current_user.id) OR (user_id IS NULL)` — a project created before authentication existed is visible to any logged-in user until "claimed" by creating/modifying it; it is never deleted or hidden entirely. A project belonging to a *different* specific user returns 404 (not 403), so its existence isn't leaked.
- **Protected routes**: every page except `/login` and `/register` requires authentication on both the frontend (`ProtectedRoute` redirects to `/login`) and, more importantly, the backend (every route depends on `get_current_user` — frontend route guards are never trusted alone).

### Database changes (this update)
One new migration (`658636f084fb`): `scans.warnings`; `observations.start_line/end_line/start_column/end_column`; `findings.start_line/end_line/start_column/end_column/code_snippet/http_method/analyzer/rule_id/verified/verification_method/verification_reason`; new `finding_status` value `accepted_risk`; new `users` table; new nullable `projects.user_id` foreign key. **No existing data is deleted** — pre-auth projects simply get `user_id = NULL`.

### APIs added/changed
- **New**: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/refresh`, `POST /api/auth/change-password`, `GET /api/auth/google`, `GET /api/auth/google/callback`.
- **Changed**: every existing route (`/projects*`, `/scans*`, `/findings*`, `/reports*`, `/knowledge/*`, `/ai/test`) now requires authentication (`Depends(get_current_user)`) and, for project-scoped resources, ownership.

### Frontend changes
New: `Login.tsx`, `Register.tsx`, `hooks/useAuth.tsx` (AuthContext), `components/ProtectedRoute.tsx`. Changed: `App.tsx` (route guards), `main.tsx` (AuthProvider), `layouts/Topbar.tsx` (real user menu with avatar/name/email/logout), `pages/Settings.tsx` (profile card + change-password form), `services/api.ts` (`credentials: "include"` on every request so auth cookies flow cross-origin, plus the new auth endpoints).

### How to run the complete system
```bash
cd backend
pip install -r requirements.txt   # adds passlib[argon2], pyjwt, email-validator
alembic upgrade head              # applies the new migration — existing data is preserved
python -m app.services.rag.ingestion   # if not already done
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install && npm run dev
```
Open http://localhost:5173 — you'll land on `/login` since nothing is authenticated yet. Register an account, then use the app as before. **Any projects you created before this update will still be there**, visible until you (or the original session's user) effectively own them.

To enable Google sign-in, add `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` to `backend/.env` per the comments in `.env.example`, then restart the backend.

### How to test with an intentionally vulnerable repository
1. Register/log in.
2. Create a project with target type "GitHub", pointing at a small, genuinely public vulnerable-by-design repo (e.g. search GitHub for a small intentionally-vulnerable Python/Node sample — avoid large training repos like the full OWASP Juice Shop for a first test, since Semgrep/Bandit runtime scales with codebase size and the free-tier LLM call budget is limited).
3. Start a scan, watch the progress stepper (queued → extracting → parsing → static_analysis → ai_analysis → completed).
4. Open the scan — check `warnings` at the top if analysis was limited (e.g. Bandit not installed).
5. Open a finding — check `verified`, `verification_reason`, `start_line`/`end_line`, and the "Security Knowledge" section for real retrieved RAG sources.

### Known limitations
- Only static/source-code analysis is implemented — no dynamic (Playwright/HTTPX) testing against live URLs yet.
- Bandit doesn't report end-line/column data, so those fields are `null` for Bandit-sourced findings (correctly, not fabricated).
- The LLM (`llama-3.3-70b-versatile` via Groq) has a training cutoff of ~December 2023 — fine for reasoning over evidence you provide, not for looking up brand-new CVEs from memory.
- Google OAuth requires you to supply your own Cloud Console credentials — untested end-to-end here since I have no network access or a Google account to test against.
- No refresh-token auto-rotation on the frontend yet — sessions expire after 30 minutes and require a fresh login (the backend endpoint exists; the frontend doesn't call it proactively yet).
- No rate limiting on login attempts yet.
- This is explicitly an **AI-assisted application security analysis platform**, not an autonomous penetration-testing system — findings should inform a human reviewer, not replace one.

---

## Dynamic Web Analysis & Reporting (latest update)

### How a web-application scan works
`app/services/scans/web_pipeline.py` runs through explicit stages (visible in the UI's progress stepper): **Scope Validation** → **Reconnaissance** → **Application Mapping** → **Security Testing** → **Evidence Collection** → **Verification** → **Completed**.

1. **Scope validation** (`services/web_analysis/scope.py`) — rejects non-http(s) URLs and missing hostnames before anything is requested. Builds a `ScanScope` restricted to the target's own host by default (same-origin), with fixed limits: 25 pages max, 100 requests max, 300s scan duration, 10s request timeout, 15s crawl timeout, 3 max redirects, a minimum delay between requests. These limits are **not configurable via the API** — a crafted request can't widen scope.
2. **Reconnaissance** (`services/web_analysis/crawler.py`) — a headless Playwright browser crawls same-origin pages, collecting links, forms (action/method/input names), and JS resource URLs. If Playwright (or its browser binary) isn't installed, this degrades gracefully to treating just the target URL as the one page to test — recorded as a warning, not a silent failure.
3. **Application mapping** — discovered pages/forms become `WebPage` and `Endpoint` rows, deduplicated by (method, URL), viewable in the scan detail page's Application Map section.
4. **Security testing** (`services/web_analysis/dynamic_checks.py`) — every request goes through `ControlledHttpClient` (`services/web_analysis/http_client.py`), which enforces the scope's redirect/timeout/rate limits in one place and redacts sensitive headers (Authorization, Cookie, Set-Cookie, API keys) before anything is stored. Four checks run per discovered endpoint:
   - **Missing security headers** — deterministic, high confidence.
   - **Reflected XSS indicator** — injects an inert marker (`csai<random><xsscheck>`, no working payload) into each query parameter and checks whether it comes back unescaped in an HTML response.
   - **SQL-injection error-based indicator** — appends a single quote to each parameter and checks the response for known database error signatures (MySQL/PostgreSQL/SQLite/Oracle/MSSQL), compared against a clean baseline request.
   - **IDOR heuristic** — requests a numeric-ID endpoint with an adjacent ID and flags it (at deliberately **low** confidence) if both return 200 with different content. This is explicitly the weakest of the four checks and is documented as a heuristic requiring manual review, not proof.
5. **Evidence collection + Verification** — every dynamic observation goes through the same `SecurityAgent` and deterministic `Verifier` as static findings (see the section above), via `verify_dynamic_finding()`, which mirrors the static verifier's four-signal structure using the dynamic check's own reported confidence instead of Semgrep/Bandit's.

### The "AI Security Reasoning" timeline
Every finding (static or dynamic) now persists a `reasoning_steps` JSON field: `[{"label": "Observation", "text": ...}, {"label": "Hypothesis", ...}, {"label": "Test", ...}, {"label": "Evidence", ...}, {"label": "Verification", ...}, {"label": "Conclusion", ...}]`, built by `SecurityAgent.build_reasoning_steps()` and rendered as a vertical timeline on the Finding Detail page — so the reasoning is inspectable, not hidden behind an opaque AI call.

### HTML report generation
`services/reporting/report_generator.py` builds a single self-contained HTML file (inline CSS, no external requests) covering all 16 spec sections (Executive Summary through Scan Errors/Warnings), generated from the scan's real findings — never manufactured statistics. Generate via the scan detail page or the Reports page; download via `GET /api/reports/{id}/download`. PDF export is not implemented (HTML works first, per spec) — any browser's "Print to PDF" works on the generated file in the meantime.

### New dependency: Playwright
```bash
pip install -r requirements.txt   # installs the playwright Python package
playwright install chromium       # separately downloads the actual browser binary — required, pip alone is not enough
```
Without the second command, dynamic scans still run (falling back to single-URL HTTPX-only testing) but won't discover multiple pages/forms — this is recorded as a `Scan.warnings` entry, not a silent limitation.

### New database changes (this update)
One migration (`f77516fcb3f2`): `scans.pages_discovered/endpoints_discovered/requests_made`; `observations.endpoint/http_method/parameter`; `findings.reasoning_steps`; new `web_pages` and `endpoints` tables.

### New APIs
`GET /api/scans/{id}/pages`, `GET /api/scans/{id}/endpoints` (application map), `POST /api/scans/{id}/reports` (generate), `GET /api/reports/{id}/download`.

### Frontend changes (this update)
`AnalysisProgress.tsx` now renders a different stage sequence for web vs. source scans, with live pages/endpoints/requests counters. `ScanDetails.tsx` gained an Application Map section and report generation/download. `Findings.tsx` gained severity/status/category filters and severity/confidence/date sorting. `FindingDetail.tsx` was restructured into the exact spec section order (Overview → Why This Was Detected → Source Location/Endpoint → Evidence → Request/Response [dynamic only] → AI Security Reasoning → Impact → Remediation → Security Knowledge → Related Findings). `Dashboard.tsx` now computes real severity breakdowns and recent findings instead of hardcoded zeros.

### Known limitations (dynamic analysis specifically)
- Only 4 dynamic check categories are implemented (missing headers, reflected XSS indicator, SQL error-based indicator, IDOR heuristic) — not full coverage of OWASP Top 10 dynamic testing.
- The IDOR check is a heuristic and will produce false positives on any endpoint that legitimately varies content by ID without an authorization bug (e.g. a public product catalog) — it's scored at low confidence specifically because of this.
- No authenticated crawling — the crawler and dynamic checks only test what's reachable without logging in, so anything behind auth is out of scope for now.
- No JavaScript-rendered SPA route discovery beyond what Playwright's `domcontentloaded` wait captures — a heavily client-side-routed app may be under-crawled.
- Untested against a live OWASP Juice Shop/NodeGoat/WebGoat instance — I have no network access in this environment to run that verification myself. **Please run this against one and tell me what you get.**

### Exact next commands to run
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
pytest
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install && npm run dev
```
Please confirm `pytest` passes — I cannot execute it from this environment. Then try a full demo: create a project with a website target (something small and safe you're authorized to test — even a local dev server), start a web scan, and watch the Application Map and Findings populate.
