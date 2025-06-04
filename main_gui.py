# main_gui.py

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from utils.project_detector import detect_project_type
from utils.test_runner import run_tests
from utils.git_manager import GitManager
from utils.github_client import GitHubClient
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

        # Tipo de Rama
        tk.Label(frame, text="Tipo de Rama:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=4, column=0, sticky="w")
        branch_menu = tk.OptionMenu(frame, self.branch_type, "feature", "bugfix", "hotfix", "update")
        branch_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        branch_menu["menu"].config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        branch_menu.grid(row=4, column=1, sticky="w")
        tk.Label(frame, text="Selecciona el tipo de trabajo. Ejemplo: feature (nueva funcionalidad)", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=5, column=1, sticky="w")

        # Nombre de la Rama
        tk.Label(frame, text="Nombre de la Rama:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=6, column=0, sticky="w")
        self.entry_branch_name = tk.Entry(frame, width=30, bg="#172A45", fg=JARVIS_TEXT, insertbackground=JARVIS_TEXT, font=FONT)
        self.entry_branch_name.grid(row=6, column=1, sticky="w")
        tk.Label(frame, text="Describe brevemente (sin espacios). Ejemplo: loginwindow (puedes dejarlo vacío)", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=7, column=1, sticky="w")

        # Tipo Commit
        tk.Label(frame, text="Tipo Commit:", bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD).grid(row=8, column=0, sticky="w")
        commit_menu = tk.OptionMenu(frame, self.commit_category, "feat", "fix", "refactor", "chore", "test")
        commit_menu.config(bg="#172A45", fg=JARVIS_TEXT, font=FONT, highlightthickness=0, bd=0, activebackground=JARVIS_ACCENT2)
        commit_menu["menu"].config(bg="#172A45", fg=JARVIS_TEXT, font=FONT)
        commit_menu.grid(row=8, column=1, sticky="w")
        tk.Label(frame, text="Tipo de cambio. Ejemplo: feat (funcionalidad), fix, chore...", bg=JARVIS_PANEL, fg=JARVIS_TEXT2, font=("Segoe UI", 9)).grid(row=9, column=1, sticky="w")

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

        # Añadir al changelog
        tk.Checkbutton(frame, text="➕ Añadir al changelog", variable=self.add_to_changelog, bg=JARVIS_PANEL, fg=JARVIS_ACCENT2, font=FONT).grid(row=16, column=1, sticky="w")
        tk.Checkbutton(
            frame,
            text="Eliminar carpetas indeseadas (.git, __pycache__, etc.)",
            variable=self.clean_folders,
            bg=JARVIS_PANEL,
            fg=JARVIS_ACCENT2,
            font=FONT
        ).grid(row=17, column=1, sticky="w")

        # --- Botones de acción ---
        action_frame = tk.Frame(self.root, bg=JARVIS_BG)
        action_frame.pack(padx=12, pady=5, fill="x")

        tk.Button(action_frame, text="🚀 Subir y Crear PR", bg=JARVIS_ACCENT, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.deploy).pack(side="left", padx=5)
        tk.Button(action_frame, text="📤 Hacer Push Manual", bg=JARVIS_ACCENT2, fg=JARVIS_BG, font=FONT_BOLD, activebackground=JARVIS_ACCENT, command=self.push_current_branch).pack(side="left", padx=5)
        tk.Button(action_frame, text="🧹 Limpiar Log", bg="#233554", fg=JARVIS_TEXT2, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.clear_log).pack(side="right", padx=5)
        tk.Button(action_frame, text="ℹ️ Info", bg="#233554", fg=JARVIS_ACCENT2, font=FONT_BOLD, activebackground=JARVIS_ACCENT2, command=self.show_modified_files).pack(side="right", padx=5)

        # --- Log ---
        log_frame = tk.LabelFrame(self.root, text="Log", padx=10, pady=5, bg=JARVIS_PANEL, fg=JARVIS_ACCENT, font=FONT_BOLD)
        log_frame.pack(padx=12, pady=5, fill="both", expand=True)
        self.log = ScrolledText(log_frame, height=10, bg="#172A45", fg=JARVIS_TEXT, font=("Consolas", 11), insertbackground=JARVIS_TEXT, borderwidth=0, highlightthickness=0)
        self.log.pack(fill="both", expand=True)

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
        tipo = detect_project_type(path)
        self.label_project.config(text=tipo, fg=JARVIS_SUCCESS if tipo != "Desconocido" else JARVIS_ERROR)

        self.log.insert(tk.END, f"🔍 Proyecto detectado: {tipo}\n")
        try:
            import pytest
        except ImportError:
            self.log.insert(tk.END, "⚠️ El módulo 'pytest' no está instalado. Instálalo con: pip install pytest\n")
            return

        test_result = run_tests(tipo)
        if test_result is None:
            self.log.insert(tk.END, "⚠️ No se encontraron tests para ejecutar\n")
        elif test_result == 0:
            self.log.insert(tk.END, "⚠️ Se encontraron 0 tests\n")
        elif not test_result:
            self.log.insert(tk.END, "❌ Tests fallaron\n")
        else:
            self.log.insert(tk.END, "✅ Tests pasaron\n")

    def load_repos(self):
        self.repo_options = self.gh.list_repos()
        if self.repo_options:
            menu = self.repo_menu["menu"]
            menu.delete(0, "end")
            for repo in self.repo_options:
                menu.add_command(label=repo, command=lambda value=repo: self.repo_var.set(value))
            self.repo_var.set(self.repo_options[0])
            self.log.insert(tk.END, "📦 Repositorios cargados\n")
        else:
            messagebox.showerror("Error", "No se encontraron repositorios o fallo en la carga.")

    def ensure_git_initialized(self, path):
        if not os.path.exists(os.path.join(path, ".git")):
            subprocess.run(["git", "init"], cwd=path, check=True)
            self.log.insert(tk.END, "✅ Git inicializado\n")

        try:
            subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path, check=True)
            self.log.insert(tk.END, "✅ Commit inicial creado\n")

    def deploy(self):
        def remote_exists():
            result = subprocess.run(["git", "remote"], cwd=path, capture_output=True, text=True)
            return "origin" in result.stdout
        path = self.entry_path.get()
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
        self.repo_name = self.repo_var.get()

        self.ensure_git_initialized(path)

        if not remote_exists():
            repo_url = f"https://github.com/{self.repo_name}.git"
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=path, check=True)
            self.log.insert(tk.END, f"✅ Remote agregado: {repo_url}\n")

        git = GitManager()

        try:
            try:
                subprocess.run(["git", "checkout", rama], cwd=path, check=True)
                self.log.insert(tk.END, f"🔁 Rama existente detectada, cambiando a: {rama}\n")
            except subprocess.CalledProcessError:
                git.create_branch(rama)
                self.log.insert(tk.END, f"🌱 Rama creada: {rama}\n")
            git.add_all_changes()
            git.commit(mensaje)
            git.push(rama)
            self.gh.create_pr(self.repo_name, rama, f"{referencia}: {mensaje_final}", f"issue: link-to-jira{mensaje}\n")
            subprocess.run(["gh", "pr", "view", "--web"], cwd=path)
            self.log.insert(tk.END, "✅ PR creado correctamente\n")
            if self.add_to_changelog.get():
                try:
                    changelog_path = os.path.join(self.path, "CHANGELOG.md")
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

    def push_current_branch(self):
        path = self.entry_path.get()
        try:
            subprocess.run(["git", "push"], cwd=path, check=True)
            self.log.insert(tk.END, "✅ Push realizado con éxito\n")
        except subprocess.CalledProcessError as e:
            self.log.insert(tk.END, f"❌ Error al hacer push: {e}\n")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = BulletUploader(root)
    root.mainloop()
