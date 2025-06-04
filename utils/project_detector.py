# utils/project_detector.py

import os

def detect_project_type(path):
    files = os.listdir(path)
    
    if "package.json" in files:
        return "Node.js"
    elif "requirements.txt" in files or any(f.endswith(".py") for f in files):
        return "Python"
    elif any(f.endswith(".csproj") for f in files):
        return ".NET"
    elif "pom.xml" in files:
        return "Java Maven"
    elif "build.gradle" in files:
        return "Java Gradle"
    else:
        return "Desconocido"
