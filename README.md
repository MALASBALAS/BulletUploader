# 🤖 BulletUploader GUI

**BulletUploader** is an advanced graphical interface designed to automate and simplify uploading and managing repositories on GitHub. Inspired by the **JARVIS** (Iron Man) aesthetic, it combines a modern design with powerful developer tools.

---

## ✨ Main Features

- 🔍 **Automatic project type detection** (Python, Node, etc.)
- ✅ **Test execution** with `pytest` or other tools depending on the stack
- 🔐 **Secret scanning** (API keys, passwords, tokens) before uploading code
- 🌱 **Branch creator** following conventions: `feature/JIRA-ID/description`
- 💬 **Commit generator** with automatic changelog integration
- 🚀 **Push and Pull Request** to GitHub using GitHub CLI (`gh`)
- 📦 **Automatic repository loading** from your GitHub account
- 🧹 **Unwanted folder cleanup** (`.git`, `__pycache__`, `.vscode`, etc.)
- 📋 **Auto-generated changelog** from your commits
- 🖥️ **Modern interface** inspired by JARVIS, with custom themes and intuitive experience
- ℹ️ **Quick view** of modified files before committing

---

## ⚡ Installation

### Requirements

- Python 3.9+ (recomendado 3.11)
- Git instalado y en PATH
- GitHub CLI (`gh`) autenticado (opcional, recomendado)
- Tk (Tkinter) disponible para la GUI
	- Ubuntu: `sudo apt-get update && sudo apt-get install -y python3-tk`
	- macOS: si usas Homebrew Python: `brew install python-tk@3.11` (ajusta versión); o usa el Python del sistema con Tk.


## Ejecutar en macOS (Monterey 12.7.6+) y Ubuntu

Requisitos del sistema:
- Python 3.9+ (recomendado 3.11)
- Tk (Tkinter):
  - Ubuntu: `sudo apt-get update && sudo apt-get install -y python3-tk`
  - macOS: si usas Homebrew Python: `brew install python-tk@3.11` (ajusta versión); o usa el Python del sistema con Tk.
- Git instalado y en PATH
- GitHub CLI `gh` (opcional pero recomendado) autenticado (`gh auth login`)

Pasos:
1) Da permisos de ejecución al launcher (una vez):
	- macOS/Ubuntu: `chmod +x ./run.sh`
2) Ejecuta:
	- `./run.sh`

El script creará/activará `.venv`, instalará dependencias de `requirements.txt` y lanzará la app.

## Ejecutar en Windows

Usa `run.bat` (se autoeleva y preferirá `.venv` local si existe).

### Clone and Run

```bash
git clone https://github.com/your-user/BulletUploader.git
cd BulletUploader
pip install -r requirements.txt
python main_gui.py
```

---

## 🚀 Quick Start

1. **Select your project folder.**
2. **Detect the project type** and run tests automatically.
3. **Load or select your GitHub repository.**
4. **Create a branch, write your commit, and push the changes.**
5. **The Pull Request will open automatically in your browser.**

---

## 🛡️ Smart Security

Before uploading code, BulletUploader scans your files for secrets (API keys, passwords, tokens, etc.) and can clean unwanted folders to prevent accidental leaks.

---

## 🧠 Smart Conventions

- **Commit format:** `type: JIRA-ID message`
- **Branch format:** `type/JIRA-ID/short-description`
- **Changelog:** automatic entries based on your commits

---

## 👨‍💻 Author

Developed by Álvaro Balas – part of a local AI-powered developer workflow assistant.

---

## 📄 License

MIT License – free to use and modify.
