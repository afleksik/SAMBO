
# Продолжаем судейское окно (часть 2)
judge_window_final_p2 = '''
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
                f"У борца {athlete_num} уже 3 предупреждения.\\n"
                f"4-е предупреждение приведет к дисквалификации.\\n\\n"
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
        
        self.match_data.update_athlete_info(athlete_num, name, club)'''

print("Создание судейского окна (часть 2)...")
