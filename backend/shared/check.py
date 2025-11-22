import requests

# Конфигурация
AUTH_URL = "http://127.0.0.1:8001/login"  # URL микросервиса авторизации
UPLOAD_URL = "http://localhost:8002/api/v1/resumes/upload"  # URL сервиса загрузки
CREDENTIALS = {
    "email": "user@exap.com",  # Данные для входа
    "password": "password123"
}
RESUME_FILE_PATH = "/home/user/Downloads/1.pdf"  # Путь к файлу для загрузки

def get_access_token():
    """Получение access token из микросервиса авторизации"""
    try:
        response = requests.post(AUTH_URL, json=CREDENTIALS)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            print("Access token не найден в ответе.")
            return None
        return access_token
    except requests.RequestException as e:
        print(f"Ошибка при получении токена: {e}")
        return None

def upload_resume(access_token):
    """Загрузка файла с использованием access token"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        "resume": open(RESUME_FILE_PATH, "rb"),
        "email": (None, CREDENTIALS["email"])
    }
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files)
        response.raise_for_status()  # Проверка на ошибки HTTP
        print("Файл успешно загружен:", response.json())
    except requests.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")

if __name__ == "__main__":
    # Получение токена
    token = get_access_token()
    if token:
        print("Токен получен:", token)
        # Загрузка файла
        upload_resume(token)
    else:
        print("Не удалось получить токен.")