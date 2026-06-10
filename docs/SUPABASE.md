# Hong ERP + Supabase

## 프로젝트

| 항목 | 값 |
|------|-----|
| URL | https://oglrabxukdfirjuneogx.supabase.co |
| Region | ap-northeast-2 (Seoul) |
| DB | Postgres 17 |

## SQLite → Postgres

로컬 MVP 개발 시 `erp/backend/erp.db`(SQLite)를 사용했습니다. 운영 DB는 **Supabase Postgres**입니다.

- `.gitignore`에 `erp.db`가 포함되어 있어 Git에는 올라가지 않습니다.
- 새 배포/로컬 실행 시 `ERP_DATABASE_URL`만 Supabase URI로 설정하면 됩니다.

## 연결 문자열

Supabase 대시보드 → **Settings → Database → Connection string → URI**

- 권장: **Transaction pooler** (port `6543`)
- 예시 형식:

```
postgresql://postgres.oglrabxukdfirjuneogx:[PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

`erp/backend/.env`에 `ERP_DATABASE_URL`로 설정하세요.

## 시드 계정

| login_id | password | role |
|----------|----------|------|
| admin | admin | admin |
| hongseungbo | hongsb | admin |
| sajang, sangmu, bujang, staff1 | demo1 | manager/user |

## 관리자 정책

- `admin` 역할은 여러 명 가능
- **비활성화**만 지원 (즉시 삭제 없음)
- 비활성화 후 **7일** 지나면 백그라운드 작업이 자동 **완전 삭제**
- 마지막 활성 admin은 비활성화 불가
- 본인 계정 비활성화 불가

## ERP API (Vercel)

| 항목 | 값 |
|------|-----|
| Production URL | https://first-erp-api.vercel.app |
| Vercel 프로젝트 | `first-erp-api` |
| 로컬 폴더 | `erp/backend/` |

### 필수 환경 변수 (`first-erp-api`)

| 변수 | 상태 |
|------|------|
| `ERP_CORS_ORIGINS` | 설정됨 |
| `ERP_SECRET_KEY` | 설정됨 |
| `ERP_DATABASE_URL` | **미설정** — Supabase DB URI 필요 |

Supabase 연결 문자열: 대시보드 → Settings → Database → URI (pooler port `6543`)

또는 Vercel Marketplace에서 **Supabase** 통합 설치 후 `POSTGRES_URL` 자동 주입 (코드가 fallback 지원).

### 프론트 연동 (`first-erp`)

`NEXT_PUBLIC_ERP_API_URL=https://first-erp-api.vercel.app` (설정·재배포 완료)

## 로컬 실행

```powershell
cd erp/backend
pip install -r requirements.txt
# .env 작성 후
uvicorn app.main:app --reload --port 8001
```

```powershell
cd erp/frontend
npm run dev
```
