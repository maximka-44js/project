#!/bin/bash

echo "🚀 СУПЕР БЫСТРАЯ ПРОВЕРКА СИСТЕМЫ"
echo "================================="

# Активируем venv
echo "📦 Активируем venv из корня проекта..."
source .venv/bin/activate

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ venv не активирован! Проверь что .venv есть в корне проекта"
    exit 1
fi

echo "✅ venv активирован: $VIRTUAL_ENV"

# Запускаем инфраструктуру
echo "🐘 Запускаем PostgreSQL и Redis..."
sudo docker-compose up -d postgres redis

# Ждем немного
sleep 3

# Проверяем что поднялись
echo "📊 Статус контейнеров:"
sudo docker-compose ps postgres redis

echo ""
echo "🧪 ЗАПУСКАЙ РУЧНУЮ ПРОВЕРКУ:"
echo "============================"
echo ""
echo "1. Запусти тестовый сервер:"
echo "   python test_ultra_quick.py"
echo ""
echo "2. Или сразу попробуй реальный User Service:"
echo "   cd services/user-service"
echo "   PYTHONPATH='../../shared' python -c \"import sys; print('Python paths:'); [print(p) for p in sys.path]\""
echo ""
echo "3. Если импорты работают, запускай сервис:"
echo "   PYTHONPATH='../../shared' python app.py"
echo ""
echo "4. В другом терминале тестируй:"
echo "   curl http://localhost:8001/"
echo "   curl http://localhost:8001/health"
echo ""
echo "🎯 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ:"
echo "=========================="
echo "- Проверь что venv активирован: echo \$VIRTUAL_ENV"
echo "- Установи зависимости: pip install fastapi uvicorn"
echo "- Проверь контейнеры: sudo docker-compose ps"
echo ""
echo "✨ Готово! Теперь тестируй руками!"