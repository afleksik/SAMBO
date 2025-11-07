@echo off
chcp 65001 >nul
echo ========================================
echo   СБОРКА ТАБЛО ДЛЯ САМБО v3.0
echo ========================================
echo.

echo [1/3] Проверка зависимостей...
pip install -r requirements.txt

echo.
echo [2/3] Создание исполняемого файла .exe...
pyinstaller --onefile --windowed --name="SamboScoreboard" ^
    --icon=icon.ico ^
    --add-data="README.txt;." ^
    main.py

echo.
echo [3/3] Готово!
echo.
echo Исполняемый файл: dist\SamboScoreboard.exe
echo.
echo Скопируйте SamboScoreboard.exe на любой компьютер и запустите!
echo Установка Python не требуется.
echo.
pause
