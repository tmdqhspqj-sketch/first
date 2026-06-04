# Vercel 배포 (Git 연동)

동일 저장소에서 **프로젝트 2개**를 만드는 것을 권장합니다.

| Vercel 프로젝트 | Root Directory | 환경 변수 |
|-----------------|----------------|----------|
| first-ui (AI) | `frontend` | `NEXT_PUBLIC_API_URL` = 백엔드 URL |
| first-erp | `erp/frontend` | `NEXT_PUBLIC_ERP_API_URL` = ERP API URL |

`main` 브랜치 push 시 각 프로젝트가 자동 배포됩니다.

CLI 수동 배포:

```powershell
cd frontend
npx vercel deploy --prod

cd ../erp/frontend
npx vercel deploy --prod
```
