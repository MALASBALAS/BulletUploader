# main_gui.py

import os
import subprocess
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from utils.project_detector import detect_project_type
from utils.test_runner import run_tests
from utils.git_manager import GitManager
from utils.github_client import GitHubClient
from utils.account_manager import AccountManager
from utils.security_checker import check_for_secrets

# Colores inspirados en Jarvis (Iron Man)
JARVIS_BG = "#0A192F"
JARVIS_PANEL = "#112240"
JARVIS_ACCENT = "#64FFDA"
JARVIS_ACCENT2 = "#00BFAE"
JARVIS_ERROR = "#FF5370"
JARVIS_SUCCESS = "#21C7A8"
JARVIS_TEXT = "#CCD6F6"
JARVIS_TEXT2 = "#8892B0"
FONT = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")

class BulletUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 JarvisUploader GUI")
        self.root.configure(bg=JARVIS_BG)
        self.path = ""
        self.repo_name = ""
        self.repo_options = []
        self.gh = GitHubClient()
        self.account_mgr = AccountManager()
        self.account_var = tk.StringVar()
        self.accounts = []

        self.setup_ui()
        self.load_repos()  # <-- Cargar repos automáticamente al iniciar

    def style_widget(self, widget, bg=JARVIS_BG, fg=JARVIS_TEXT, font=FONT):
        widget.configure(bg=bg, fg=fg, font=font, highlightthickness=0, bd=0)

    def setup_ui(self):
        self.commit_category = tk.StringVar(value="feat")
        self.commit_ref = tk.StringVar()
        self.commit_desc = tk.StringVar()
        self.commit_message = tk.StringVar()
        self.add_to_changelog = tk.BooleanVar()
        self.branch_type = tk.StringVar(value="feature")
        self.repo_var = tk.StringVar()
        self.clean_folders = tk.BooleanVar(value=True)

        # --- Cuenta GitHub ---
        acct_frame = tk.LabelFrame(self.root, text="Cuenta GitHub", padx=12, pady=8, bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD)
        acct_frame.pack(padx=12, pady=(12, 0), fill="x")

        tk.Label(acct_frame, text="Selecciona cuenta:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.account_menu = tk.OptionMenu(acct_frame, self.account_var, "")
        self.account_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        self.account_menu["menu"].config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        self.account_menu.grid(row=0, column=1, sticky="w")
        tk.Button(acct_frame, text="Añadir", command=self.add_account, bg=JARVIS_ACCENT, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2).grid(row=0, column=2, padx=4)
        tk.Button(acct_frame, text="Eliminar", command=self.remove_account, bg="#FF5C5C", fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2).grid(row=0, column=3, padx=4)
        tk.Button(acct_frame, text="Iniciar sesión", command=self.login_selected_account, bg=JARVIS_ACCENT2, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT).grid(row=0, column=4, padx=4)

        # cargar cuentas en el menú
        self.load_accounts()

        # --- Main Frame ---
        frame = tk.LabelFrame(self.root, text="Configuración de Proyecto", padx=12, pady=12, bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD)
        frame.pack(padx=12, pady=12, fill="x")

        # Ruta del Proyecto
        tk.Label(frame, text="Ruta del Proyecto:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.entry_path = tk.Entry(frame, width=50, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        self.entry_path.grid(row=0, column=1, padx=5)
        tk.Button(frame, text="📁", command=self.browse_folder, bg=JARVIS_ACCENT, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2).grid(row=0, column=2)
        tk.Label(frame, text="Selecciona la carpeta de tu proyecto", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w")

        # Tipo de Proyecto
        tk.Label(frame, text="Tipo de Proyecto:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=2, column=0, sticky="w")
        self.label_project = tk.Label(frame, text="Desconocido", fg=JARVIS_ACCENT2, bg=JARVIS_PANEL, font=FONT_BOLD)
        self.label_project.grid(row=2, column=1, sticky="w")
        tk.Button(frame, text="Detectar y Testear", command=self.detect_and_test, bg=JARVIS_ACCENT2, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT).grid(row=2, column=2, pady=2)

        # Repositorio GitHub
        tk.Label(frame, text="Repositorio GitHub:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=3, column=0, sticky="w")
        self.repo_menu = tk.OptionMenu(frame, self.repo_var, "")
        self.repo_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        self.repo_menu["menu"].config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        self.repo_menu.grid(row=3, column=1, sticky="w")
        tk.Button(frame, text="Cargar Repos", command=self.load_repos, bg=JARVIS_ACCENT, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2).grid(row=3, column=2)

        # Tipo de Rama (mostrar significado entre paréntesis)
        tk.Label(frame, text="Tipo de Rama:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=4, column=0, sticky="w")
        branch_types = {
            "feature": "feature (nueva funcionalidad)",
            "bugfix": "bugfix (corrección de error)",
            "hotfix": "hotfix (urgente en producción)",
            "update": "update (mantenimiento/actualización)",
        }
        branch_menu = tk.OptionMenu(frame, self.branch_type, *branch_types.keys())
        branch_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        bmenu = branch_menu["menu"]
        bmenu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        bmenu.delete(0, "end")
        for value, label in branch_types.items():
            bmenu.add_command(label=label, command=lambda v=value: self.branch_type.set(v))
        branch_menu.grid(row=4, column=1, sticky="w")
        tk.Label(
            frame,
            text="feature (nueva), bugfix (corrige bug), hotfix (urgente prod), update (mantenimiento)",
            bg=JARVIS_PANEL,
            fg=JARVIS_TEXT2,
            font=("Segoe UI", 9)
        ).grid(row=5, column=1, sticky="w")

        # Nombre de la Rama
        tk.Label(frame, text="Nombre de la Rama:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=6, column=0, sticky="w")
        self.entry_branch_name = tk.Entry(frame, width=30, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        self.entry_branch_name.grid(row=6, column=1, sticky="w")
        tk.Label(frame, text="Describe brevemente (sin espacios). Ejemplo: loginwindow (puedes dejarlo vacío)", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=7, column=1, sticky="w")

        # Tipo Commit (mostrar significado entre paréntesis)
        tk.Label(frame, text="Tipo Commit:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=8, column=0, sticky="w")
        commit_types = {
            "feat": "feat (nueva funcionalidad)",
            "fix": "fix (corrección de errores)",
            "refactor": "refactor (mejoras internas sin cambiar comportamiento)",
            "chore": "chore (tareas de mantenimiento y build)",
            "test": "test (añadir o actualizar pruebas)",
        }
        commit_menu = tk.OptionMenu(frame, self.commit_category, *commit_types.keys())
        commit_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        menu = commit_menu["menu"]
        menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        menu.delete(0, "end")
        for value, label in commit_types.items():
            menu.add_command(label=label, command=lambda v=value: self.commit_category.set(v))
        commit_menu.grid(row=8, column=1, sticky="w")
        tk.Label(
            frame,
            text="Selecciona el tipo de cambio: feat (nueva funcionalidad), fix (bug), refactor, chore, test",
            bg=JARVIS_PANEL,
            fg=JARVIS_TEXT2,
            font=("Segoe UI", 9)
        ).grid(row=9, column=1, sticky="w")

        # ID Referencia
        tk.Label(frame, text="ID Referencia:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=10, column=0, sticky="w")
        entry_ref = tk.Entry(frame, textvariable=self.commit_ref, width=30, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        entry_ref.grid(row=10, column=1, sticky="w")
        tk.Label(frame, text="ID del ticket o referencia. Ejemplo: FB-001", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=11, column=1, sticky="w")

        # Descripción rama
        tk.Label(frame, text="Descripción rama:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=12, column=0, sticky="w")
        entry_desc = tk.Entry(frame, textvariable=self.commit_desc, width=30, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        entry_desc.grid(row=12, column=1, sticky="w")
        tk.Label(frame, text="Descripción en kebab-case. Ejemplo: añadir-ventana-login", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=13, column=1, sticky="w")

        # Mensaje Commit
        tk.Label(frame, text="Mensaje Commit:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=14, column=0, sticky="w")
        entry_msg = tk.Entry(frame, textvariable=self.commit_message, width=50, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        entry_msg.grid(row=14, column=1, sticky="w")
        tk.Label(frame, text="Descripción clara del cambio. Ejemplo: Add login window with validation", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=15, column=1, sticky="w")

        # Añadir al changelog y limpieza
        tk.Checkbutton(frame, text="➕ Añadir al changelog", variable=self.add_to_changelog, bg=JARVIS_PANEL, fg=JARVIS_ACCENT2, font=FONT).grid(row=16, column=1, sticky="w")
        tk.Checkbutton(frame, text="Eliminar carpetas indeseadas (.git, __pycache__, etc.)", variable=self.clean_folders, bg=JARVIS_PANEL, fg=JARVIS_ACCENT2, font=FONT).grid(row=17, column=1, sticky="w")

        # --- Botones de acción ---
        action_frame = tk.Frame(self.root, bg=JARVIS_BG)
        action_frame.pack(padx=12, pady=5, fill="x")

        btn_deploy = tk.Button(action_frame, text="🚀 Subir y Crear PR", bg=JARVIS_ACCENT, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.deploy)
        btn_deploy.pack(side="left", padx=5)

        btn_push = tk.Button(action_frame, text="📤 Hacer Push Manual", bg=JARVIS_ACCENT2, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT, command=self.push_current_branch)
        btn_push.pack(side="left", padx=5)

        self.btn_initial = tk.Button(action_frame, text="📦 Subida inicial", bg="#2EA043", fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.initial_upload)
        self.btn_initial.pack(side="left", padx=5)

        btn_clear = tk.Button(action_frame, text="🧹 Limpiar Log", bg="#233554", fg=JARVIS_TEXT2, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.clear_log)
        btn_clear.pack(side="right", padx=5)

        btn_info = tk.Button(action_frame, text="ℹ️ Info", bg="#233554", fg=JARVIS_ACCENT2, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.show_modified_files)
        btn_info.pack(side="right", padx=5)

        # --- Log ---
        log_frame = tk.LabelFrame(self.root, text="Log", padx=10, pady=5, bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD)
        log_frame.pack(padx=12, pady=5, fill="both", expand=True)
        self.log = ScrolledText(log_frame, height=10, bg="#172A45", fg=JARVIS_TEXT, font=("Consolas", 11), insertbackground=JARVIS_TEXT, borderwidth=0, highlightthickness=0)
        self.log.pack(fill="both", expand=True)

    # Repos se cargan bajo sesión de gh (gh auth login)

    def load_accounts(self):
        try:
            self.accounts = self.account_mgr.list_accounts()
            menu = self.account_menu["menu"]
            menu.delete(0, "end")
            if not self.accounts:
                # placeholder
                self.account_var.set("")
                menu.add_command(label="(sin cuentas)", command=lambda: None)
            else:
                for acct in self.accounts:
                    label = acct.get("name") or acct.get("username") or "(sin nombre)"
                    menu.add_command(label=label, command=lambda v=label: self.account_var.set(v))
                # set default
                self.account_var.set(self.accounts[0].get("name") or self.accounts[0].get("username") or "")
        except Exception as e:
            try:
                self.log.insert(tk.END, f"⚠️ Error cargando cuentas: {e}\n")
            except Exception:
                pass

    def add_account(self):
        alias = simpledialog.askstring("Nueva cuenta", "Alias de la cuenta (por ejemplo: personal, trabajo):", parent=self.root)
        if not alias:
            return
        username = simpledialog.askstring("Usuario GitHub", "Nombre de usuario de GitHub (opcional, para iniciar sesión/switch):", parent=self.root)
        self.account_mgr.add(alias, username=username if username else None)
        self.load_accounts()

    def remove_account(self):
        sel = self.account_var.get()
        if not sel:
            return
        self.account_mgr.remove(sel)
        self.load_accounts()

    def login_selected_account(self):
        sel = self.account_var.get()
        if not sel:
            messagebox.showinfo("Cuenta", "Primero añade o selecciona una cuenta")
            return
        username = self.account_mgr.get_username(sel) or sel
        ok = self.gh.ensure_login_for_user(username)
        if ok:
            self.log.insert(tk.END, f"✅ Sesión activa con: {username}\n")
            # refrescar repos cuando hay login
            self.load_repos()
        else:
            self.log.insert(tk.END, f"❌ No se pudo iniciar sesión/switch con: {username}\n")

    def clear_log(self):
        self.log.delete(1.0, tk.END)

    def browse_folder(self):
        self.path = filedialog.askdirectory()
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, self.path)

    def detect_and_test(self):
        path = self.entry_path.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Ruta no válida")
            return
            
        self.label_project.config(text="Detectando...", fg=JARVIS_ACCENT2)
        
        # Cambiar al directorio del proyecto
        original_cwd = os.getcwd()
        try:
            os.chdir(path)
            tipo = detect_project_type(path)
            self.label_project.config(text=tipo, fg=JARVIS_SUCCESS if tipo != "Desconocido" else JARVIS_ERROR)

            self.log.insert(tk.END, f"🔍 Proyecto detectado: {tipo}\n")
            
            # Verificar pytest solo para proyectos Python
            if tipo == "Python":
                try:
                    import pytest
                except ImportError:
                    self.log.insert(tk.END, "⚠️ El módulo 'pytest' no está instalado. Instálalo con: pip install pytest\n")
                    return

            test_result = run_tests(tipo)
            if test_result is None:
                self.log.insert(tk.END, "⚠️ No se pudieron ejecutar tests (herramientas faltantes o no configuradas)\n")
            elif test_result == 0:
                self.log.insert(tk.END, "⚠️ Se encontraron 0 tests\n")
            elif not test_result:
                self.log.insert(tk.END, "❌ Tests fallaron\n")
            else:
                self.log.insert(tk.END, "✅ Tests pasaron\n")
                
        finally:
            os.chdir(original_cwd)

    def load_repos(self):
        try:
            # Usar sesión de gh (gh auth login)
            self.gh = GitHubClient()
            # No forzar login aquí para evitar prompts repetidos
            self.repo_options = self.gh.list_repos()
        except FileNotFoundError:
            self.repo_options = []
            self.log.insert(tk.END, "⚠️ GitHub CLI 'gh' no está instalado o no está en el PATH.\n")
        if self.repo_options:
            menu = self.repo_menu["menu"]
            menu.delete(0, "end")
            for repo in self.repo_options:
                menu.add_command(label=repo, command=lambda value=repo: self.repo_var.set(value))
            self.repo_var.set(self.repo_options[0])
            self.log.insert(tk.END, "📦 Repositorios cargados\n")
        else:
            # Indicar el usuario actual si existe
            current = self.gh.get_current_user()
            if current:
                self.log.insert(tk.END, f"ℹ️ No se encontraron repos visibles para {current} o no hay permisos.\n")
            else:
                self.log.insert(tk.END, "ℹ️ No se pudieron cargar repos. Asegúrate de tener 'gh' instalado y autenticado.\n")

    # Eliminado: gestión de cuentas por PAT; se usa gh auth login

    def ensure_git_initialized(self, path):
        """Inicializa git si no existe y maneja errores correctamente"""
        git_dir = os.path.join(path, ".git")
        
        # Verificar si git está disponible
        if not shutil.which("git"):
            self.log.insert(tk.END, "❌ Git no está instalado o no está en el PATH\n")
            return False
            
        try:
            # Si no existe .git, inicializar
            if not os.path.exists(git_dir):
                result = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log.insert(tk.END, f"❌ Error al inicializar git: {result.stderr}\n")
                    return False
                self.log.insert(tk.END, "✅ Git inicializado\n")

            # Verificar si hay commits
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                cwd=path, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                # No hay commits, hacer commit inicial
                subprocess.run(["git", "add", "."], cwd=path, check=True)
                
                # Verificar si hay algo que commitear
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"], 
                    cwd=path, 
                    capture_output=True, 
                    text=True
                )
                
                if status_result.stdout.strip():
                    subprocess.run(
                        ["git", "commit", "-m", "Initial commit"], 
                        cwd=path, 
                        check=True
                    )
                    self.log.insert(tk.END, "✅ Commit inicial creado\n")
                else:
                    self.log.insert(tk.END, "⚠️ No hay archivos para commitear\n")
                    
            return True
            
        except subprocess.CalledProcessError as e:
            self.log.insert(tk.END, f"❌ Error en git: {e}\n")
            return False
        except Exception as e:
            self.log.insert(tk.END, f"❌ Error inesperado: {e}\n")
            return False

    def _parse_owner_repo_from_url(self, url: str) -> str | None:
        try:
            if not url:
                return None
            # Examples:
            # https://github.com/OWNER/REPO.git
            # git@github.com:OWNER/REPO.git
            # ssh://git@github.com/OWNER/REPO.git
            if "github.com" not in url:
                return None
            # Normalize separators
            part = url.split("github.com", 1)[1]
            if part.startswith(":") or part.startswith("/"):
                part = part[1:]
            # Remove protocol residue and .git
            part = part.replace(".git", "")
            # The remaining should start with OWNER/REPO
            owner_repo = part.split("/", 2)[:2]
            if len(owner_repo) < 2:
                return None
            return f"{owner_repo[0]}/{owner_repo[1]}"
        except Exception:
            return None

    def _get_origin_repo(self, path: str) -> str | None:
        try:
            res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=path, capture_output=True, text=True)
            if res.returncode != 0:
                return None
            url = (res.stdout or "").strip()
            return self._parse_owner_repo_from_url(url)
        except Exception:
            return None

    def deploy(self):
        def remote_exists():
            result = subprocess.run(["git", "remote"], cwd=path, capture_output=True, text=True)
            return "origin" in result.stdout
            
        path = self.entry_path.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Ruta no válida")
            return
            
        if not check_for_secrets(path, clean_folders=self.clean_folders.get()):
            messagebox.showerror("Seguridad", "Secretos encontrados en el proyecto")
            return
        tipo = self.branch_type.get()
        nombre = self.entry_branch_name.get()
        referencia = self.commit_ref.get().strip()
        desc = self.commit_desc.get().strip().replace(" ", "-")
        rama = f"{tipo}/{referencia}/{desc}"
        mensaje_final = self.commit_message.get().strip()
        categoria = self.commit_category.get()
        mensaje = f"{categoria}: {referencia} {mensaje_final}"
        # Determinar repo de destino: priorizar 'origin' si existe, para evitar PRs en repo equivocado
        origin_repo = self._get_origin_repo(path)
        selected_repo = self.repo_var.get().strip()
        self.repo_name = origin_repo or selected_repo
        if origin_repo and selected_repo and origin_repo != selected_repo:
            self.log.insert(tk.END, f"ℹ️ El remote 'origin' apunta a {origin_repo}. Usaré este repo para el PR (ignorando selección '{selected_repo}').\n")
        if not self.repo_name:
            messagebox.showerror("Repositorio", "No se pudo determinar el repositorio destino. Configura un remote 'origin' o selecciona uno en el desplegable.")
            return

        if not self.ensure_git_initialized(path):
            messagebox.showerror("Error", "No se pudo inicializar el repositorio git.")
            return

        if not remote_exists():
            repo_url = f"https://github.com/{self.repo_name}.git"
            try:
                subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=path, check=True)
                self.log.insert(tk.END, f"🔗 Remote agregado: {repo_url}\n")
            except subprocess.CalledProcessError as e:
                self.log.insert(tk.END, f"❌ Error agregando remote: {e}\n")
                return

        # Cambiar al directorio del proyecto para las operaciones git
        original_cwd = os.getcwd()
        try:
            os.chdir(path)
            git = GitManager()

            try:
                subprocess.run(["git", "checkout", rama], check=True)
                self.log.insert(tk.END, f"🔁 Rama existente detectada, cambiando a: {rama}\n")
            except subprocess.CalledProcessError:
                git.create_branch(rama)
                self.log.insert(tk.END, f"🌱 Rama creada: {rama}\n")
                
            git.add_all_changes()
            git.commit(mensaje)
            git.push(rama)
            try:
                self.gh.create_pr(self.repo_name, rama, f"{referencia}: {mensaje_final}", f"issue: link-to-jira{mensaje}\n")
                subprocess.run(["gh", "pr", "view", "--repo", self.repo_name, "--web"])
                self.log.insert(tk.END, "✅ PR creado correctamente\n")
            except subprocess.CalledProcessError as e:
                # Mensaje más claro cuando no hay diferencia o base inválida
                self.log.insert(tk.END, f"❌ No se pudo crear el PR: {e}. Verifica que la rama base exista y que haya commits distintos entre '{rama}' y la base.\n")
            
            if self.add_to_changelog.get():
                try:
                    changelog_path = os.path.join(path, "CHANGELOG.md")
                    if not os.path.exists(changelog_path):
                        with open(changelog_path, "w", encoding="utf-8") as f:
                            f.write("# Changelog\n\n")

                    with open(changelog_path, "a", encoding="utf-8") as changelog:
                        changelog.write(f"\n### {referencia} - {mensaje_final}\n- {mensaje}\n")
                    self.log.insert(tk.END, "📝 Añadido al changelog\n")
                except Exception as ce:
                    self.log.insert(tk.END, f"⚠️ Error al actualizar changelog: {ce}\n")
                    
        except Exception as e:
            self.log.insert(tk.END, f"❌ Error: {str(e)}\n")
        finally:
            os.chdir(original_cwd)

    def push_current_branch(self):
        path = self.entry_path.get()
        try:
            subprocess.run(["git", "push"], cwd=path, check=True)
            self.log.insert(tk.END, "✅ Push realizado con éxito\n")
        except subprocess.CalledProcessError as e:
            self.log.insert(tk.END, f"❌ Error al hacer push: {e}\n")

    def initial_upload(self):
        """Subida inicial con comprobaciones, conteo de archivos y progreso por porcentaje."""
        if hasattr(self, "btn_initial"):
            self.btn_initial.configure(state="disabled")
        threading.Thread(target=self._initial_upload_task, daemon=True).start()

    def show_modified_files(self):
        path = self.entry_path.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Ruta no válida")
            return
        try:
            # Solo archivos modificados (no añadidos al commit)
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().splitlines()
            if not lines:
                self.log.insert(tk.END, "ℹ️ No hay archivos modificados sin commitear.\n")
                return
            self.log.insert(tk.END, "📝 Archivos modificados:\n")
            for line in lines:
                status, file = line[:2], line[3:]
                self.log.insert(tk.END, f"  {status.strip()} {file}\n")
        except Exception as e:
            self.log.insert(tk.END, f"❌ Error al obtener archivos modificados: {e}\n")

    # --- Helpers de subida inicial ---
    def _log(self, msg: str):
        print(msg, end="")
        self.log.insert(tk.END, msg)
        self.log.see(tk.END)

    def _run(self, args, cwd=None, check=True, capture=False):
        try:
            res = subprocess.run(args, cwd=cwd, text=True, check=check,
                                 capture_output=capture)
            return res
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Error ejecutando: {' '.join(args)}\n{e}\n")
            raise

    def _git_remote_exists(self, path: str) -> bool:
        try:
            res = self._run(["git", "remote"], cwd=path, capture=True)
            remotes = (res.stdout or "").split()
            return "origin" in remotes
        except Exception:
            return False

    def _list_files_to_commit(self, path: str):
        # Untracked
        res_u = self._run(["git", "ls-files", "-o", "--exclude-standard"], cwd=path, capture=True)
        untracked = [l for l in (res_u.stdout or "").splitlines() if l.strip()]
        # Modified
        res_m = self._run(["git", "ls-files", "-m"], cwd=path, capture=True)
        modified = [l for l in (res_m.stdout or "").splitlines() if l.strip()]
        files = list(dict.fromkeys(untracked + modified))
        files = [f for f in files if not f.startswith('.git/')]
        return files

    def _list_staged_files(self, path: str):
        """List files currently staged for commit."""
        res = self._run(["git", "diff", "--cached", "--name-only"], cwd=path, capture=True)
        staged = [l for l in (res.stdout or "").splitlines() if l.strip()]
        return staged

    def _initial_upload_task(self):
        try:
            path = self.entry_path.get().strip()
            if not os.path.isdir(path):
                messagebox.showerror("Error", "Ruta no válida")
                return

            if not shutil.which("git"):
                messagebox.showerror("Error", "Git no está instalado o no está en el PATH")
                return

            if not self.repo_var.get():
                messagebox.showerror("Error", "Selecciona un repositorio de GitHub en el desplegable")
                return

            self._log("\n🚀 Iniciando subida inicial...\n")

            # Secret scan
            ok = check_for_secrets(path, clean_folders=self.clean_folders.get())
            if not ok:
                if not messagebox.askyesno("Seguridad", "Se detectaron posibles secretos. ¿Continuar igualmente?"):
                    self._log("Operación cancelada por hallazgo de secretos.\n")
                    return

            # Asegurar repositorio válido y rama main
            if not self._ensure_valid_git_repo(path):
                return

            # Remote origin
            if not self._git_remote_exists(path):
                repo_url = f"https://github.com/{self.repo_var.get()}.git"
                self._run(["git", "remote", "add", "origin", repo_url], cwd=path)
                self._log(f"🔗 Remote agregado: {repo_url}\n")

            # Archivos a subir
            files = self._list_files_to_commit(path)
            total = len(files)
            self._log(f"📦 Archivos a subir: {total}\n")
            if total == 0:
                # Intentar detectar cambios tras add -A (p.ej. primer commit)
                self._run(["git", "add", "-A"], cwd=path)
                staged = self._list_staged_files(path)
                total = len(staged)
                self._log(f"📦 Archivos detectados tras 'git add -A': {total}\n")
                if total == 0:
                    self._log("Nada que subir.\n")
                    return
                # Registrar progreso sobre los ya staged (sin re-añadir)
                for i, f in enumerate(staged, start=1):
                    pct = (i / total) * 100
                    self._log(f"Progreso: {pct:.1f}% ({i}/{total}) -> {f}\n")

            # Añadir con progreso
            if total > 0 and 'files' in locals() and files:
                for i, f in enumerate(files, start=1):
                    self._run(["git", "add", "--", f], cwd=path)
                    pct = (i / total) * 100
                    self._log(f"Progreso: {pct:.1f}% ({i}/{total}) -> {f}\n")

            # Commit si hay staged
            res = self._run(["git", "status", "--porcelain"], cwd=path, capture=True)
            if not (res.stdout or "").strip():
                self._log("ℹ️ No hay cambios para commitear.\n")
                return

            mensaje_final = (self.commit_message.get() or "subida inicial").strip()
            categoria = (self.commit_category.get() or "chore").strip()
            mensaje = f"{categoria}: {mensaje_final}"
            self._run(["git", "commit", "-m", mensaje], cwd=path)
            self._log(f"📝 Commit creado: {mensaje}\n")

            # Push
            self._log("⬆️  Pushing a origin/main...\n")
            self._run(["git", "push", "-u", "origin", "main"], cwd=path)
            self._log("✅ Subida inicial completada.\n")

        except Exception as e:
            self._log(f"❌ Error en subida inicial: {e}\n")
        finally:
            if hasattr(self, "btn_initial") and self.btn_initial:
                self.btn_initial.configure(state="normal")

    def _ensure_valid_git_repo(self, path: str) -> bool:
        """Comprueba si el directorio es un repo git válido; si no, intenta repararlo/reiniciarlo."""
        try:
            # ¿Estamos dentro de un repo válido?
            res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path, text=True, capture_output=True)
            inside = (res.returncode == 0 and (res.stdout or "").strip() == "true")
            if not inside:
                git_dir = os.path.join(path, ".git")
                if os.path.exists(git_dir):
                    # .git presente pero inválido -> pedir reparar
                    if not messagebox.askyesno("Repositorio corrupto", "Se detectó .git pero no es válido. ¿Reinicializar el repositorio?\n(Se eliminará la carpeta .git local)"):
                        self._log("Operación cancelada por el usuario.\n")
                        return False
                    try:
                        shutil.rmtree(git_dir, ignore_errors=True)
                        self._log("🧹 Carpeta .git eliminada.\n")
                    except Exception as e:
                        self._log(f"❌ No se pudo eliminar .git: {e}\n")
                        return False
                # Inicializar
                self._run(["git", "init"], cwd=path)
                self._log("✅ Git inicializado\n")

            # Asegurar main
            self._run(["git", "checkout", "-B", "main"], cwd=path)
            self._log("🌿 Rama objetivo: main\n")
            return True
        except Exception as e:
            self._log(f"❌ Error preparando el repositorio: {e}\n")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = BulletUploader(root)
    root.mainloop()
