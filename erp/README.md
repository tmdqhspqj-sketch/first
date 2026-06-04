# Hong ERP (간단 사내 ERP)

## 기능

- **로그인** · 직급 8단 (사장~사원)
- **결재**: 휴가 신청, 상품 아이디어 신청 · 결재선 **부장(팀장) → 상무 → 사장**
- **super** (`hongseungbo`): 결재 **승인 없음**, **전체 관람만**
- **회의실 예약** · **쪽지/메일**
- **사용자 관리** (super / manager)

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
| hongseungbo | `.env`의 `ERP_SUPER_PASSWORD` (기본 example은 .env.example 참고, 시드 기본 hongsb) | super |
| sajang | demo1 | manager (사장) |
| sangmu | demo1 | manager |
| bujang | demo1 | user + 1차 결재 (팀장) |
| staff1 | demo1 | user |

`.env`에 `ERP_SUPER_PASSWORD=hongsb` 설정 후 백엔드 재시작.
