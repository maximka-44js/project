import os

structure = {
    "backend": [
        "docker-compose.yml",
        ".env",
        "nginx.conf",
        {"api-gateway": [
            "Dockerfile",
            "requirements.txt",
            "app.py",
            {"middleware": ["auth.py"]},
            {"routes": ["gateway.py"]}
        ]},
        {"services": [
            {"user-service": [
                "Dockerfile",
                "requirements.txt",
                "app.py",
                {"models": ["user.py"]},
                {"routes": ["emails.py"]},
                {"utils": ["validation.py"]}
            ]},
            {"resume-service": [
                "Dockerfile",
                "requirements.txt",
                "app.py",
                {"models": ["resume.py"]},
                {"routes": ["resumes.py"]},
                {"storage": ["file_handler.py"]},
                {"utils": ["validators.py"]}
            ]},
            {"analysis-service": [
                "Dockerfile",
                "requirements.txt",
                "app.py",
                {"models": ["analysis.py"]},
                {"routes": ["analysis.py"]},
                {"workers": ["analyzer.py"]},
                {"utils": ["ml_processor.py"]}
            ]}
        ]},
        {"shared": [
            "__init__.py",
            "database.py",
            "auth.py",
            "redis_client.py",
            "schemas.py"
        ]},
        "uploads"
    ]
}

def create_structure(base_path, struct):
    for item in struct:
        if isinstance(item, str):
            path = os.path.join(base_path, item)
            if '.' in os.path.basename(item):  # file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, 'a').close()
            else:  # folder
                os.makedirs(path, exist_ok=True)
        elif isinstance(item, dict):
            for folder, contents in item.items():
                folder_path = os.path.join(base_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                create_structure(folder_path, contents)

if __name__ == "__main__":
    create_structure(".", structure["backend"])
    print("Структура создана.")