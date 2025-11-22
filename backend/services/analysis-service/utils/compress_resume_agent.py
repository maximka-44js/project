import os
from typing import List

from pydantic import BaseModel, Field
import openai

import asyncio

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


class Resume(BaseModel):
    role: str = Field(description="Основная профессиональная роль или желаемая должность, указанная в резюме.")
    experience: str = Field(description="Краткое, обобщенное описание профессионального опыта кандидата (например, '5+ лет в разработке ПО', 'Старший менеджер по продукту с 10-летним опытом').")
    skills: List[str] = Field(description="Список ключевых технических и мягких навыков, представленный в виде массива строк (например, ['Python', 'SQL', 'Машинное обучение', 'Управление проектами']).")
    city: str = Field(description="Текущий или предпочтительный город проживания кандидата. Если не указан явно, постарайтесь вывести его или укажите None.")


tools = [
    {
        "type": "function",
        "function": {
            "name": "summarize_resume",
            "description": "Извлекает и суммирует ключевую информацию из текста резюме, возвращая структурированный словарь.",
            "parameters": Resume.model_json_schema(),
        },
    }
]

system_prompt = """
Вы — высокоэффективный и точный помощник по анализу резюме.
Ваша основная задача — прочитать предоставленный текст резюме и извлечь четыре ключевых элемента информации:
1. role: Основная профессиональная роль или желаемая должность.
2. experience: Краткое описание профессионального опыта.
3. skills: Список ключевых технических и мягких навыков, представленный в формате массива строк Python (например, ['Python', 'SQL', 'Машинное обучение']).
4. city: Город проживания.

Если какая-либо информация не указана явно, постарайтесь разумно ее вывести или укажите 'неизвестно'.
Всегда используйте предоставленный инструмент 'summarize_resume' для возврата структурированного резюме.
"""


async def agent_summarize_resume(resume_text: str) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Пожалуйста, проанализируйте и суммируйте следующее резюме:\n\n{resume_text}"}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o",  # Choose required model
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "summarize_resume"}},
    )

    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        raise ValueError("Агент не выполнил вызов инструмента.")

    function_args_str = tool_calls[0].function.arguments 
    
    resume_summary_obj = Resume.model_validate_json(function_args_str)
    
    return resume_summary_obj.model_dump()
