# PRD: 로컬 LLM AI 에이전트 (MVP)

## 1. 개요

Ollama로 로컬 LLM을 설치·풀링하고, Python 백엔드와 Next.js 프론트엔드로 **로컬에서 동작하는 AI 에이전트**를 구축한다.  
최초 목표는 **간단한 RAG 기반 MVP**로 모델·파이프라인·툴 호출 흐름을 검증하는 것이다.

## 2. 목표

| 구분 | 내용 |
|------|------|
| **1차 (MVP)** | Ollama 로컬 모델 + 단순 RAG로 질의·응답 및 컨텍스트 검색 검증 |
| **2차** | LangGraph로 툴 호출·다단계 추론·상태 관리 |
| **3차** | FastMCP 도구 연동, 페르소나·모델 설정 파일 기반 운영 |

## 3. 기술 스택

| 영역 | 기술 | 역할 |
|------|------|------|
| LLM 런타임 | **Ollama** | 로컬 모델 설치·풀링·추론 |
| 오케스트레이션 | **LangGraph** | 툴 호출, 단계 분기, 에이전트 상태·그래프 실행 |
| MCP 서버 | **FastMCP** (Python) | 외부/내부 도구를 MCP 프로토콜로 노출 |
| API | **FastAPI** (Python) | REST/SSE 등 API, 헬스체크, RAG·에이전트 엔드포인트 |
| 프론트엔드 | **Next.js** | 채팅 UI, 설정, API 연동 |
| 설정 | **모델 파일** (YAML/JSON 등) | 페르소나, 시스템 프롬프트, 모델명·파라미터 |

## 4. 아키텍처 (개념)

```
[Next.js UI]
     │ HTTP/SSE
     ▼
[FastAPI] ──► [LangGraph Agent]
     │              │
     │              ├── Ollama (로컬 LLM)
     │              ├── RAG (벡터 DB / 임베딩)
     │              └── FastMCP (툴)
     ▼
[페르소나·모델 설정 파일]
```

- **프론트**: 사용자 입력, 스트리밍 응답, (선택) 페르소나·모델 선택.
- **FastAPI**: 인증·CORS·라우팅, LangGraph 실행 트리거, RAG 검색 API.
- **LangGraph**: 노드(검색 → 생성 → 툴 호출 → 재생성 등)와 엣지로 워크플로 정의.
- **FastMCP**: 에이전트가 호출할 도구(파일, DB, API 등)를 MCP로 제공.
- **설정 파일**: 코드 변경 없이 페르소나·모델 교체.

## 5. MVP 범위 (RAG 검증)

### 포함

- Ollama 설치 및 대상 모델 풀링 (예: `llama3`, `qwen2` 등 1종 고정)
- 문서 업로드 또는 고정 코퍼스 → 청킹 → 임베딩 → 벡터 저장
- 사용자 질의 → 유사 청크 검색 → 컨텍스트 주입 → Ollama 응답
- FastAPI: `/health`, `/chat` 또는 `/query` (동기 또는 스트리밍)
- Next.js: 단일 채팅 화면, API URL 설정

### 제외 (MVP 이후)

- 복잡한 멀티 에이전트·장기 메모리
- 프로덕션급 인증·멀티테넌시
- 전체 MCP 도구 세트 (MVP는 RAG만, 툴은 스텁 또는 1개 샘플)

## 6. LangGraph · MCP 단계 (MVP 이후)

1. **그래프 정의**: `retrieve` → `generate` → (필요 시) `tool_call` → `generate`.
2. **툴 노드**: FastMCP 클라이언트로 도구 목록 조회·실행, 결과를 상태에 반영.
3. **조건 분기**: 툴 필요 여부, RAG 신뢰도, 최대 반복 횟수 등.
4. **상태**: 메시지 히스토리, 검색 결과, 툴 출력을 LangGraph `State`에 통합.

## 7. 페르소나·모델 설정 (모델 파일)

- 경로 예: `config/personas/`, `config/models/`
- 페르소나: 이름, system prompt, tone, 금지 사항
- 모델: Ollama 모델 태그, temperature, top_p, max_tokens
- 런타임: API 또는 UI에서 persona_id / model_id 로드

## 8. API (FastAPI) 초안

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | Ollama·벡터 DB 연결 상태 |
| POST | `/v1/chat` | RAG + (추후) LangGraph 에이전트 실행 |
| POST | `/v1/ingest` | (MVP) 문서 인덱싱 |
| GET | `/v1/personas` | 페르소나 목록 (설정 파일 기반) |

## 9. 프론트엔드 (Next.js) 초안

- 채팅 패널 (메시지 목록, 입력, 전송)
- (선택) 페르소나·모델 드롭다운
- 환경 변수: `NEXT_PUBLIC_API_URL`
- 스트리밍 응답 표시 (SSE 또는 fetch stream)

## 10. 디렉터리 구조 (권장)

```
first/
├── docs/
│   └── PRD.md
├── backend/          # FastAPI + LangGraph + RAG
│   ├── app/
│   ├── mcp/          # FastMCP 서버
│   └── pyproject.toml / requirements.txt
├── frontend/         # Next.js
├── config/
│   ├── personas/
│   └── models/
└── data/             # RAG 코퍼스 (로컬)
```

## 11. 성공 기준 (MVP)

- [ ] Ollama에서 지정 모델이 로컬에서 응답 생성
- [ ] 업로드/고정 문서 기준 RAG 질의 시 관련 문단이 답에 반영됨
- [ ] FastAPI `/health`, 질의 API가 Next.js에서 호출 가능
- [ ] (선택) LangGraph 1노드 RAG 파이프라인이 그래프로 실행됨

## 12. 리스크·전제

- **전제**: 개발 머신에 GPU/충분한 RAM, Ollama 데몬 상시 실행
- **리스크**: 로컬 모델 품질·속도 → MVP는 소형 모델 + 짧은 컨텍스트로 완화
- **리스크**: MCP·LangGraph 통합 복잡도 → MVP 이후 단계적으로 도입

## 13. 로드맵 요약

| 단계 | 산출물 |
|------|--------|
| **0** | Ollama 설치, 모델 pull, CLI/API 스모크 테스트 |
| **1 (MVP)** | RAG + FastAPI + Next.js 채팅 |
| **2** | LangGraph 워크플로, 툴 호출 루프 |
| **3** | FastMCP 도구, 페르소나·모델 파일 운영 |

---

*문서 버전: 0.1 · 최초 작성: 로컬 LLM 에이전트 기획 요약*
