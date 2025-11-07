#!/bin/bash
echo "========================================"
echo "  СБОРКА ТАБЛО ДЛЯ САМБО v3.0"
echo "========================================"
echo ""

echo "[1/3] Проверка зависимостей..."
pip install -r requirements.txt

echo ""
echo "[2/3] Создание исполняемого файла..."
pyinstaller --onefile --windowed --name="SamboScoreboard" \
    --add-data="README.txt:." \
    main.py

echo ""
echo "[3/3] Готово!"
echo ""
echo "Исполняемый файл: dist/SamboScoreboard"
echo ""
