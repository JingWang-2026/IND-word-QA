# Word Report QA Assistant

Full-stack MVP for `.docx` Word document QA.

This project only targets Word document quality checks. It does not implement PDF, OCR, eCTD, regulatory compliance judgement, electronic signatures, or automatic Word rewriting.

## Structure

```text
backend/   FastAPI, SQLModel, SQLite
frontend/  React, TypeScript, Vite, TailwindCSS
storage/   Local uploaded files and future exports
```

## Backend

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8011/health
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5175`.

The frontend reads its backend URL from `frontend/.env.local`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8011
```

## Fixed Local Ports

```text
Software: Word Report QA Assistant
Frontend: http://localhost:5175
Backend:  http://127.0.0.1:8011
Database: SQLite local file, no network port
API base: http://127.0.0.1:8011
```

## One-command Local Start

```powershell
.\scripts\start-local.ps1
```

Or start services separately:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

## Local Verification

Run from the project root:

```powershell
npm run check
npm run check:ports
npm run check:health
npm run test:smoke
```

These commands verify fixed local ports, environment files, `VITE_API_BASE_URL`, backend `/health`, frontend reachability, and the frontend-to-backend health call.

## Phase Status

Implemented:

- Phase 0 project skeleton
- Phase 1 database models and CRUD APIs
- Phase 2 `.docx` parser for paragraphs, headings, tables, headers, footers, comments, tracked changes, hidden text, and metadata
- Phase 3 QA engine framework and first deterministic rules
- Phase 4 advanced deterministic rules
- Phase 5 frontend project, upload, parse, QA, issue list, issue detail, and review flow
- Phase 6 Excel QA log export
- Phase 7 generated sample docx fixtures and automated tests

Implemented rule IDs:

- `TEXT-001`, `TEXT-002`
- `NUM-001`
- `TABLE-001`, `TABLE-002`, `TABLE-003`
- `REF-001`
- `HEAD-001`
- `WORD-001`, `WORD-002`, `WORD-003`
- `ABBR-001`, `ABBR-002`
- `TERM-001`

## Main API

- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/documents`
- `GET /api/projects/{project_id}/documents`
- `POST /api/documents/{document_id}/parse`
- `GET /api/documents/{document_id}/parsed-summary`
- `POST /api/documents/{document_id}/qa/run`
- `POST /api/projects/{project_id}/qa/run`
- `GET /api/projects/{project_id}/issues`
- `GET /api/issues/{issue_id}`
- `PATCH /api/issues/{issue_id}`
- `GET /api/projects/{project_id}/export/issues.xlsx`

## Test Fixtures

Generate sample Word files:

```powershell
cd backend
python app\tests\fixtures\generate_sample_docx.py
```

Fixture outputs:

- `backend/app/tests/fixtures/sample_bad_report.docx`
- `backend/app/tests/fixtures/sample_clean_report.docx`

## Known Limitations

- No PDF, OCR, eCTD, regulatory compliance judgement, electronic signatures, or automatic Word rewriting.
- Table total checks intentionally support only simple numeric tables.
- Abbreviation and terminology rules use conservative regex heuristics.
- AI semantic QA is not implemented; the deterministic MVP works without AI.
