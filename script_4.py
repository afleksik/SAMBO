
# Финальная часть судейского окна (часть 3)
judge_window_final_p3 = '''
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
            msg.setText("Матч завершился с абсолютно равными показателями.\\n\\n"
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
            f"🏆 ПОБЕДИТЕЛЬ: {winner_name}\\n\\n{reason}",
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
            "Сбросить все данные матча?\\n\\nЭто действие необратимо.",
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
'''

# Объединяем все части
full_judge = judge_window_final_p1 + judge_window_final_p2 + judge_window_final_p3

with open('judge_window.py', 'w', encoding='utf-8') as f:
    f.write(full_judge)

print("✓ Создан файл: judge_window.py")
print("  - Добавлена кнопка ОТМЕНЫ ДЕЙСТВИЯ (фиолетовая)")
print("  - УБРАНЫ все всплывающие уведомления при предупреждениях")
print("  - УБРАНЫ уведомления при удержании 10/20 секунд")
print("  - Окно полностью масштабируемое")
print("  - Остались только критичные подтверждения (дисквалификация, победа)")
