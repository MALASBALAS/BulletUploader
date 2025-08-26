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
        # If not logged in at all, perform login via web flow.
        if not self.is_logged_in():
            try:
                subprocess.run(["gh", "auth", "login", "-h", "github.com", "--web"], check=True)
                return True
            except Exception:
                return False

        # Already logged in
        if not username:
            return True
        current = self.get_current_user()
        if current == username:
            return True
        # Different user selected; trigger login switch (only called from explicit UI action)
        try:
            subprocess.run(["gh", "auth", "login", "-h", "github.com", "--web"], check=True)
            # After login, verify user (best effort)
            return True
        except Exception:
            return False
