# Hong ERP (간단 사내 ERP)

## 기능

- **로그인** · 직급 8단 (사장~사원)
- **결재**: 휴가 신청, 상품 아이디어 신청 · 결재선 **부장(팀장) → 상무 → 사장**
- **admin** (`admin`, `hongseungbo`): 결재 **승인 없음**, **전체 관람만**, 관리자 계정 CRUD
- **회의실 예약** · **쪽지/메일**
- **사용자 관리** (admin / manager) · 비활성화 후 7일 뒤 자동 삭제

## 실행

```powershell
# 백엔드 (포트 8001)
cd erp\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# 프론트 (포트 3001)
cd erp\frontend
copy .env.local.example .env.local
npm install
npm run dev
```

http://localhost:3001/login

## 계정

| ID | 비밀번호 | 역할 |
|----|----------|------|
| admin | `.env`의 `ERP_ADMIN_PASSWORD` (기본 admin) | admin |
| hongseungbo | `.env`의 `ERP_HONG_PASSWORD` (기본 hongsb) | admin |
| sajang | demo1 | manager (사장) |
| sangmu | demo1 | manager |
| bujang | demo1 | user + 1차 결재 (팀장) |
| staff1 | demo1 | user |

DB는 **Supabase Postgres** 사용. [docs/SUPABASE.md](../docs/SUPABASE.md) 참고.

Vercel(`first-erp`)은 프론트만 배포됩니다. API는 Render/Railway 등에 `erp/backend`를 별도 배포하고 `NEXT_PUBLIC_ERP_API_URL`을 연결하세요.
