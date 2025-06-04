# github_client.py

import subprocess
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class GitHubClient:
    def select_repo(self):
        repos = self.list_repos()
        if not repos:
            console.print("[red]❌ No se encontraron repositorios. Asegúrate de estar autenticado con 'gh auth login'.[/red]")
            exit(1)
        for i, repo in enumerate(repos, 1):
            console.print(f"[{i}] {repo}")
        idx = int(Prompt.ask("📦 Elige el número del repo")) - 1
        return repos[idx]

    def create_pr(self, repo, branch, title, body):
        subprocess.run([
            "gh", "pr", "create",
            "--repo", repo,
            "--head", branch,
            "--base", "main",
            "--title", title,
            "--body", body
        ], check=True)

    def list_repos(self):
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
        except subprocess.CalledProcessError:
            return []
