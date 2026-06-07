import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv


def load_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def execute_sql(connection_string: str, sql: str) -> None:
    with psycopg.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()


def main() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required in .env to apply Supabase schema.")

    root = Path(__file__).resolve().parent.parent
    schema_path = root / "infra" / "supabase" / "schema.sql"
    seed_path = root / "infra" / "supabase" / "seed.sql"

    print(f"Applying schema from {schema_path}")
    schema_sql = load_sql(schema_path)
    execute_sql(database_url, schema_sql)
    print("Schema applied successfully.")

    print(f"Applying seed from {seed_path}")
    seed_sql = load_sql(seed_path)
    execute_sql(database_url, seed_sql)
    print("Seed data applied successfully.")


if __name__ == "__main__":
    main()
