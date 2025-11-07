"""
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
        return group
    def create_global_controls(self):
        """Создать глобальные кнопки управления"""
        group = QGroupBox("Глобальное управление")
        layout = QVBoxLayout()

        # Первая строка кнопок
        row1 = QHBoxLayout()

        # КНОПКА ОТМЕНЫ (UNDO)
        undo_btn = QPushButton("↶ ОТМЕНИТЬ ПОСЛЕДНЕЕ ДЕЙСТВИЕ")
        undo_btn.clicked.connect(self.undo_last_action)
        undo_btn.setStyleSheet("""
            background-color: #9b59b6; 
            color: white; 
            font-size: 15px;
            min-height: 50px;
        """)
        self.undo_button = undo_btn
        row1.addWidget(undo_btn)

        layout.addLayout(row1)

        # Вторая строка кнопок
        row2 = QHBoxLayout()

        reset_all_btn = QPushButton("🔄 СБРОС ВСЕГО")
        reset_all_btn.clicked.connect(self.reset_all)
        reset_all_btn.setStyleSheet("""
            background-color: #e74c3c; 
            color: white; 
            font-size: 15px;
            min-height: 45px;
        """)
        row2.addWidget(reset_all_btn)

        # Кнопка завершения матча по времени
        end_match_btn = QPushButton("⏱ Завершить матч (определить победителя)")
        end_match_btn.clicked.connect(self.end_match_and_determine_winner)
        end_match_btn.setStyleSheet("""
            background-color: #16a085; 
            color: white; 
            font-size: 14px;
            min-height: 45px;
        """)
        row2.addWidget(end_match_btn)

        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    # === Обработчики событий ===

    def start_match_timer(self):
        """Запустить таймер матча"""
        if not self.match_running and not self.match_data.match_is_over:
            self.match_running = True
            self.match_timer.start(1000)

    def pause_match_timer(self):
        """Поставить на паузу"""
        self.match_running = False
        self.match_timer.stop()

    def reset_match_timer(self):
        """Сбросить таймер"""
        self.match_running = False
        self.match_timer.stop()
        self.match_data.match_seconds = 300
        self.match_data.update_time("5:00", 300)
        self.timer_display.setText("5:00")

    def update_match_timer(self):
        """Обновить таймер матча"""
        if self.match_data.match_seconds > 0:
            self.match_data.match_seconds -= 1
            mins = self.match_data.match_seconds // 60
            secs = self.match_data.match_seconds % 60
            time_str = f"{mins}:{secs:02d}"
            self.timer_display.setText(time_str)
            self.match_data.update_time(time_str, self.match_data.match_seconds)
        else:
            # Время вышло - автоматически определяем победителя
            self.pause_match_timer()
            self.end_match_and_determine_winner()

    def add_points(self, athlete_num, points):
        """Добавить очки с проверкой правил FIAS"""
        if self.match_data.match_is_over:
            # БЕЗ ВСПЛЫВАЮЩЕГО ОКНА - просто игнорируем
            return

        # Начисляем очки с проверкой правил
        victory = self.match_data.update_score(athlete_num, points)

        # Обновить отображение
        if athlete_num == 1:
            score = self.match_data.athlete1_score
        else:
            score = self.match_data.athlete2_score

        score_display = getattr(self, f"score_display_{athlete_num}")
        score_display.setText(f"Счет: {score}")

        if victory:
            # Остановить таймер при досрочной победе
            self.pause_match_timer()

    def add_warning(self, athlete_num):
        """Добавить предупреждение (БЕЗ ВСПЛЫВАЮЩИХ УВЕДОМЛЕНИЙ)"""
        if self.match_data.match_is_over:
            return

        # Получаем текущее количество предупреждений
        if athlete_num == 1:
            current_warnings = self.match_data.athlete1_warnings
        else:
            current_warnings = self.match_data.athlete2_warnings

        # Проверка на 4-е предупреждение
        if current_warnings >= 3:
            # Дисквалификация - показываем только подтверждение
            reply = QMessageBox.question(
                self,
                "Дисквалификация",
                f"У борца {athlete_num} уже 3 предупреждения.\n"
                f"4-е предупреждение приведет к дисквалификации.\n\n"
                f"Подтвердите дисквалификацию.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.match_data.disqualify_athlete(athlete_num)
                self.pause_match_timer()
            return

        # Добавляем предупреждение (очки начисляются автоматически)
        result = self.match_data.add_warning(athlete_num)

        if result == True:
            warnings = current_warnings + 1

            # Обновляем дисплей предупреждений
            warning_display = getattr(self, f"warning_display_{athlete_num}")
            warning_display.setText(f"Предупреждения: {warnings}/3")

            # Обновляем счет соперника (очки уже начислены в match_data)
            opponent = 3 - athlete_num
            if opponent == 1:
                score = self.match_data.athlete1_score
            else:
                score = self.match_data.athlete2_score

            score_display = getattr(self, f"score_display_{opponent}")
            score_display.setText(f"Счет: {score}")

            # БЕЗ ВСПЛЫВАЮЩИХ УВЕДОМЛЕНИЙ - только обновляем UI

    def toggle_hold(self, athlete_num):
        """Переключить удержание"""
        if athlete_num == 1:
            if not self.hold_running_1:
                self.hold_running_1 = True
                self.hold_timer_1.start(1000)
                self.hold_button_1.setText("⏹ Остановить удержание")
                self.hold_button_1.setStyleSheet("background-color: #e74c3c; color: white;")
            else:
                self.hold_running_1 = False
                self.hold_timer_1.stop()
                self.hold_button_1.setText("⏱ Начать удержание")
                self.hold_button_1.setStyleSheet("background-color: #c0392b; color: white;")
                # Сброс удержания
                self.match_data.athlete1_hold_time = 0
                self.match_data.update_hold_time(1, 0)
                self.hold_display_1.setText("Удержание: 00 сек")
        else:
            if not self.hold_running_2:
                self.hold_running_2 = True
                self.hold_timer_2.start(1000)
                self.hold_button_2.setText("⏹ Остановить удержание")
                self.hold_button_2.setStyleSheet("background-color: #e74c3c; color: white;")
            else:
                self.hold_running_2 = False
                self.hold_timer_2.stop()
                self.hold_button_2.setText("⏱ Начать удержание")
                self.hold_button_2.setStyleSheet("background-color: #2980b9; color: white;")
                self.match_data.athlete2_hold_time = 0
                self.match_data.update_hold_time(2, 0)
                self.hold_display_2.setText("Удержание: 00 сек")

    def update_hold_timer(self, athlete_num):
        """Обновить таймер удержания (БЕЗ ВСПЛЫВАЮЩИХ УВЕДОМЛЕНИЙ)"""
        if athlete_num == 1:
            hold_time = self.match_data.athlete1_hold_time + 1
            self.match_data.update_hold_time(1, hold_time)
            self.hold_display_1.setText(f"Удержание: {hold_time:02d} сек")

            # Автоматическое начисление очков БЕЗ УВЕДОМЛЕНИЙ
            if hold_time == 10:
                self.add_points(1, 2)
            elif hold_time == 20:
                self.toggle_hold(1)
                self.pause_match_timer()
        else:
            hold_time = self.match_data.athlete2_hold_time + 1
            self.match_data.update_hold_time(2, hold_time)
            self.hold_display_2.setText(f"Удержание: {hold_time:02d} сек")

            if hold_time == 10:
                self.add_points(2, 2)
            elif hold_time == 20:
                self.toggle_hold(2)
                self.pause_match_timer()

    def update_athlete_name(self, athlete_num, name):
        """Обновить имя борца"""
        if athlete_num == 1:
            club = self.match_data.athlete1_club
        else:
            club = self.match_data.athlete2_club

        self.match_data.update_athlete_info(athlete_num, name, club)

    def update_athlete_club(self, athlete_num, club):
        """Обновить клуб борца"""
        if athlete_num == 1:
            name = self.match_data.athlete1_name
        else:
            name = self.match_data.athlete2_name

        self.match_data.update_athlete_info(athlete_num, name, club)
    def declare_victory(self, athlete_num):
        """Объявить победу вручную"""
        if athlete_num == 1:
            name = self.match_data.athlete1_name or "Борец 1"
        else:
            name = self.match_data.athlete2_name or "Борец 2"

        reply = QMessageBox.question(
            self,
            "Подтверждение победы",
            f"Объявить {name} победителем?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.match_data.match_is_over = True
            self.match_data.match_ended.emit(athlete_num, "Победа по решению судей")
            self.pause_match_timer()

            QMessageBox.information(
                self,
                "ПОБЕДА!",
                f"🏆 {name} одержал победу! 🏆",
                QMessageBox.StandardButton.Ok
            )

    def end_match_and_determine_winner(self):
        """Завершить матч и определить победителя по правилам FIAS"""
        if self.match_data.match_is_over:
            return

        self.pause_match_timer()

        winner_num, reason = self.match_data.get_winner_at_end()

        if winner_num == 0:
            # Ничья - требуется судейское решение
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("Ничья - Требуется решение")
            msg.setText("Матч завершился с абсолютно равными показателями.\n\n"
                       "Выберите победителя:")
            msg.addButton("Борец 1", QMessageBox.ButtonRole.YesRole)
            msg.addButton("Борец 2", QMessageBox.ButtonRole.NoRole)
            msg.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

            result = msg.exec()

            if result == 0:
                winner_num = 1
                reason = "Победа по решению судей (после ничьей)"
            elif result == 1:
                winner_num = 2
                reason = "Победа по решению судей (после ничьей)"
            else:
                return

        # Объявляем победителя
        self.match_data.match_is_over = True
        self.match_data.match_ended.emit(winner_num, reason)

        winner_name = self.match_data.athlete1_name if winner_num == 1 else self.match_data.athlete2_name
        if not winner_name:
            winner_name = f"Борец {winner_num}"

        QMessageBox.information(
            self,
            "МАТЧ ЗАВЕРШЕН",
            f"🏆 ПОБЕДИТЕЛЬ: {winner_name}\n\n{reason}",
            QMessageBox.StandardButton.Ok
        )

    def undo_last_action(self):
        """ОТМЕНИТЬ ПОСЛЕДНЕЕ ДЕЙСТВИЕ"""
        success = self.match_data.undo_last_action()

        if not success:
            # НЕТ действий для отмены - можно показать сообщение в статус-баре
            # но не всплывающее окно
            return

        # Обновляем UI после отмены
        self.refresh_all_displays()

    def on_action_undone(self):
        """Обработчик сигнала отмены действия"""
        self.refresh_all_displays()

    def refresh_all_displays(self):
        """Обновить все дисплеи после отмены"""
        # Обновляем счета
        for i in [1, 2]:
            score = self.match_data.athlete1_score if i == 1 else self.match_data.athlete2_score
            score_display = getattr(self, f"score_display_{i}")
            score_display.setText(f"Счет: {score}")

            warnings = self.match_data.athlete1_warnings if i == 1 else self.match_data.athlete2_warnings
            warning_display = getattr(self, f"warning_display_{i}")
            warning_display.setText(f"Предупреждения: {warnings}/3")

    def on_match_ended(self, winner_num, reason):
        """Обработчик сигнала окончания матча"""
        # Останавливаем все таймеры
        self.pause_match_timer()
        if self.hold_running_1:
            self.toggle_hold(1)
        if self.hold_running_2:
            self.toggle_hold(2)

    def reset_all(self):
        """Сбросить все данные"""
        reply = QMessageBox.question(
            self,
            "Подтверждение сброса",
            "Сбросить все данные матча?\n\nЭто действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.match_data.reset_all()

        # Сбросить UI
        self.reset_match_timer()

        for i in [1, 2]:
            score_display = getattr(self, f"score_display_{i}")
            score_display.setText("Счет: 0")

            warning_display = getattr(self, f"warning_display_{i}")
            warning_display.setText("Предупреждения: 0/3")

            hold_display = getattr(self, f"hold_display_{i}")
            hold_display.setText("Удержание: 00 сек")

            name_input = getattr(self, f"name_input_{i}")
            name_input.clear()

            club_input = getattr(self, f"club_input_{i}")
            club_input.clear()

            # Сброс кнопок удержания
            hold_button = getattr(self, f"hold_button_{i}")
            hold_button.setText("⏱ Начать удержание")
            color = "#c0392b" if i == 1 else "#2980b9"
            hold_button.setStyleSheet(f"background-color: {color}; color: white;")

        # Остановить удержания
        if self.hold_running_1:
            self.hold_running_1 = False
            self.hold_timer_1.stop()
        if self.hold_running_2:
            self.hold_running_2 = False
            self.hold_timer_2.stop()
