# utils/test_runner.py

import subprocess
import sys


def run_tests(project_type):
    """
    Ejecuta los tests según el tipo de proyecto detectado.
    Devuelve True si los tests pasan, False si fallan, y None si no hay tests configurados.
    """
    try:
        if project_type == "Node.js":
            subprocess.run(["npm", "install"], check=True)
            subprocess.run(["npm", "test"], check=True)
        elif project_type == "Python":
            result = subprocess.run([sys.executable, "-m", "pytest"])
            return result.returncode == 0
        elif project_type == "Java Maven":
            subprocess.run(["mvn", "test"], check=True)
        elif project_type == "Java Gradle":
            subprocess.run(["./gradlew", "test"], check=True)
        else:
            print("⚠️ No hay tests configurados para este tipo de proyecto.")
            return None
        return True
    except subprocess.CalledProcessError:
        return False
