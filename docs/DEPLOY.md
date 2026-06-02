# Git + Vercel 배포

## 구조

| 대상 | 호스팅 | 설명 |
|------|--------|------|
| **frontend/** (Next.js) | **Vercel** | 채팅 UI — Git push 시 자동 배포 |
| **backend/** (FastAPI) | 로컬 PC 또는 Railway/Render 등 | Ollama·Chroma 필요 → Vercel에 올리지 않음 |

Vercel에는 **프론트만** 배포합니다. API는 별도 URL을 환경 변수로 연결합니다.

## 1. GitHub에 올리기

```powershell
cd C:\Repo\first
git init
git add .
git commit -m "Initial commit: local LLM agent (Gemma4 + RAG + Next.js)"
git branch -M main
git remote add origin https://github.com/<YOUR_USER>/<REPO_NAME>.git
git push -u origin main
```

## 2. Vercel 연결 (자동 배포)

1. https://vercel.com → **Add New Project**
2. GitHub 저장소 Import
3. **Root Directory** → `frontend` 로 설정 (중요)
4. Environment Variables:
   - `NEXT_PUBLIC_API_URL` = 백엔드 공개 URL (예: `https://your-api.onrender.com` 또는 ngrok URL)
5. Deploy

이후 `main` 브랜치에 push 할 때마다 Vercel이 자동 빌드·배포합니다.

## 3. 백엔드를 외부에서 쓰는 경우

- 로컬만: Vercel 사이트에서 API 호출 불가 (localhost). 개발은 `npm run dev` + 로컬 API.
- 공개 API: Railway/Render/Fly에 `backend` 배포 후 `NEXT_PUBLIC_API_URL` 설정.
- **Ollama는 여전히 GPU PC에서 실행** — 클라우드 백엔드만으로는 동일 스택 불가.

## 4. 로컬에서 Vercel CLI (선택)

```powershell
npm i -g vercel
cd frontend
vercel link
vercel --prod
```
