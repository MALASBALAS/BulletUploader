# utils/security_checker.py

import re
import os
import shutil

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),  # Google
    re.compile(r"ghp_[0-9A-Za-z]{36}"),  # GitHub token
    re.compile(r"(?i)(password|secret|api[_-]?key)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9\-_]{8,}"),
]

FOLDERS_TO_REMOVE = [
    ".pytest_cache",
    ".git",
    ".vscode",
    ".idea",
    "__pycache__"
]

def clean_root_folders(path):
    """
    Elimina carpetas indeseadas en la raíz del proyecto.
    """
    for folder in FOLDERS_TO_REMOVE:
        folder_path = os.path.join(path, folder)
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"🗑️ Carpeta eliminada: {folder_path}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {folder_path}: {e}")

def check_for_secrets(path, clean_folders=True):
    """
    Recorre recursivamente los archivos en el directorio dado y busca patrones de secretos.
    Retorna True si no se encuentran secretos, False si se detecta alguno.
    Si clean_folders es True, elimina carpetas indeseadas en la raíz.
    """
    if clean_folders:
        clean_root_folders(path)
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in SECRET_PATTERNS:
                            if pattern.search(content):
                                print(f"🔐 Posible secreto encontrado en {file_path}")
                                return False
                except Exception as e:
                    print(f"⚠️ No se pudo leer {file_path}: {e}")
    print("✅ No se encontraron posibles secretos.")
    return True
