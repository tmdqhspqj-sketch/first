# Vercel 배포

| 앱 | Production URL | Vercel 프로젝트 | 로컬 폴더 |
|----|----------------|----------------|-----------|
| **AI (랜딩+채팅)** | https://first-ai-khaki.vercel.app | `first-ai` | `frontend/` |
| **ERP** | https://first-erp-pearl.vercel.app | `first-erp` | `erp/frontend/` |
| **ERP API** | https://first-erp-api.vercel.app | `first-erp-api` | `erp/backend/` |

GitHub: https://github.com/tmdqhspqj-sketch/first — `main` push 후 자동 배포는 Vercel 대시보드에서 각 프로젝트 **Root Directory** 설정 필요.

| 프로젝트 | Root Directory | 환경 변수 |
|----------|----------------|----------|
| first-ai | `frontend` | `NEXT_PUBLIC_API_URL` |
| first-erp | `erp/frontend` | `NEXT_PUBLIC_ERP_API_URL` (별도 배포한 FastAPI URL) |

**주의:** Git push 시 Vercel은 **프론트엔드만** 자동 배포합니다. ERP API(`erp/backend`)는 Vercel에 포함되지 않습니다. `render.yaml` 또는 Railway로 API를 배포한 뒤 `NEXT_PUBLIC_ERP_API_URL`을 설정하세요.

CLI 수동 배포:

```powershell
cd frontend
npx vercel deploy --prod

cd ../erp/frontend
npx vercel deploy --prod
```
