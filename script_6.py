
# Создадим requirements.txt
requirements = '''PyQt6>=6.4.0
pyinstaller>=5.13.0
'''

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements)

# Создадим build.bat для Windows
build_bat = '''@echo off
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
echo Исполняемый файл: dist\\SamboScoreboard.exe
echo.
echo Скопируйте SamboScoreboard.exe на любой компьютер и запустите!
echo Установка Python не требуется.
echo.
pause
'''

with open('build.bat', 'w', encoding='utf-8') as f:
    f.write(build_bat)

# Создадим build.sh для Linux/Mac
build_sh = '''#!/bin/bash
echo "========================================"
echo "  СБОРКА ТАБЛО ДЛЯ САМБО v3.0"
echo "========================================"
echo ""

echo "[1/3] Проверка зависимостей..."
pip install -r requirements.txt

echo ""
echo "[2/3] Создание исполняемого файла..."
pyinstaller --onefile --windowed --name="SamboScoreboard" \\
    --add-data="README.txt:." \\
    main.py

echo ""
echo "[3/3] Готово!"
echo ""
echo "Исполняемый файл: dist/SamboScoreboard"
echo ""
'''

with open('build.sh', 'w', encoding='utf-8') as f:
    f.write(build_sh)

# Создадим spec-файл для PyInstaller (более продвинутая конфигурация)
spec_file = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('README.txt', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SamboScoreboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
'''

with open('SamboScoreboard.spec', 'w', encoding='utf-8') as f:
    f.write(spec_file)

print("✓ Создан файл: requirements.txt")
print("✓ Создан файл: build.bat (для Windows)")
print("✓ Создан файл: build.sh (для Linux/Mac)")
print("✓ Создан файл: SamboScoreboard.spec (конфигурация PyInstaller)")
