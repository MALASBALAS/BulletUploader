# utils/security_checker.py

import os
import re
import shutil
import stat

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS Access Key
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),  # Google API Key
    re.compile(r"ghp_[0-9A-Za-z]{36}"),  # GitHub Personal Access Token
    re.compile(r"gho_[0-9A-Za-z]{36}"),  # GitHub OAuth Token
    re.compile(r"ghu_[0-9A-Za-z]{36}"),  # GitHub User Token
    re.compile(r"ghs_[0-9A-Za-z]{36}"),  # GitHub Server Token
    re.compile(r"glpat-[0-9A-Za-z\-_]{20}"),  # GitLab Personal Access Token
    re.compile(r"sk-[0-9A-Za-z]{48}"),  # OpenAI API Key
    re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,48}"),  # Slack tokens
    # Genérico (evitar falsos positivos conocidos con negative lookahead)
    re.compile(r"(?i)(?!SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED)(password|secret|api[_-]?key)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9\-_]{8,}"),
]

FOLDERS_TO_REMOVE = [
    ".pytest_cache",
    "__pycache__",
    ".vscode",
    ".idea",
    "node_modules"
]

EXCLUDED_DIRECTORIES = {"node_modules", ".vite", "dist", "build", ".git", ".venv"}
EXCLUDED_PATTERNS = [
    "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED",  # React PropTypes constant
    "ReactPropTypesSecret",
]

def handle_remove_readonly(func, path, exc):
    """Maneja archivos de solo lectura durante la eliminación"""
    try:
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
    except Exception:
        pass

def clean_root_folders(path):
    """Limpia carpetas indeseadas de la raíz del proyecto."""
    for folder_name in FOLDERS_TO_REMOVE:
        folder_path = os.path.join(path, folder_name)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path, onerror=handle_remove_readonly)
                print(f"✅ Eliminado: {folder_path}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {folder_path}: {e}")

def _mask_secret(snippet: str) -> str:
    if not snippet:
        return ""
    if len(snippet) <= 6:
        return "*" * len(snippet)
    return snippet[:3] + "*" * max(0, len(snippet) - 6) + snippet[-3:]

def check_for_secrets(path, clean_folders=True):
    """
    Escanea archivos buscando posibles secretos. True si no hay hallazgos, False si encuentra alguno.
    """
    if clean_folders:
        clean_root_folders(path)

    findings = []
    for root, _, files in os.walk(path):
        # Omitir directorios excluidos
        if any(excl in root.replace("\\", "/").split("/") for excl in EXCLUDED_DIRECTORIES):
            continue

        for file in files:
            if not file.endswith((".py", ".js", ".ts", ".env", ".json", ".yml", ".yaml", ".ini", ".cfg", ".txt")):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Excluir patrones conocidos falsos positivos
                if any(p in content for p in EXCLUDED_PATTERNS):
                    continue

                for pattern in SECRET_PATTERNS:
                    match = pattern.search(content)
                    if match:
                        snippet = match.group(0)
                        print(f"🔐 Posible secreto encontrado en {file_path}: {_mask_secret(snippet)}")
                        findings.append((file_path, pattern.pattern))
                        break  # Un hallazgo por archivo es suficiente
            except Exception as e:
                print(f"⚠️ No se pudo leer {file_path}: {e}")

    if findings:
        print("❌ Se detectaron posibles secretos. Revisa los archivos listados arriba.")
        return False

    print("✅ No se encontraron posibles secretos.")
    return True
