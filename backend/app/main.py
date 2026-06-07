from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from app.clients import get_neo4j_driver, get_langfuse_client, get_supabase_client
from app.config import settings

app = FastAPI(title="TuVi-BatTu GraphRAG - FastAPI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

supabase = get_supabase_client()
neo4j_driver = get_neo4j_driver()
langfuse = get_langfuse_client()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chart/tuvi")
async def create_tuvi_chart(payload: dict):
    # Placeholder endpoint for TuVi chart generation
    return JSONResponse({"status": "not_implemented", "message": "TuVi chart generation is pending implementation."}, status_code=501)


class ChatRequest(BaseModel):
    chart_id: str
    query: str
    user_id: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        langfuse.log_event("chat_request", {
            "chart_id": req.chart_id,
            "user_id": req.user_id,
            "query": req.query,
        })
    except Exception:
        pass

    return JSONResponse(
        {
            "status": "not_implemented",
            "message": "Chat orchestration is pending implementation.",
            "query": req.query,
        },
        status_code=501,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info")