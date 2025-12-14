"""
Окно табло для зрителей (финальная версия с динамическим масштабированием)
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SpectatorWindow(QMainWindow):
    """Масштабируемое окно табло для зрителей"""
    
    def __init__(self, match_data):
        super().__init__()
        self.match_data = match_data
        self.setWindowTitle("Табло для зрителей - Самбо")
        
        # Окно можно свободно изменять размер
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 500)
        
        # Подключаем сигналы
        self.match_data.score_changed.connect(self.update_score)
        self.match_data.time_changed.connect(self.update_time)
        self.match_data.warning_added.connect(self.update_warnings)
        self.match_data.hold_time_changed.connect(self.update_hold_time)
        self.match_data.athlete_info_changed.connect(self.update_athlete_info)
        self.match_data.match_reset.connect(self.reset_display)
        self.match_data.match_ended.connect(self.show_winner)
        self.match_data.action_undone.connect(self.on_action_undone)
        self.match_data.joint_lock_time_changed.connect(self.update_joint_time)
        
        # Счетчики предупреждений
        self.warnings_count_1 = 0
        self.warnings_count_2 = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Таймер матча
        self.timer_label = QLabel("3:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 80px;
                font-weight: bold;
                background-color: black;
                color: white;
                padding: 10px;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.timer_label, stretch=1)
        
        # Горизонтальный layout для двух борцов
        athletes_layout = QHBoxLayout()
        athletes_layout.setSpacing(20)
        main_layout.addLayout(athletes_layout, stretch=5)
        
        # Левая секция (Красный борец)
        self.athlete1_widget = self.create_athlete_section(1, "#c0392b")
        athletes_layout.addWidget(self.athlete1_widget)
        
        # Правая секция (Синий борец)
        self.athlete2_widget = self.create_athlete_section(2, "#2980b9")
        athletes_layout.addWidget(self.athlete2_widget)
        
        # Устанавливаем равные пропорции
        athletes_layout.setStretch(0, 1)
        athletes_layout.setStretch(1, 1)
        
        # Применяем стили
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
        
    def create_athlete_section(self, athlete_num, color):
        """Создать секцию для борца"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Фамилия борца
        name_label = QLabel("Борец " + str(athlete_num))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: white;
                background-color: {color};
                padding: 8px;
                border-radius: 5px;
            }}
        """)
        setattr(self, f"name_label_{athlete_num}", name_label)
        layout.addWidget(name_label, stretch=0)
        
        # Клуб/Университет
        club_label = QLabel("")
        club_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        club_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: white;
                background-color: {color};
                padding: 5px;
            }}
        """)
        setattr(self, f"club_label_{athlete_num}", club_label)
        layout.addWidget(club_label, stretch=0)
        
        # Счет (огромные цифры - динамический размер)
        score_label = QLabel("0")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet(f"""
            QLabel {{
                font-size: 200px;
                font-weight: bold;
                color: white;
                background-color: {color};
                padding: 10px;
                border-radius: 10px;
            }}
        """)
        setattr(self, f"score_label_{athlete_num}", score_label)
        layout.addWidget(score_label, stretch=10)
        
        # ВИЗУАЛИЗАЦИЯ ПРЕДУПРЕЖДЕНИЙ (желтые квадраты)
        warnings_container = QWidget()
        warnings_layout = QHBoxLayout()
        warnings_layout.setSpacing(10)
        warnings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warnings_container.setLayout(warnings_layout)
        warnings_container.setStyleSheet(f"background-color: {color}; padding: 10px;")
        
        # Создаем 3 квадрата для предупреждений
        warning_squares = []
        for i in range(3):
            square = QLabel("")
            square.setFixedSize(40, 40)
            square.setStyleSheet("""
                QLabel {
                    background-color: #34495e;
                    border: 2px solid #7f8c8d;
                    border-radius: 5px;
                }
            """)
            warning_squares.append(square)
            warnings_layout.addWidget(square)
        setattr(self, f"warning_squares_{athlete_num}", warning_squares)
        layout.addWidget(warnings_container, stretch=0)
        
        # Удержание
        hold_label = QLabel("Удержание: 00")
        hold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hold_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: {color};
                padding: 8px;
            }}
        """)
        setattr(self, f"hold_label_{athlete_num}", hold_label)
        layout.addWidget(hold_label, stretch=0)
        
        # БОЛЕВОЙ
        joint_label = QLabel("Болевой: 00")
        joint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        joint_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: {color};
                padding: 8px;
            }}
        """)
        setattr(self, f"joint_label_{athlete_num}", joint_label)
        layout.addWidget(joint_label, stretch=0)
        
        widget.setStyleSheet(f"QWidget {{ background-color: {color}; border-radius: 10px; }}")
        return widget
    
    def resizeEvent(self, event):
        """Обработка изменения размера окна - динамическое масштабирование"""
        super().resizeEvent(event)
        self.update_score_font_sizes()
        
    def update_score_font_sizes(self):
        """Динамическое обновление размера шрифта очков"""
        # Вычисляем размер шрифта на основе высоты окна
        window_height = self.height()
        
        # Размер очков - 40% от высоты окна
        score_font_size = int(window_height * 0.6)
        score_font_size = max(80, min(score_font_size, 700))
        
        # Обновляем стили для обоих борцов
        for athlete_num in [1, 2]:
            score_label = getattr(self, f"score_label_{athlete_num}")
            color = "#c0392b" if athlete_num == 1 else "#2980b9"
            
            # Проверяем наличие золотой рамки (победитель)
            current_style = score_label.styleSheet()
            has_gold_border = "gold" in current_style
            
            border_style = "border: 8px solid gold;" if has_gold_border else ""
            
            score_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {score_font_size}px;
                    font-weight: bold;
                    color: white;
                    background-color: {color};
                    padding: 10px;
                    border-radius: 10px;
                    {border_style}
                }}
            """)
    
    def update_score(self, athlete_num, new_score):
        """Обновить счет"""
        label = getattr(self, f"score_label_{athlete_num}")
        label.setText(str(new_score))
        
    def update_time(self, time_string):
        """Обновить время"""
        self.timer_label.setText(time_string)
        
    def update_warnings(self, athlete_num, warnings_count):
        """Обновить визуализацию предупреждений (желтые квадраты)"""
        warning_squares = getattr(self, f"warning_squares_{athlete_num}")
        
        for i, square in enumerate(warning_squares):
            if i < warnings_count:
                # Активное предупреждение - желтый квадрат
                square.setStyleSheet("""
                    QLabel {
                        background-color: #f1c40f;
                        border: 3px solid #f39c12;
                        border-radius: 5px;
                    }
                """)
            else:
                # Неактивное - серый квадрат
                square.setStyleSheet("""
                    QLabel {
                        background-color: #34495e;
                        border: 2px solid #7f8c8d;
                        border-radius: 5px;
                    }
                """)
        
        # Сохраняем для внутреннего использования
        if athlete_num == 1:
            self.warnings_count_1 = warnings_count
        else:
            self.warnings_count_2 = warnings_count
            
    def update_hold_time(self, athlete_num, hold_time):
        """Обновить время удержания"""
        label = getattr(self, f"hold_label_{athlete_num}")
        label.setText(f"Удержание: {hold_time}")
        
    def update_joint_time(self, athlete_num, joint_time):
        label = getattr(self, f"joint_label_{athlete_num}")
        label.setText(f"Болевой: {joint_time}")
        
    def update_athlete_info(self, athlete_num, name, club):
        """Обновить информацию о борце"""
        name_label = getattr(self, f"name_label_{athlete_num}")
        club_label = getattr(self, f"club_label_{athlete_num}")
        
        name_label.setText(name if name else f"Борец {athlete_num}")
        club_label.setText(club)
        
    def show_winner(self, winner_num, reason):
        """Показать победителя с золотой рамкой"""
        self.update_score_font_sizes()
        
    def on_action_undone(self):
        """Обработчик отмены действия"""
        # Обновляем все элементы после отмены
        self.update_score(1, self.match_data.athlete1_score)
        self.update_score(2, self.match_data.athlete2_score)
        self.update_warnings(1, self.match_data.athlete1_warnings)
        self.update_warnings(2, self.match_data.athlete2_warnings)
        
        # Убираем золотую рамку
        self.update_score_font_sizes()
        
    def reset_display(self):
        """Сбросить отображение"""
        self.timer_label.setText("3:00")
        
        for i in [1, 2]:
            self.update_score(i, 0)
            self.update_warnings(i, 0)
            self.update_hold_time(i, "00")
            self.update_joint_time(i, "00")
            self.update_athlete_info(i, "", "")
            
        # Убрать золотую рамку
        self.update_score_font_sizes()
