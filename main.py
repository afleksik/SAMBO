"""
Главный файл запуска приложения Табло для самбо
Версия 3.0 - Финальная
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Импорт наших модулей
from match_data import MatchData
from spectator_window import SpectatorWindow
from judge_window import JudgeWindow


def main():
    """Главная функция запуска приложения"""
    # Включаем высокое DPI масштабирование
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Устанавливаем имя приложения
    app.setApplicationName("Табло для самбо FIAS v3.0")

    # Создаем модель данных (единая для обоих окон)
    match_data = MatchData()

    # Создаем окно для зрителей
    spectator_window = SpectatorWindow(match_data)

    # Создаем окно для судей
    judge_window = JudgeWindow(match_data)

    # Показываем оба окна
    spectator_window.show()
    judge_window.show()

    # Опционально: размещаем окна на разных мониторах
    #screens = app.screens()
    #if len(screens) > 1:
    #    # Если есть второй монитор, показываем зрительское окно там
    #    second_screen = screens[1]
    #    spectator_window.setGeometry(second_screen.geometry())

    print("="*70)
    print("   ТАБЛО ДЛЯ САМБО - Версия 3.0 (Финальная)")
    print("="*70)
    print("\nОкна запущены:")
    print("  ✓ Окно для зрителей (фамилии 30px, можно масштабировать)")
    print("  ✓ Окно для судей (с кнопкой ОТМЕНЫ)")
    print("\nНовые возможности v3.0:")
    print("  • Увеличенные фамилии спортсменов (30px)")
    print("  • Полное масштабирование обоих окон")
    print("  • КНОПКА ОТМЕНЫ последнего действия (фиолетовая)")
    print("  • БЕЗ всплывающих уведомлений")
    print("  • Правила FIAS применяются автоматически")
    print("="*70)

    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
