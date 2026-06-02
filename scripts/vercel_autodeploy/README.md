# Playwright: GitHub + Vercel 자동 배포

## 실행

```powershell
cd C:\Repo\first\scripts\vercel_autodeploy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
$env:GITHUB_REPO_NAME = "local-llm-agent"
# push 자동화용 (권장): GitHub → Settings → Developer settings → PAT
# $env:GITHUB_TOKEN = "ghp_xxxx"
python deploy.py
```

브라우저가 열리면 **GitHub 로그인 → 저장소 생성 → git push → Vercel 로그인(GitHub 연동) → Import → Deploy** 순으로 진행됩니다.

로그인 상태는 `auth/*.json`에 저장되어 다음 실행부터 빠릅니다.

## Vercel 설정

- Root Directory: `frontend` (스크립트가 입력 시도)
- `NEXT_PUBLIC_API_URL` 은 백엔드 공개 URL이 있을 때만 설정
