TuVi / BaTu GraphRAG — MVP scaffold

This repository contains initial scaffolding for the project. See `docs/README.md` for next steps and references to `specifications.md` and `plan.md`.

Quick start (backend):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend/app --reload
```

Local environment setup:

```powershell
copy .env.example .env
```

Then fill `.env` with your Supabase, Neo4j, Langfuse, and Gemini credentials.

Useful scripts:

- `python scripts/apply_supabase_schema.py` — apply Supabase schema and seed data using `DATABASE_URL` from `.env`
- `python scripts/ingest_pdf.py` — extract and chunk PDF data from `data/tuvi` and `data/battu`
