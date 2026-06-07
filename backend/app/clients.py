import requests
from neo4j import GraphDatabase
from supabase import create_client
from .config import settings


class LangfuseClient:
    def __init__(self, base_url: str, public_key: str, secret_key: str):
        self.base_url = base_url.rstrip("/")
        self.public_key = public_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.secret_key,
        })

    def log_event(self, event_name: str, payload: dict):
        url = f"{self.base_url}/events"
        body = {
            "event": event_name,
            "public_key": self.public_key,
            "payload": payload,
        }
        response = self.session.post(url, json=body)
        response.raise_for_status()
        return response.json()


def get_supabase_client():
    return create_client(settings.NEXT_PUBLIC_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_neo4j_driver():
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
    )


def get_langfuse_client():
    return LangfuseClient(
        base_url=settings.LANGFUSE_BASE_URL,
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
    )
