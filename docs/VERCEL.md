# Vercel 배포

| 앱 | Production URL | Vercel 프로젝트 | 로컬 폴더 |
|----|----------------|----------------|-----------|
| **AI (랜딩+채팅)** | https://first-ai-khaki.vercel.app | `first-ai` | `frontend/` |
| **ERP** | https://first-erp-pearl.vercel.app | `first-erp` | `erp/frontend/` |

GitHub: https://github.com/tmdqhspqj-sketch/first — `main` push 후 자동 배포는 Vercel 대시보드에서 각 프로젝트 **Root Directory** 설정 필요.

| 프로젝트 | Root Directory | 환경 변수 |
|----------|----------------|----------|
| first-ai | `frontend` | `NEXT_PUBLIC_API_URL` |
| first-erp | `erp/frontend` | `NEXT_PUBLIC_ERP_API_URL` |

CLI 수동 배포:

```powershell
cd frontend
npx vercel deploy --prod

cd ../erp/frontend
npx vercel deploy --prod
```
