Вот полный список того, что нужно реализовать на бэкенде для интеграции с нашим фронтендом:

## 📡 API Эндпоинты для реализации

### 1. 📧 Email сервис

**POST** `/api/v1/emails/subscribe`
```json
Request:
{
  "email": "user@example.com",
  "source": "hero_section",
  "metadata": {
    "timestamp": "2025-11-21T10:00:00Z",
    "user_agent": "Mozilla/5.0..."
  }
}

Response:
{
  "data": {
    "id": "uuid-here",
    "email": "user@example.com", 
    "subscribed": true,
    "created_at": "2025-11-21T10:00:00Z"
  },
  "success": true,
  "message": "Email успешно добавлен"
}
```

**GET** `/api/v1/emails/status/{email}`
```json
Response:
{
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "subscribed": true,
    "created_at": "2025-11-21T10:00:00Z"
  },
  "success": true
}
```

### 2. 📄 Резюме сервис

**POST** `/api/v1/resumes/upload`
```
Content-Type: multipart/form-data

FormData:
- resume: File (PDF, DOC, DOCX, TXT)
- email: string (optional)

Response:
{
  "data": {
    "upload_id": "uuid-here",
    "file_name": "resume.pdf",
    "file_size": 1048576,
    "status": "uploaded", // или "processing"
    "analysis_id": "analysis-uuid" // если анализ запускается сразу
  },
  "success": true
}
```

**GET** `/api/v1/resumes/supported-formats`
```json
Response:
{
  "data": [".pdf", ".doc", ".docx", ".txt"],
  "success": true
}
```

### 3. 🔍 Анализ сервис

**GET** `/api/v1/analysis/{analysis_id}`
```json
Response (processing):
{
  "data": {
    "analysis_id": "uuid-here",
    "status": "processing"
  },
  "success": true
}

Response (completed):
{
  "data": {
    "analysis_id": "uuid-here", 
    "status": "completed",
    "results": {
      "position_levels": [
        {
          "level": "Junior Developer",
          "salary_min": 80000,
          "salary_max": 120000,
          "currency": "₽",
          "confidence": 0.85
        },
        {
          "level": "Middle Developer", 
          "salary_min": 150000,
          "salary_max": 250000,
          "currency": "₽",
          "confidence": 0.92
        }
      ],
      "market_data": {
        "total_vacancies_analyzed": 15420,
        "data_freshness_days": 30,
        "location": "Москва"
      },
      "recommendations": [
        "Добавьте больше технических навыков",
        "Укажите опыт работы с React"
      ]
    }
  },
  "success": true
}

Response (error):
{
  "data": {
    "analysis_id": "uuid-here",
    "status": "error", 
    "error_message": "Не удалось распознать текст резюме"
  },
  "success": false
}
```

**POST** `/api/v1/analysis/start` (опционально, если анализ не запускается автоматически)
```json
Request:
{
  "upload_id": "uuid-here",
  "email": "user@example.com"
}

Response:
{
  "data": {
    "analysis_id": "uuid-here",
    "status": "processing"
  },
  "success": true
}
```

## 🛡️ Обработка ошибок

Стандартизированные HTTP коды:
- **400** - Некорректные данные (невалидный email, неподдерживаемый формат файла)
- **413** - Файл слишком большой (> 10MB)
- **429** - Слишком много запросов (rate limiting)
- **500** - Внутренняя ошибка сервера

Формат ошибок:
```json
{
  "success": false,
  "message": "Описание ошибки для пользователя",
  "code": "VALIDATION_ERROR", // опционально
  "details": {} // опционально, для debugging
}
```

## 📋 Требования к реализации

### Валидация:
- **Email**: RFC compliant, длина ≤ 254 символа
- **Файлы**: PDF/DOC/DOCX/TXT, размер ≤ 10MB
- **MIME типы**: `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`

### Функциональность:
- ✅ Сохранение email в БД с дедупликацией
- ✅ Асинхронная обработка резюме (очередь задач)
- ✅ Парсинг текста из файлов резюме
- ✅ ML анализ для определения уровня и зарплат
- ✅ Интеграция с данными о вакансиях/зарплатах
- ✅ Отправка результатов на email (опционально)

### База данных:
```sql
-- Таблица подписок
emails (
  id UUID PRIMARY KEY,
  email VARCHAR(254) UNIQUE,
  source VARCHAR(50),
  metadata JSONB,
  subscribed BOOLEAN DEFAULT true,
  created_at TIMESTAMP
)

-- Таблица загрузок
uploads (
  id UUID PRIMARY KEY, 
  file_name VARCHAR(255),
  file_size INTEGER,
  file_path VARCHAR(500),
  email VARCHAR(254),
  status VARCHAR(20), -- uploaded, processing, completed, error
  created_at TIMESTAMP
)

-- Таблица анализов
analyses (
  id UUID PRIMARY KEY,
  upload_id UUID REFERENCES uploads(id),
  status VARCHAR(20), -- processing, completed, error  
  results JSONB,
  error_message TEXT,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
)
```

### Дополнительно:
- 🔄 CORS настройки для `http://localhost:3000`
- 📊 Логирование запросов и ошибок
- ⚡ Rate limiting (например, 100 req/min на IP)
- 🗂️ Файловое хранилище (локальное или S3)
- 📬 Email уведомления (опционально)

Фронтенд готов к полной интеграции! 🚀