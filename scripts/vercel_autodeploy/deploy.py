"""
GitHub repo create + git push + Vercel import/deploy via Playwright.

First run: browser opens — log in to GitHub and Vercel when prompted.
Login state is saved under auth/ for later runs.

Env:
  GITHUB_REPO_NAME   default: local-llm-agent
  GITHUB_TOKEN       optional — HTTPS push without prompt
  VERCEL_TEAM        optional team slug in URL
  PROJECT_ROOT       default: repo root (parent of scripts/)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", SCRIPT_DIR.parent.parent))
AUTH_DIR = SCRIPT_DIR / "auth"
GITHUB_STATE = AUTH_DIR / "github_state.json"
VERCEL_STATE = AUTH_DIR / "vercel_state.json"

REPO_NAME = os.environ.get("GITHUB_REPO_NAME", "local-llm-agent")
GIT_EXE = Path(r"C:\Program Files\Git\bin\git.exe")
FRONTEND_ROOT = "frontend"
LOGIN_WAIT_SEC = 300


def log(msg: str) -> None:
    print(f"[deploy] {msg}", flush=True)


def git(*args: str, cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess:
    if not GIT_EXE.exists():
        raise FileNotFoundError("Git not found. Install Git for Windows.")
    return subprocess.run(
        [str(GIT_EXE), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _github_logged_in(page: Page) -> bool:
    if page.locator('meta[name="user-login"]').count():
        content = page.locator('meta[name="user-login"]').first.get_attribute("content") or ""
        return bool(content.strip())
    return page.locator('button[aria-label*="Create"]').count() > 0


def wait_for_github_login(page: Page) -> None:
    page.goto("https://github.com/login", wait_until="domcontentloaded")
    log(f"GitHub login - sign in in the browser (max {LOGIN_WAIT_SEC}s)")
    deadline = time.time() + LOGIN_WAIT_SEC
    while time.time() < deadline:
        page.goto("https://github.com/", wait_until="domcontentloaded")
        if _github_logged_in(page):
            return
        page.wait_for_timeout(2000)
    raise TimeoutError("GitHub login timed out")


def _vercel_logged_in(page: Page) -> bool:
    if "login" in page.url.lower() or "signup" in page.url.lower():
        return False
    return (
        page.locator('a[href="/new"]').count() > 0
        or page.locator('text=Add New').count() > 0
        or page.locator('text=Projects').count() > 0
    )


def wait_for_vercel_login(page: Page) -> None:
    page.goto("https://vercel.com/login", wait_until="domcontentloaded")
    log(f"Vercel login - sign in with GitHub in the browser (max {LOGIN_WAIT_SEC}s)")
    deadline = time.time() + LOGIN_WAIT_SEC
    while time.time() < deadline:
        page.goto("https://vercel.com/dashboard", wait_until="domcontentloaded")
        if _vercel_logged_in(page):
            return
        page.wait_for_timeout(2000)
    raise TimeoutError("Vercel login timed out")


def create_github_repo(page: Page, repo_name: str) -> str:
    page.goto("https://github.com/new", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    name_input = page.locator('input[name="repository[name]"]').first
    if name_input.count() == 0:
        name_input = page.get_by_label("Repository name")
    name_input.fill(repo_name)

    # Do not initialize with README (we already have commits)
    for label in ["Add a README file", "Add README"]:
        box = page.get_by_label(label)
        if box.count() and box.is_checked():
            box.uncheck()

    create_btn = page.get_by_role("button", name=re.compile(r"Create repository", re.I))
    create_btn.click()

    try:
        page.wait_for_url(
            re.compile(rf"github\.com/[^/]+/{re.escape(repo_name)}"),
            timeout=30_000,
        )
    except Exception:
        # Repo may already exist — open it
        log("Create may have failed (existing repo?) - opening repository page")
        page.goto(f"https://github.com/{repo_name}", wait_until="domcontentloaded")
        if page.locator('text=404').count():
            user = page.locator('meta[name="user-login"]').first.get_attribute("content")
            if user:
                page.goto(f"https://github.com/{user}/{repo_name}", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

    clone_https = page.locator('input[data-testid="clone-url-input"], #repo-clone-url').first
    if clone_https.count():
        url = clone_https.input_value().strip()
    else:
        # fallback: parse from page
        m = re.search(r"github\.com/([^/]+)/([^/]+)", page.url)
        if not m:
            raise RuntimeError("Could not determine GitHub repo URL")
        url = f"https://github.com/{m.group(1)}/{m.group(2)}.git"

    if not url.endswith(".git"):
        url += ".git"
    log(f"GitHub repo ready: {url}")
    return url


def git_push(remote_url: str) -> None:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    push_url = remote_url
    if token:
        push_url = re.sub(r"https://", f"https://{token}@", remote_url, count=1)

    git("remote", "remove", "origin")
    r = git("remote", "add", "origin", push_url)
    if r.returncode != 0:
        raise RuntimeError(f"git remote add failed: {r.stderr}")

    r = git("push", "-u", "origin", "main")
    if r.returncode != 0:
        raise RuntimeError(
            f"git push failed: {r.stderr}\n"
            "Set GITHUB_TOKEN or sign in with Git Credential Manager."
        )
    log("git push to origin/main OK")


def vercel_import_project(page: Page, repo_name: str) -> None:
    page.goto("https://vercel.com/new", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Search/import Git repo
    search = page.locator('input[placeholder*="Search"], input[placeholder*="repository"]').first
    if search.count():
        search.fill(repo_name)
        page.wait_for_timeout(2000)

    repo_row = page.locator(f'text="{repo_name}"').first
    if repo_row.count() == 0:
        repo_row = page.get_by_text(repo_name, exact=True).first
    repo_row.click(timeout=30_000)

    import_btn = page.get_by_role("button", name=re.compile(r"Import|Deploy", re.I))
    if import_btn.count():
        import_btn.first.click()
    page.wait_for_timeout(2000)

    # Root Directory -> frontend
    root_input = page.locator(
        'input[name="rootDirectory"], input[placeholder*="root"], input[aria-label*="Root"]'
    ).first
    if root_input.count() == 0:
        edit_link = page.get_by_text(re.compile(r"Root Directory|Edit", re.I))
        if edit_link.count():
            edit_link.first.click()
            page.wait_for_timeout(500)
            root_input = page.locator("input").filter(has_text=re.compile("")).first

    if root_input.count():
        root_input.fill(FRONTEND_ROOT)
        page.keyboard.press("Enter")
        page.wait_for_timeout(800)

    # Optional env hint (placeholder for local API)
    env_key = page.locator('input[name*="key"], input[placeholder*="KEY"]').first
    if env_key.count() and os.environ.get("NEXT_PUBLIC_API_URL"):
        env_key.fill("NEXT_PUBLIC_API_URL")
        val = page.locator('input[name*="value"], input[placeholder*="VALUE"]').first
        if val.count():
            val.fill(os.environ["NEXT_PUBLIC_API_URL"])

    deploy = page.get_by_role("button", name=re.compile(r"Deploy", re.I))
    deploy.last.click(timeout=30_000)
    log("Vercel Deploy clicked - wait for build on dashboard")

    page.wait_for_timeout(5000)
    if page.locator('text=Congratulations').count() or page.locator('text=Building').count():
        log("Vercel deployment started")
    else:
        log("Check Vercel dashboard for deployment status")


def run() -> int:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    headless = os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=80)

        # --- GitHub ---
        gh_ctx = browser.new_context(storage_state=str(GITHUB_STATE) if GITHUB_STATE.exists() else None)
        gh_page = gh_ctx.new_page()
        try:
            wait_for_github_login(gh_page)
            remote_url = create_github_repo(gh_page, REPO_NAME)
            gh_ctx.storage_state(path=str(GITHUB_STATE))
        except Exception:
            gh_page.screenshot(path=str(SCRIPT_DIR / "github_error.png"))
            raise
        finally:
            gh_ctx.close()

        git_push(remote_url)

        # --- Vercel ---
        vc_ctx = browser.new_context(storage_state=str(VERCEL_STATE) if VERCEL_STATE.exists() else None)
        vc_page = vc_ctx.new_page()
        try:
            wait_for_vercel_login(vc_page)
            vercel_import_project(vc_page, REPO_NAME)
            vc_ctx.storage_state(path=str(VERCEL_STATE))
            vc_page.screenshot(path=str(SCRIPT_DIR / "vercel_done.png"))
        except Exception:
            vc_page.screenshot(path=str(SCRIPT_DIR / "vercel_error.png"))
            raise
        finally:
            vc_ctx.close()

        browser.close()

    log("Done.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        log(f"FAILED: {e}")
        sys.exit(1)
