# deploy_assist.py

import os
import sys
from utils.project_detector import detect_project_type
from utils.test_runner import run_tests
from utils.git_manager import GitManager
from utils.github_client import GitHubClient
from utils.security_checker import check_for_secrets

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def main():
    console.print("[bold blue]\n🚀 Deploy Assist: Automatizador de subidas a GitHub[/bold blue]\n")

    # Paso 1: Ruta del proyecto
    path = Prompt.ask("📁 Ruta del proyecto", default=os.getcwd())
    if not os.path.isdir(path):
        console.print("[bold red]❌ Ruta inválida.[/bold red]")
        sys.exit(1)
    os.chdir(path)

    # Paso 2: Detección de entorno y tests
    project_type = detect_project_type(path)
    console.print(f"🔍 Proyecto detectado: [green]{project_type}[/green]")

    if Confirm.ask("¿Ejecutar tests automáticamente?"):
        if not run_tests(project_type):
            console.print("[bold red]❌ Tests fallaron. Abortando subida.[/bold red]")
            sys.exit(1)

    # Paso 3: Verificar secretos
    if not check_for_secrets(path):
        console.print("[bold red]\n❌ Se detectaron posibles secretos.[/bold red]")
        if not Confirm.ask("¿Continuar de todas formas? (solo si estás seguro de que son falsos positivos)"):
            console.print("[bold yellow]Operación cancelada por el usuario.[/bold yellow]")
            sys.exit(1)

    # Paso 4: Inicializar git manager y GitHub
    git = GitManager()
    gh = GitHubClient()

    # Paso 5: Seleccionar repositorio
    repo = gh.select_repo()
    branch_type = Prompt.ask("🌿 Tipo de rama", choices=["feature", "bugfix", "hotfix", "update"])
    branch_name = Prompt.ask("🆕 Nombre de la rama")
    full_branch = f"{branch_type}/{branch_name}"

    git.create_branch(full_branch)
    git.add_all_changes()
    commit_msg = Prompt.ask("📝 Mensaje del commit")
    git.commit(commit_msg)
    git.push(full_branch)

    # Paso 6: Crear Pull Request
    if Confirm.ask("¿Crear Pull Request automáticamente?"):
        pr_title = Prompt.ask("📋 Título del PR")
        pr_body = Prompt.ask("🗒️ Descripción del PR")
        gh.create_pr(repo, full_branch, pr_title, pr_body)

    console.print("\n[bold green]✅ Subida completada exitosamente.[/bold green]")

if __name__ == "__main__":
    main()
