# Local LLM Agent (Ollama + RAG + LangGraph)

로컬 Ollama 모델, RAG(ChromaDB), LangGraph 에이전트, FastAPI, FastMCP, Next.js 채팅 UI.

## GitHub + Vercel

- 로컬 Git: `main` 브랜치에 커밋됨
- GitHub 푸시: `.\scripts\push-github.ps1 -RepoUrl "https://github.com/<USER>/<REPO>.git"`
- Vercel: 저장소 연결 후 **Root Directory = `frontend`**, `NEXT_PUBLIC_API_URL` 설정  
  → [docs/DEPLOY.md](docs/DEPLOY.md)

## 권장 하드웨어 (확인됨: hsb PC)

| 항목 | 사양 |
|------|------|
| CPU | AMD Ryzen 5 7500F (6코어) |
| RAM | 32GB |
| GPU | **NVIDIA GeForce RTX 4060 (8GB VRAM)** |

## 사전 요구 — Ollama + Gemma 4

1. [Ollama](https://ollama.com) 0.20+ (winget: `Ollama.Ollama`)
2. 모델 일괄 설치 (RTX 4060 8GB 기준):

```powershell
.\scripts\setup-models.ps1
```

설치되는 모델:

| 모델 | 용도 |
|------|------|
| `gemma4:e4b` | 멀티모달(비전)·에이전트·툴 호출 |
| `local-agent` | `num_ctx 8192`로 VRAM 절약한 커스텀 Gemma4 |
| `embeddinggemma` | RAG 임베딩 |

임베딩 모델을 바꾼 경우 `data/chroma` 폴더를 삭제한 뒤 API를 재시작하세요.

## 백엔드

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/health
- Chat: `POST /v1/chat`
- Ingest: `POST /v1/ingest`, `POST /v1/ingest/file`

시작 시 `data/sample_corpus.txt`가 비어 있으면 자동 인덱싱됩니다.

### FastMCP (별도 프로세스)

```powershell
cd backend
$env:PYTHONPATH = "."
python -m agent_mcp.server
```

도구: `get_time`, `echo`. LangGraph에서는 `use_tools=true`일 때 `[TOOL:get_current_time|{}]` 패턴으로 호출합니다.

## 프론트엔드

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

http://localhost:3000 — API 기본값 `http://127.0.0.1:8000`

## 설정 파일

| 경로 | 설명 |
|------|------|
| `config/personas/*.yaml` | 시스템 프롬프트·톤 |
| `config/models/*.yaml` | Ollama 모델·temperature |
| `data/` | RAG 문서·Chroma 저장 (`data/chroma/`) |

## LangGraph 흐름

`retrieve` → `generate` → (옵션) `tool` → END

## 프로젝트 구조

```
first/
├── backend/app/      # FastAPI, RAG, LangGraph
├── backend/agent_mcp/  # FastMCP 서버
├── frontend/         # Next.js UI
├── config/           # 페르소나·모델 YAML
├── data/             # 코퍼스 + Chroma
└── docs/PRD.md
```
