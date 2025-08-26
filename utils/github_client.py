import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class GitHubClient:
    def __init__(self):
        pass

    def select_repo(self):
        repos = self.list_repos()
        if not repos:
            console.print("[red]❌ No se encontraron repositorios. Asegúrate de estar autenticado con 'gh auth login'.[/red]")
            exit(1)
        for i, repo in enumerate(repos, 1):
            console.print(f"[{i}] {repo}")
        idx = int(Prompt.ask("📦 Elige el número del repo")) - 1
        return repos[idx]

    def _get_default_branch(self, repo: str) -> str | None:
        try:
            res = subprocess.run(["gh", "repo", "view", repo, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"], capture_output=True, text=True, check=True)
            return (res.stdout or "").strip() or None
        except Exception:
            return None

    def create_pr(self, repo, branch, title, body, base: str | None = None):
        # Resolve base to repo default branch if not provided
        base_branch = base or self._get_default_branch(repo) or "main"
        args = [
            "gh", "pr", "create",
            "--repo", repo,
            "--head", branch,
            "--base", base_branch,
            "--title", title,
            "--body", body
        ]
        subprocess.run(args, check=True)

    def list_repos(self):
        # Usar gh CLI (requiere gh auth login)
        try:
            # Evitar prompts: si no hay sesión, devolver lista vacía
            if not self.is_logged_in():
                return []
            result = subprocess.run(
                ["gh", "repo", "list", "--json", "nameWithOwner", "--limit", "100"],
                capture_output=True,
                text=True,
                check=True
            )
            import json
            repos_json = json.loads(result.stdout)
            return [r["nameWithOwner"] for r in repos_json]
        except Exception:
            return []

    def get_current_user(self) -> str | None:
        try:
            res = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True, check=True)
            return (res.stdout or "").strip() or None
        except Exception:
            return None

    def is_logged_in(self, host: str = "github.com") -> bool:
        try:
            res = subprocess.run(["gh", "auth", "status", "-h", host], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def ensure_login_for_user(self, username: str | None) -> bool:
        """Ensure gh is logged in; if username provided and differs, open login to switch only on explicit action."""
        # Helper to setup git so pushes use gh credentials
        def _setup_git():
            try:
                subprocess.run(["gh", "auth", "setup-git"], check=True)
            except Exception:
                # Non-fatal; continue even if setup-git isn't available
                pass

        # If not logged in at all, perform login via web flow.
        if not self.is_logged_in():
            try:
                subprocess.run(["gh", "auth", "login", "-h", "github.com", "--web"], check=True)
                _setup_git()
                return True
            except Exception:
                return False

        # Already logged in
        if not username:
            _setup_git()
            return True
        current = self.get_current_user()
        if current == username:
            _setup_git()
            return True
        # Different user selected; try gh auth switch first, then fallback to login
        switched = False
        for args in (
            ["gh", "auth", "switch", "-u", username],
            ["gh", "auth", "switch", "--account", username],
        ):
            try:
                subprocess.run(args, check=True)
                switched = True
                break
            except Exception:
                continue
        if not switched:
            try:
                subprocess.run(["gh", "auth", "login", "-h", "github.com", "--web"], check=True)
                switched = True
            except Exception:
                return False
        if switched:
            _setup_git()
            return True
        return False
