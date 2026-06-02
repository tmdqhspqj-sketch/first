# hsb PC — 하드웨어 및 모델 매핑

## 확인된 사양 (2026-06-02)

| 항목 | 값 |
|------|-----|
| 장치 이름 | hsb |
| CPU | AMD Ryzen 5 7500F 6-Core (3.70 GHz) |
| RAM | 32.0 GB |
| GPU | **NVIDIA GeForce RTX 4060** |
| VRAM | **8 GB** (8188 MiB) |
| Ollama | 0.24.0 |

## Gemma 4 선택 (Gemma 4 ≠ Gemma 3)

Google **Gemma 4** (2026-04)는 멀티모달(이미지·텍스트), 에이전트·툴 호출에 맞춰 설계되었습니다.  
RTX 4060 8GB에서는 **`gemma4:e4b`** 가 적합합니다 (디스크 ~9.6GB, VRAM ~5–7GB + 컨텍스트).

| 모델 | 8GB VRAM | 비고 |
|------|----------|------|
| `gemma4:e2b` | 여유 | 더 가볍지만 품질↓ |
| **`gemma4:e4b` / `local-agent`** | **권장** | 비전 + 에이전트 |
| `gemma4:26b` | 비권장 | MoE지만 가중치 ~18GB |
| `gemma4:31b` | 불가 | 20GB+ |

## 설치된 Ollama 모델

```
local-agent     ← gemma4:e4b + num_ctx 8192
gemma4:e4b      ← 베이스 멀티모달
embeddinggemma  ← RAG 임베딩
```

## 기능 매핑

| 기능 | 구현 |
|------|------|
| 비전 | 채팅 API `images_base64`, UI 📷 버튼 |
| 툴 | `use_tools=true` → Ollama `tools` API + LangGraph `tool` 노드 |
| RAG | `embeddinggemma` + ChromaDB |

## VRAM 절약 팁

- `local-agent`는 `num_ctx 8192` (Modelfile)
- 채팅 시 Chrome/게임 등 GPU 사용 앱 종료
- OOM 시 `config/models/gemma4-light.yaml` + `num_ctx 4096` 사용
