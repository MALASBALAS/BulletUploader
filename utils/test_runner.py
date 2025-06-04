# utils/test_runner.py

import subprocess

def run_tests(project_type):
    try:
        if project_type == "Node.js":
            subprocess.run(["npm", "install"], check=True)
            subprocess.run(["npm", "test"], check=True)
        elif project_type == "Python":
            subprocess.run(["pytest"], check=True)
        elif project_type == "Java Maven":
            subprocess.run(["mvn", "test"], check=True)
        elif project_type == "Java Gradle":
            subprocess.run(["./gradlew", "test"], check=True)
        else:
            print("⚠️ No hay tests configurados para este tipo de proyecto.")
            return True
        return True
    except subprocess.CalledProcessError:
        return False
