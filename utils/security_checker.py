# utils/security_checker.py

import re
import os
import shutil

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS Access Key
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),  # Google API Key
    re.compile(r"ghp_[0-9A-Za-z]{36}"),  # GitHub Personal Access Token
    re.compile(r"gho_[0-9A-Za-z]{36}"),  # GitHub OAuth Token
    re.compile(r"ghu_[0-9A-Za-z]{36}"),  # GitHub User Token
    re.compile(r"ghs_[0-9A-Za-z]{36}"),  # GitHub Server Token
    re.compile(r"glpat-[0-9A-Za-z\-_]{20}"),  # GitLab Personal Access Token
    re.compile(r"sk-[0-9A-Za-z]{48}"),  # OpenAI API Key
    # More specific pattern for passwords/secrets (exclude React constants)
    re.compile(r"(?i)(?!SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED)(password|secret|api[_-]?key)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9\-_]{8,}"),
]

FOLDERS_TO_REMOVE = [
    ".pytest_cache",
    ".git",
    ".vscode",
    ".idea",
    "__pycache__",
    "node_modules"  # Add node_modules to folders to remove
]

EXCLUDED_PATTERNS = [
    "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED",  # React PropTypes constant
    "ReactPropTypesSecret",  # React internal constant
]

EXCLUDED_DIRECTORIES = [
    "node_modules",
    ".vite",
    "dist",
    "build",
    ".next"
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
        # Skip excluded directories
        if any(excluded_dir in root for excluded_dir in EXCLUDED_DIRECTORIES):
            continue
            
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Check if content contains excluded patterns
                        if any(excluded in content for excluded in EXCLUDED_PATTERNS):
                            continue
                            
                        for pattern in SECRET_PATTERNS:
                            if pattern.search(content):
                                print(f"🔐 Posible secreto encontrado en {file_path}")
                                return False
                except Exception as e:
                    print(f"⚠️ No se pudo leer {file_path}: {e}")
    print("✅ No se encontraron posibles secretos.")
    return True
