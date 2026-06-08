"""
Apply Neo4j schema from Cypher file to AuraDB instance.
"""
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv


def apply_cypher(driver, cypher_file: Path) -> None:
    sql_content = cypher_file.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    
    with driver.session() as session:
        for statement in statements:
            try:
                session.run(statement)
                print(f"✓ Executed: {statement[:80]}...")
            except Exception as e:
                print(f"✗ Failed: {statement[:80]}...")
                print(f"  Error: {e}")


def main() -> None:
    load_dotenv()
    
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_user, neo4j_pass]):
        raise SystemExit("Neo4j credentials missing in .env")
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    
    root = Path(__file__).resolve().parent.parent
    cypher_file = root / "infra" / "neo4j" / "schema.cypher"
    
    print(f"Applying Neo4j schema from {cypher_file}")
    apply_cypher(driver, cypher_file)
    
    driver.close()
    print("Neo4j schema applied successfully.")


if __name__ == "__main__":
    main()
