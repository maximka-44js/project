from agents import Agent, Runner
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ScheduleType(str, Enum):
    """График работы"""
    OTHER = "OTHER"
    FLEXIBLE = "FLEXIBLE"
    SIX_ON_ONE_OFF = "SIX_ON_ONE_OFF"
    FIVE_ON_TWO_OFF = "FIVE_ON_TWO_OFF"
    TWO_ON_TWO_OFF = "TWO_ON_TWO_OFF"
    THREE_ON_THREE_OFF = "THREE_ON_THREE_OFF"
    FOUR_ON_TWO_OFF = "FOUR_ON_TWO_OFF"
    UNKNOWN = "unknown"
    ONE_ON_THREE_OFF = "ONE_ON_THREE_OFF"
    WEEKEND = "WEEKEND"
    FOUR_ON_FOUR_OFF = "FOUR_ON_FOUR_OFF"
    TWO_ON_ONE_OFF = "TWO_ON_ONE_OFF"
    FOUR_ON_THREE_OFF = "FOUR_ON_THREE_OFF"
    ONE_ON_TWO_OFF = "ONE_ON_TWO_OFF"
    THREE_ON_TWO_OFF = "THREE_ON_TWO_OFF"


class ExperienceLevel(str, Enum):
    """Уровень опыта"""
    BETWEEN_1_AND_3 = "between1And3"
    NO_EXPERIENCE = "noExperience"
    BETWEEN_3_AND_6 = "between3And6"
    MORE_THAN_6 = "moreThan6"


class VacancyAnalysisOutput(BaseModel):
    """
    Модель для валидации выходных данных анализа вакансий OpenAI agents-sdk
    """
    vacancy_nm: str = Field(
        ...,
        description="Название вакансии. Строка от 1 до 255 символов. Например: 'Программист', 'Python Developer', 'Data Scientist'",
        min_length=1,
        max_length=255
    )
    
    location: str = Field(
        ...,
        description="Местоположение вакансии. Строка от 1 до 255 символов. Например: 'Москва', 'Санкт-Петербург', 'Удаленно'",
        min_length=1,
        max_length=255
    )
    
    schedule: ScheduleType = Field(
        ...,
        description="График работы. Возможные значения: 'OTHER', 'FLEXIBLE', 'SIX_ON_ONE_OFF', 'FIVE_ON_TWO_OFF', 'TWO_ON_TWO_OFF', 'THREE_ON_THREE_OFF', 'FOUR_ON_TWO_OFF', 'unknown', 'ONE_ON_THREE_OFF', 'WEEKEND', 'FOUR_ON_FOUR_OFF', 'TWO_ON_ONE_OFF', 'FOUR_ON_THREE_OFF', 'ONE_ON_TWO_OFF', 'THREE_ON_TWO_OFF'"
    )
    
    experience: ExperienceLevel = Field(
        ...,
        description="Требуемый уровень опыта. Возможные значения: 'between1And3' (от 1 до 3 лет), 'noExperience' (без опыта), 'between3And6' (от 3 до 6 лет), 'moreThan6' (более 6 лет)"
    )
    
    work_hours: float = Field(
        ...,
        description="Количество рабочих часов в день. Допустимые значения: от 0.0 до 24 (максимум часов в дне). Например: 8.0 для полного рабочего дня",
        ge=0.0,
        le=168.0  # максимум часов в неделе
    )
    
    skills_text: str = Field(
        ...,
        description="Требуемые навыки в текстовом формате. Строка от 1 до 1000 символов. Перечислите навыки через запятую. Например: 'Python, Java, Swagger', 'React, Node.js, MongoDB'",
        min_length=1,
        max_length=1000
    )

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra="forbid"  # запрещаем дополнительные поля
    )
 

extr_agent = Agent(
    name="Resume Extractor",
    instructions=(
        "Ты — эксперт по анализу резюме. Твоя задача — выделять из текста резюме следующие поля:\n"
        "- vacancy_nm: Название вакансии (например, 'Программист', 'Python Developer').\n"
        "- location: Местоположение (например, 'Москва', 'Удаленно').\n"
        "- schedule: График работы (выбери одно из: 'OTHER', 'FLEXIBLE', 'SIX_ON_ONE_OFF', 'FIVE_ON_TWO_OFF', "
        "'TWO_ON_TWO_OFF', 'THREE_ON_THREE_OFF', 'FOUR_ON_TWO_OFF', 'unknown', 'ONE_ON_THREE_OFF', 'WEEKEND', "
        "'FOUR_ON_FOUR_OFF', 'TWO_ON_ONE_OFF', 'FOUR_ON_THREE_OFF', 'ONE_ON_TWO_OFF', 'THREE_ON_TWO_OFF').\n"
        "- experience: Уровень опыта (выбери одно из: 'between1And3', 'noExperience', 'between3And6', 'moreThan6').\n"
        "- work_hours: Количество рабочих часов в день (от 0.0 до 24.0).\n"
        "- skills_text: Перечисли навыки через запятую (например, 'Python, Java, Swagger').\n"
        "Извлекай только указанные поля, строго следуя формату. Не добавляй лишней информации. "
        "Если поле отсутствует, оставь его пустым или укажи 'unknown'."
    ),
    output_type=VacancyAnalysisOutput
)


text = """Иванов Иван Иванович
Дата рождения: 01.01.1990
Телефон: +7 (999) 123-45-67
Email: ivanov@example.com

Цель: Получение должности Python-разработчика

Образование:
2012–2017 — МГУ, факультет прикладной математики, бакалавр

Опыт работы:
2018–2025 — ООО «ТехноСофт», Python-разработчик
— Разработка и поддержка веб-приложений
— Работа с базами данных (PostgreSQL, MySQL)
— Внедрение автоматизации бизнес-процессов

Навыки:
— Python, Django, Flask
— SQL
— Git
— Docker

Личные качества:
— Ответственность
— Внимательность
— Умение работать в команде"""



