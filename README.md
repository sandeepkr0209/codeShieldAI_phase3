# CodeShieldAI

### AI-Assisted Application Security Analysis Platform

CodeShieldAI is an evidence-driven security analysis platform that combines deterministic security scanners, source-code analysis, controlled web security checks, Retrieval-Augmented Generation (RAG), and LLM-based reasoning to identify, verify, explain, and report security findings.

> **Observation → Hypothesis → Controlled Test → Evidence → Verification → Finding → Remediation**

The LLM is used as a reasoning and explanation layer, not as a standalone vulnerability oracle.

---

## Overview

CodeShieldAI supports:

- ZIP source-code uploads
- Public GitHub repository imports
- Static analysis with Semgrep and Bandit
- Structural analysis with Tree-sitter
- Authorized web-application reconnaissance
- Playwright / HTTPX-based web analysis
- Local RAG over security knowledge
- AI-assisted Security Agent reasoning
- Deterministic finding verification
- Attack-surface mapping
- Evidence-backed findings
- HTML security reports
- Email/password and Google OAuth authentication

---

## Architecture

```text
Source Code / Authorized Web Target
                │
        ┌───────┴────────┐
        │                │
  Source Analysis    Web Analysis
        │                │
 Semgrep / Bandit   Playwright / HTTPX
 Tree-sitter        Application Mapping
        │                │
        └───────┬────────┘
                ▼
          Observations
                │
                ▼
         Security Agent
                │
       ┌────────┼────────┐
       │        │        │
   Hypothesis  RAG      LLM
       │        │        │
       └────────┼────────┘
                ▼
       Evidence Collection
                │
                ▼
     Deterministic Verification
                │
                ▼
            Findings
                │
       ┌────────┼────────┐
       │        │        │
   Dashboard Reports Remediation
```

---

# Key Features

## Source Code Security Analysis

- Public GitHub repository import
- ZIP upload with safe extraction
- Language detection
- Tree-sitter structural extraction
- Semgrep static analysis
- Bandit Python security analysis
- Normalized `Observation` model
- Source file, line, and column tracking
- Code snippets attached to findings

## AI Security Agent

CodeShieldAI uses one Security Agent rather than a multi-agent swarm:

```text
Observe
   ↓
Prioritize
   ↓
Generate Hypothesis
   ↓
Select Controlled Test
   ↓
Execute / Review Test
   ↓
Collect Evidence
   ↓
Verify
   ↓
Create Finding
```

The agent combines analyzer observations, RAG context, LLM reasoning, evidence, and deterministic verification.

## Deterministic Verification

Findings are not confirmed solely because an LLM says they are vulnerabilities.

Verification considers signals such as:

- Analyzer confidence
- Retrieved security knowledge
- LLM execution success
- LLM confidence
- Valid source or endpoint location
- Dynamic-check confidence where applicable

Findings can be represented as:

```text
Potential
Confirmed
Accepted Risk
```

## Retrieval-Augmented Generation

Security knowledge is stored locally using:

```text
Markdown Knowledge
       ↓
Chunking
       ↓
Sentence Transformers
       ↓
Embeddings
       ↓
ChromaDB
       ↓
Relevant Context
       ↓
Security Agent / LLM
```

Current knowledge covers:

- OWASP security guidance
- CWE references
- SQL injection
- Cross-site scripting
- Broken access control / IDOR
- Security misconfiguration

Retrieved knowledge is also stored as finding evidence.

---

# Dynamic Web Application Analysis

Authorized web scans follow:

```text
Scope Validation
       ↓
Reconnaissance
       ↓
Application Mapping
       ↓
Security Testing
       ↓
Evidence Collection
       ↓
Verification
       ↓
Completed
```

### Reconnaissance

Playwright can discover:

- Pages
- Links
- Forms
- Form methods
- Input parameters
- JavaScript resources

HTTPX provides a controlled fallback when browser-based reconnaissance is unavailable.

### Controlled Checks

Current dynamic checks include:

1. **Security headers** — identifies missing security-related response headers.
2. **Reflected XSS indicator** — uses a harmless inert marker and checks whether it is reflected without proper escaping.
3. **SQL error-based indicator** — compares a single-quote test against a clean baseline and checks for database error signatures.
4. **IDOR heuristic** — compares adjacent numeric IDs and is deliberately treated as a low-confidence heuristic requiring manual review.

### Safety Controls

Web analysis uses an explicit `ScanScope` with:

- Same-origin restrictions
- Maximum pages
- Maximum requests
- Scan duration limits
- Request and crawl timeouts
- Redirect limits
- Rate limiting
- Sensitive-header redaction

CodeShieldAI is intended for authorized security analysis only.

---

# Findings

A finding can contain:

- Title
- Category
- Severity
- Confidence
- Description
- Impact
- CWE
- OWASP category
- Remediation
- Source file
- Source line/column range
- Code snippet
- Endpoint
- HTTP method
- Parameter
- Analyzer
- Rule ID
- Verification status
- Verification method
- Verification reason
- Security knowledge references
- AI Security Reasoning timeline

## AI Security Reasoning

Each finding can expose:

```text
Observation
     ↓
Hypothesis
     ↓
Test
     ↓
Evidence
     ↓
Verification
     ↓
Conclusion
```

---

# Security Reports

CodeShieldAI generates self-contained HTML reports from real scan data.

Reports cover:

- Executive Summary
- Scan Overview
- Severity Distribution
- Findings
- Evidence
- Verification
- Security Knowledge
- Remediation
- Scan Statistics
- Scan Errors and Warnings

The application does not manufacture findings or statistics.

PDF export is not currently implemented; generated HTML can be printed to PDF from a browser.

---

# Authentication

CodeShieldAI supports:

### Email + Password

- Argon2 password hashing
- HttpOnly authentication cookies
- Protected backend APIs
- Protected frontend routes

### Google OAuth 2.0

Google sign-in can be enabled with credentials from Google Cloud Console.

### Tokens

- Short-lived JWT access tokens
- Longer-lived refresh tokens
- HttpOnly cookies

Backend authentication is enforced independently of frontend route protection.

---

# Product Interface

The authenticated workspace includes:

- Dashboard
- Projects
- Scans
- Scan Details
- Findings
- Finding Details
- Attack Surface
- Reports
- Knowledge Base
- Settings

The UI uses a dark, technical security-product design with severity-aware colors, security posture metrics, scan progress, application mapping, evidence, filters, and AI reasoning timelines.

---

# Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Recharts
- Lucide React

### Backend

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

### Security Analysis

- Semgrep
- Bandit
- Tree-sitter
- Playwright
- HTTPX

### AI / RAG

- Groq
- `openai/gpt-oss-120b`
- Sentence Transformers
- ChromaDB

### Authentication

- JWT
- Argon2
- Google OAuth 2.0

### Testing

- pytest
- Vitest
- React Testing Library

---

# Project Structure

```text
codeshieldai/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── code_analysis/
│   │       ├── llm/
│   │       ├── rag/
│   │       ├── security_agent/
│   │       ├── scans/
│   │       ├── web_analysis/
│   │       └── reporting/
│   ├── alembic/
│   ├── tests/
│   ├── storage/
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── hooks/
    │   ├── layouts/
    │   ├── pages/
    │   ├── services/
    │   └── types/
    ├── package.json
    └── .env.example
```

---

# Prerequisites

- Python 3.12+
- Node.js 20+
- npm
- PostgreSQL 14+
- Git
- Groq API key
- Playwright + Chromium for browser-based dynamic reconnaissance

---

# Installation

## Clone

```bash
git clone https://github.com/sandeepkr0209/codeShieldAI_phase3.git
cd codeShieldAI_phase3
```

## Backend

```bash
cd backend
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## PostgreSQL

```sql
CREATE DATABASE codeshieldai;
CREATE USER codeshield WITH PASSWORD 'codeshield';
GRANT ALL PRIVILEGES ON DATABASE codeshieldai TO codeshield;
```

## Environment

Create `backend/.env` from `.env.example` and configure:

```env
DATABASE_URL=postgresql+psycopg2://codeshield:codeshield@localhost:5432/codeshieldai
FRONTEND_ORIGIN=http://localhost:5173
FRONTEND_URL=http://localhost:5173

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

JWT_SECRET_KEY=your_secret_key
COOKIE_SECURE=false
```

For Google OAuth:

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

Never commit `.env` or API keys.

## Database Migration

```bash
alembic upgrade head
```

## Initialize RAG

```bash
python -m app.services.rag.ingestion
```

## Install Chromium

```bash
playwright install chromium
```

## Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

## Start Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

---

# Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API | http://localhost:8000/api |
| Swagger | http://localhost:8000/docs |
| Health | http://localhost:8000/api/health |

---

# Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run test
```

---

# Source-Code Scan Workflow

```text
Register / Login
        ↓
Create Project
        ↓
Import GitHub Repository / Upload ZIP
        ↓
Start Source Scan
        ↓
Source Extraction
        ↓
Tree-sitter Analysis
        ↓
Semgrep / Bandit
        ↓
Observation Normalization
        ↓
RAG Retrieval
        ↓
Security Agent
        ↓
Deterministic Verification
        ↓
Findings
        ↓
Remediation / Report
```

# Web Scan Workflow

```text
Create Web Application Project
        ↓
Authorized Target URL
        ↓
Scope Validation
        ↓
Reconnaissance
        ↓
Application Mapping
        ↓
Controlled Security Checks
        ↓
Evidence Collection
        ↓
Security Agent
        ↓
Verification
        ↓
Findings
        ↓
HTML Security Report
```

---

# Security Principles

### Evidence First

Findings should be backed by observable analyzer or application evidence.

### LLM as Reasoning Layer

The LLM interprets evidence rather than acting as an autonomous vulnerability oracle.

### Deterministic Verification

Confirmation uses explicit verification rules rather than LLM confidence alone.

### Controlled Testing

Dynamic checks are deliberately scoped and non-destructive.

### Human Review

Findings support human security review rather than replacing it.

### No Fabricated Findings

The platform does not generate fake findings or statistics simply to populate the interface.

---

# Current Coverage

| Capability | Status |
|---|---|
| GitHub repository import | ✅ |
| ZIP upload | ✅ |
| Tree-sitter analysis | ✅ |
| Semgrep | ✅ |
| Bandit | ✅ |
| RAG | ✅ |
| AI explanation | ✅ |
| Deterministic verification | ✅ |
| Web scope validation | ✅ |
| Playwright reconnaissance | ✅ |
| HTTPX controlled requests | ✅ |
| Application mapping | ✅ |
| Dynamic security checks | ✅ |
| Attack Surface | ✅ |
| HTML reports | ✅ |
| Authentication | ✅ |
| Google OAuth | ✅ |
| Authenticated web crawling | Not currently implemented |
| Full OWASP dynamic coverage | Not currently implemented |
| PDF export | Not currently implemented |

---

# Known Limitations

- No source-code ↔ live-endpoint correlation
- No authenticated web crawling
- Dynamic checks cover a limited set of security indicators
- IDOR detection is heuristic and requires manual review
- SPA route discovery can be incomplete for heavily client-side applications
- No visual attack-surface topology graph
- No full IDE-style source-code viewer
- No in-app multi-page report navigator
- PDF export is not implemented
- Frontend refresh-token rotation is not automatic
- Login rate limiting is not currently implemented

---

# Responsible Use

CodeShieldAI is intended for:

- Your own applications
- Local development environments
- Authorized security testing
- Security research with explicit permission
- Intentionally vulnerable applications designed for testing

**Do not use CodeShieldAI to scan systems without authorization.**

CodeShieldAI is an **AI-assisted application security analysis platform**, not an autonomous penetration-testing system.

---

# Project Status

**Functional integrated prototype**

The current implementation combines:

```text
Authentication
     +
Project Management
     +
Source Analysis
     +
Static Security Analysis
     +
RAG
     +
Security Agent
     +
Deterministic Verification
     +
Dynamic Web Analysis
     +
Attack Surface Mapping
     +
Findings
     +
AI Security Reasoning
     +
HTML Reporting
     +
Security-focused UI
```

---

# Future Improvements

- Source ↔ endpoint correlation
- IDE-style source viewer
- Attack-surface graph visualization
- Authenticated web scanning
- Expanded OWASP coverage
- OWASP API Security Top 10 knowledge
- CAPEC knowledge integration
- Improved SPA crawling
- PDF report generation
- CI/CD integration
- GitHub Actions integration
- Team/RBAC capabilities
- Expanded automated testing
- Production deployment hardening

---

# License

This project is primarily an educational and research project.

Add an appropriate open-source license if the repository is intended for public distribution.

---

# Author

**Sandeep Kumar**

B.Tech — Artificial Intelligence & Machine Learning

GitHub: https://github.com/sandeepkr0209

---

## CodeShieldAI

> **Observe. Reason. Verify. Secure.**
