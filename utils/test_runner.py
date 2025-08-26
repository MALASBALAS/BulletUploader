# utils/test_runner.py

import subprocess
import shutil
import os
import sys


def run_tests(project_type):
    """
    Ejecuta los tests según el tipo de proyecto detectado.
    Devuelve True si los tests pasan, False si fallan, y None si no hay tests configurados.
    """
    try:
        if project_type == "Node.js":
            # Verificar si npm está disponible
            if not shutil.which("npm"):
                print("⚠️ npm no está instalado o no está en el PATH")
                return None
            
            # Verificar si package.json existe
            if not os.path.exists("package.json"):
                print("⚠️ No se encontró package.json")
                return None
                
            subprocess.run(["npm", "install"], check=True)
            result = subprocess.run(["npm", "test"], capture_output=True)
            return result.returncode == 0
            
        elif project_type == "Python":
            # Verificar si pytest está disponible
            if not shutil.which("pytest"):
                print("⚠️ pytest no está instalado")
                return None
                
            result = subprocess.run(["pytest"], capture_output=True)
            return result.returncode == 0
            
        elif project_type == "Java Maven":
            subprocess.run(["mvn", "test"], check=True)
        elif project_type == "Java Gradle":
            subprocess.run(["./gradlew", "test"], check=True)
        else:
            print(f"⚠️ Tipo de proyecto no soportado para tests: {project_type}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")
        return None
