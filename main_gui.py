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

class BulletUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("🔫 BulletUploader GUI")
        self.path = ""
        self.repo_name = ""
        self.repo_options = []

        self.gh = GitHubClient()

        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Ruta del Proyecto:").grid(row=0, column=0, sticky="w")
        self.entry_path = tk.Entry(frame, width=50)
        self.entry_path.grid(row=0, column=1, padx=5)
        tk.Button(frame, text="📁", command=self.browse_folder).grid(row=0, column=2)

        tk.Label(frame, text="Tipo de Proyecto:").grid(row=1, column=0, sticky="w")
        self.label_project = tk.Label(frame, text="Desconocido")
        self.label_project.grid(row=1, column=1, sticky="w")

        tk.Button(frame, text="Detectar y Testear", command=self.detect_and_test).grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Repositorio GitHub:").grid(row=3, column=0, sticky="w")
        self.repo_var = tk.StringVar()
        self.repo_menu = tk.OptionMenu(frame, self.repo_var, "")
        self.repo_menu.grid(row=3, column=1, sticky="w")
        tk.Button(frame, text="Cargar Repos", command=self.load_repos).grid(row=3, column=2)

        tk.Label(frame, text="Tipo de Rama:").grid(row=4, column=0, sticky="w")
        self.branch_type = tk.StringVar()
        tk.OptionMenu(frame, self.branch_type, "feature", "bugfix", "hotfix", "update").grid(row=4, column=1, sticky="w")

        tk.Label(frame, text="Nombre de la Rama:").grid(row=5, column=0, sticky="w")
        self.entry_branch_name = tk.Entry(frame, width=30)
        self.entry_branch_name.grid(row=5, column=1, sticky="w")

        tk.Label(frame, text="Mensaje Commit:").grid(row=6, column=0, sticky="w")
        self.entry_commit = tk.Entry(frame, width=50)
        self.entry_commit.grid(row=6, column=1, sticky="w")

        tk.Button(frame, text="🚀 Subir y Crear PR", command=self.deploy).grid(row=7, column=1, pady=5)
        tk.Button(frame, text="📤 Hacer Push Manual", command=self.push_current_branch).grid(row=8, column=1, pady=5)

        self.log = ScrolledText(self.root, height=10)
        self.log.pack(padx=10, pady=5, fill="both", expand=True)

    def browse_folder(self):
        self.path = filedialog.askdirectory()
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, self.path)

    def detect_and_test(self):
        path = self.entry_path.get()
        if not os.path.isdir(path):
            messagebox.showerror("Error", "Ruta no válida")
            return
        self.label_project.config(text="Detectando...")
        tipo = detect_project_type(path)
        self.label_project.config(text=tipo)

        self.log.insert(tk.END, f"🔍 Proyecto detectado: {tipo}\n")
        if tipo == "Python":
            import shutil
            if not shutil.which("pytest"):
                self.log.insert(tk.END, "⚠️ 'pytest' no está instalado. Instálalo con: pip install pytest\n")
                return
        if not run_tests(tipo):
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
        if not check_for_secrets(path):
            messagebox.showerror("Seguridad", "Secretos encontrados en el proyecto")
            return

        tipo = self.branch_type.get()
        nombre = self.entry_branch_name.get()
        rama = f"{tipo}/{nombre}"
        mensaje = self.entry_commit.get()
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
            self.gh.create_pr(self.repo_name, rama, mensaje, f"Auto PR desde BulletUploader GUI")
            subprocess.run(["gh", "pr", "view", "--web"], cwd=path)
            self.log.insert(tk.END, "✅ PR creado correctamente\n")
        except Exception as e:
            self.log.insert(tk.END, f"❌ Error: {str(e)}\n")

    def push_current_branch(self):
        path = self.entry_path.get()
        try:
            subprocess.run(["git", "push"], cwd=path, check=True)
            self.log.insert(tk.END, "✅ Push realizado con éxito\n")
        except subprocess.CalledProcessError as e:
            self.log.insert(tk.END, f"❌ Error al hacer push: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BulletUploader(root)
    root.mainloop()
