# Backend

FastAPI backend for Word Report QA Assistant.

## Setup

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

## Tests

```powershell
pytest
```

Current tests cover parser extraction, comments/tracked changes detection, deterministic QA rules, Excel export, and the upload to parse to QA to export API workflow.
