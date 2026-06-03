# Backend

FastAPI backend for Word Report QA Assistant.

## Setup

```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8011/health
```

Local environment defaults:

```text
WORD_QA_DATABASE_URL=sqlite:///./word_qa.db
WORD_QA_FRONTEND_ORIGINS=http://localhost:5175,http://127.0.0.1:5175
```

## Tests

```powershell
pytest
```

Current tests cover parser extraction, comments/tracked changes detection, deterministic QA rules, Excel export, and the upload to parse to QA to export API workflow.
