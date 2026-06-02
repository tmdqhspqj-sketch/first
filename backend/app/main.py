import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agent.graph import run_agent
from app.services.config_loader import get_model, get_persona, list_models, list_personas
from app.services.ollama import ollama_client
from app.services.rag import rag_store
from app.settings import settings

@asynccontextmanager
async def lifespan(_app: FastAPI):
    sample = settings.data_path / "sample_corpus.txt"
    if sample.exists() and rag_store.count == 0:
        try:
            await rag_store.ingest_file(sample)
        except Exception:
            pass
    yield


app = FastAPI(title="Local LLM Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    persona_id: str = "assistant"
    model_id: str = "default"
    use_rag: bool = True
    use_tools: bool = False
    stream: bool = False
    images_base64: list[str] = Field(
        default_factory=list,
        description="Base64-encoded images for Gemma 4 vision",
    )


class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = "api"


@app.get("/health")
async def health():
    ollama_status: dict = {"ok": False, "error": None, "models": []}
    try:
        ollama_status = await ollama_client.health()
    except Exception as e:
        ollama_status["error"] = str(e)

    return {
        "status": "ok" if ollama_status.get("ok") else "degraded",
        "ollama": ollama_status,
        "rag": {"chunks": rag_store.count, "chroma_path": str(settings.chroma_dir)},
    }


@app.get("/v1/personas")
async def personas():
    return {"personas": list_personas()}


@app.get("/v1/models")
async def models():
    return {"models": list_models()}


@app.post("/v1/ingest")
async def ingest_text(body: IngestTextRequest):
    n = await rag_store.ingest_text(body.text, source=body.source)
    return {"ingested_chunks": n, "total_chunks": rag_store.count}


@app.post("/v1/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 text") from None
    n = await rag_store.ingest_text(text, source=file.filename or "upload")
    return {"ingested_chunks": n, "total_chunks": rag_store.count}


@app.post("/v1/ingest/path")
async def ingest_path(relative_path: str = Query(...)):
    path = (settings.data_path / relative_path).resolve()
    if not path.is_relative_to(settings.data_path.resolve()):
        raise HTTPException(400, "Path must stay under data/")
    if not path.exists():
        raise HTTPException(404, "File not found")
    n = await rag_store.ingest_file(path)
    return {"ingested_chunks": n, "total_chunks": rag_store.count}


@app.post("/v1/chat")
async def chat(body: ChatRequest):
    if not get_persona(body.persona_id):
        raise HTTPException(404, f"Persona not found: {body.persona_id}")
    if not get_model(body.model_id):
        raise HTTPException(404, f"Model not found: {body.model_id}")

    history = [{"role": m.role, "content": m.content} for m in body.history]

    if body.stream:
        return StreamingResponse(
            _stream_chat(body, history),
            media_type="text/event-stream",
        )

    result = await run_agent(
        body.message,
        messages=history,
        persona_id=body.persona_id,
        model_id=body.model_id,
        use_rag=body.use_rag,
        use_tools=body.use_tools,
        images=body.images_base64 or None,
    )
    return result


async def _stream_chat(body: ChatRequest, history: list[dict]):
    result = await run_agent(
        body.message,
        messages=history,
        persona_id=body.persona_id,
        model_id=body.model_id,
        use_rag=body.use_rag,
        use_tools=body.use_tools,
        images=body.images_base64 or None,
    )
    answer = result.get("answer", "")
    chunk_size = 32
    for i in range(0, len(answer), chunk_size):
        payload = {"type": "token", "content": answer[i : i + chunk_size]}
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done', 'retrieved': result.get('retrieved', []), 'tool_name': result.get('tool_name'), 'tool_result': result.get('tool_result')}, ensure_ascii=False)}\n\n"
