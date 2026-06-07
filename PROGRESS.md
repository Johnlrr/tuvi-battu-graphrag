# Progress Report

## Completed

- Created root `.env` for local secrets and blanked `.env.example` to avoid storing secrets in example files.
- Added backend config and client helpers for Supabase, Neo4j, and Langfuse.
- Extended backend fastapi skeleton with CORS and stub endpoints:
  - `/health`
  - `/chart/tuvi`
  - `/chat`
- Added Supabase schema trigger for `updated_at` and created seed SQL file.
- Created Neo4j schema setup script in `infra/neo4j/schema.cypher`.
- Added frontend auth and routing skeleton:
  - landing page
  - login
  - register
  - dashboard
  - chart detail
- Added Supabase client for frontend in `frontend/lib/supabaseClient.ts`.
- Created PDF ingestion script `scripts/ingest_pdf.py` to extract and chunk documents from `data/tuvi` and `data/battu`.
- Added `scripts/apply_supabase_schema.py` for applying Supabase schema and seed data via `DATABASE_URL`.
- Verified Python syntax for backend and ingestion scripts.

## Notes

- Supabase CLI is not installed locally, so `infra/supabase/schema.sql` and `infra/supabase/seed.sql` are ready but not applied automatically.
- Neo4j schema script is available, but actual database execution requires connecting to the AuraDB instance.
- Frontend dependencies updated in `frontend/package.json`, but package installation has not been run yet.

## Next steps

1. Fill `.env` with real credentials and run `python scripts/apply_supabase_schema.py`.
2. Run `npm install` inside `frontend/` and start the Next.js app.
3. Apply `infra/neo4j/schema.cypher` to the Neo4j AuraDB instance.
4. Run `python scripts/ingest_pdf.py` to create chunk JSON from the PDF corpus.
