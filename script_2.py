
# Создадим судейское окно (часть 1) - без уведомлений, с кнопкой Undo
judge_window_final_p1 = '''"""
Окно управления для судей (финальная версия с отменой действий)
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, QGridLayout, QMessageBox)
from PyQt6.QtCore import QTimer, Qt


class JudgeWindow(QMainWindow):
    """Окно управления для судей с применением правил FIAS и функцией отмены"""
    
    def __init__(self, match_data):
        super().__init__()
        self.match_data = match_data
        self.setWindowTitle("Панель управления - Судейская")
        
        # Окно можно свободно изменять размер
        self.setGeometry(50, 50, 1150, 800)
        self.setMinimumSize(900, 600)
        
        # Таймеры
        self.match_timer = QTimer()
        self.match_timer.timeout.connect(self.update_match_timer)
        self.match_running = False
        
        self.hold_timer_1 = QTimer()
        self.hold_timer_1.timeout.connect(lambda: self.update_hold_timer(1))
        self.hold_running_1 = False
        
        self.hold_timer_2 = QTimer()
        self.hold_timer_2.timeout.connect(lambda: self.update_hold_timer(2))
        self.hold_running_2 = False
        
        # Подключаем сигнал окончания матча
        self.match_data.match_ended.connect(self.on_match_ended)
        self.match_data.action_undone.connect(self.on_action_undone)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Заголовок
        title = QLabel("ПАНЕЛЬ УПРАВЛЕНИЯ ТАБЛО САМБО (FIAS)")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Таймер матча
        timer_group = self.create_timer_section()
        main_layout.addWidget(timer_group)
        
        # Секции для двух борцов
        athletes_layout = QHBoxLayout()
        
        # Борец 1 (красный)
        athlete1_group = self.create_athlete_control(1, "#c0392b")
        athletes_layout.addWidget(athlete1_group)
        
        # Борец 2 (синий)
        athlete2_group = self.create_athlete_control(2, "#2980b9")
        athletes_layout.addWidget(athlete2_group)
        
        main_layout.addLayout(athletes_layout)
        
        # Глобальные кнопки управления
        control_group = self.create_global_controls()
        main_layout.addWidget(control_group)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #ecf0f1; }
            QPushButton {
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
    
    def create_timer_section(self):
        """Создать секцию таймера"""
        group = QGroupBox("Таймер матча")
        layout = QVBoxLayout()
        
        # Отображение времени
        self.timer_display = QLabel("5:00")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                background-color: black;
                color: white;
                padding: 15px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.timer_display)
        
        # Кнопки управления таймером
        timer_buttons = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Старт")
        self.start_button.clicked.connect(self.start_match_timer)
        self.start_button.setStyleSheet("background-color: #27ae60; color: white;")
        timer_buttons.addWidget(self.start_button)
        
        self.pause_button = QPushButton("⏸ Пауза")
        self.pause_button.clicked.connect(self.pause_match_timer)
        self.pause_button.setStyleSheet("background-color: #f39c12; color: white;")
        timer_buttons.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("↻ Сброс")
        self.reset_button.clicked.connect(self.reset_match_timer)
        self.reset_button.setStyleSheet("background-color: #3498db; color: white;")
        timer_buttons.addWidget(self.reset_button)
        
        layout.addLayout(timer_buttons)
        group.setLayout(layout)
        
        return group
    
    def create_athlete_control(self, athlete_num, color):
        """Создать панель управления для борца"""
        group = QGroupBox(f"Борец {athlete_num} ({'Красный' if athlete_num == 1 else 'Синий'})")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 15px;
                font-weight: bold;
                border: 3px solid {color};
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                color: {color};
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Поля ввода информации
        info_layout = QGridLayout()
        
        name_label = QLabel("Фамилия:")
        info_layout.addWidget(name_label, 0, 0)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Введите фамилию борца")
        name_input.textChanged.connect(
            lambda text: self.update_athlete_name(athlete_num, text)
        )
        setattr(self, f"name_input_{athlete_num}", name_input)
        info_layout.addWidget(name_input, 0, 1)
        
        club_label = QLabel("Университет:")
        info_layout.addWidget(club_label, 1, 0)
        
        club_input = QLineEdit()
        club_input.setPlaceholderText("Введите университет/клуб")
        club_input.textChanged.connect(
            lambda text: self.update_athlete_club(athlete_num, text)
        )
        setattr(self, f"club_input_{athlete_num}", club_input)
        info_layout.addWidget(club_input, 1, 1)
        
        layout.addLayout(info_layout)
        
        # Счет
        score_label = QLabel("Счет: 0")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: white;
                background-color: {color};
                padding: 12px;
                border-radius: 5px;
            }}
        """)
        setattr(self, f"score_display_{athlete_num}", score_label)
        layout.addWidget(score_label)
        
        # Кнопки добавления очков
        points_layout = QHBoxLayout()
        
        btn1 = QPushButton("+1")
        btn1.clicked.connect(lambda: self.add_points(athlete_num, 1))
        btn1.setStyleSheet(f"background-color: {color}; color: white;")
        points_layout.addWidget(btn1)
        
        btn2 = QPushButton("+2")
        btn2.clicked.connect(lambda: self.add_points(athlete_num, 2))
        btn2.setStyleSheet(f"background-color: {color}; color: white;")
        points_layout.addWidget(btn2)
        
        btn4 = QPushButton("+4")
        btn4.clicked.connect(lambda: self.add_points(athlete_num, 4))
        btn4.setStyleSheet(f"background-color: {color}; color: white;")
        points_layout.addWidget(btn4)
        
        layout.addLayout(points_layout)
        
        # Предупреждения
        warning_label = QLabel("Предупреждения: 0/3")
        warning_label.setStyleSheet("font-size: 13px; padding: 5px; font-weight: bold;")
        setattr(self, f"warning_display_{athlete_num}", warning_label)
        layout.addWidget(warning_label)
        
        warning_btn = QPushButton("⚠ Добавить предупреждение")
        warning_btn.clicked.connect(lambda: self.add_warning(athlete_num))
        warning_btn.setStyleSheet("background-color: #f39c12; color: white;")
        layout.addWidget(warning_btn)
        
        # Удержание
        hold_label = QLabel("Удержание: 00 сек")
        hold_label.setStyleSheet("font-size: 13px; padding: 5px; font-weight: bold;")
        setattr(self, f"hold_display_{athlete_num}", hold_label)
        layout.addWidget(hold_label)
        
        hold_btn = QPushButton("⏱ Начать удержание")
        hold_btn.clicked.connect(lambda: self.toggle_hold(athlete_num))
        hold_btn.setStyleSheet(f"background-color: {color}; color: white;")
        setattr(self, f"hold_button_{athlete_num}", hold_btn)
        layout.addWidget(hold_btn)
        
        # Информация о правилах удержания
        hold_info = QLabel("10сек=+2 очка, 20сек=+4 (победа)")
        hold_info.setStyleSheet("font-size: 10px; color: #7f8c8d; font-style: italic;")
        hold_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hold_info)
        
        # Победа
        victory_btn = QPushButton("🏆 ПОБЕДА")
        victory_btn.clicked.connect(lambda: self.declare_victory(athlete_num))
        victory_btn.setStyleSheet(f"background-color: gold; color: black; font-size: 15px;")
        layout.addWidget(victory_btn)
        
        group.setLayout(layout)
        return group'''

print("Создание судейского окна (часть 1)...")
