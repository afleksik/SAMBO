#!/bin/bash

echo "=================================="
echo "  Сборка .exe для Windows"
echo "=================================="

# Проверяем наличие spec файла
if [ ! -f "sambo.spec" ]; then
    echo "✗ Ошибка: sambo.spec не найден!"
    echo "Создайте файл sambo.spec"
    exit 1
fi

# Создаем папку для результата
mkdir -p dist

# Собираем образ
echo "Шаг 1: Создание Docker образа..."
docker build -f Dockerfile.windows -t sambo-windows-builder .

# Запускаем сборку
echo "Шаг 2: Сборка .exe файла..."
docker run --rm -v "$(pwd)/dist:/output" sambo-windows-builder

# Проверяем результат
if [ -f "dist/Sambo_Scoreboard.exe" ]; then
    echo "=================================="
    echo "✓ Успешно!"
    echo "✓ Файл: dist/Sambo_Scoreboard.exe"
    echo "=================================="
    ls -lh dist/Sambo_Scoreboard.exe
else
    echo "✗ Ошибка: .exe не создан"
    echo "Проверьте логи выше"
    exit 1
fi
