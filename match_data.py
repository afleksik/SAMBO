"""
Модель данных для матча самбо с логикой правил FIAS и историей действий
"""
from PyQt6.QtCore import QObject, pyqtSignal


class MatchAction:
    """Класс для хранения действия (для отмены)"""
    def __init__(self, action_type, athlete_num, value, prev_state):
        self.action_type = action_type  # 'score', 'warning', 'hold', etc.
        self.athlete_num = athlete_num
        self.value = value
        self.prev_state = prev_state  # Предыдущее состояние для восстановления


class MatchData(QObject):
    """Класс для хранения и синхронизации данных матча с применением правил FIAS"""

    # Сигналы для обновления UI
    score_changed = pyqtSignal(int, int)  # athlete_num, new_score
    time_changed = pyqtSignal(str)  # time_string
    warning_added = pyqtSignal(int, int)  # athlete_num, warnings_count
    hold_time_changed = pyqtSignal(int, str)  # athlete_num, hold_time
    joint_lock_time_changed = pyqtSignal(int, str) 
    athlete_info_changed = pyqtSignal(int, str, str)  # athlete_num, name, club
    match_reset = pyqtSignal()
    match_ended = pyqtSignal(int, str)  # winner_num, reason
    action_undone = pyqtSignal()  # Сигнал отмены действия

    def __init__(self):
        super().__init__()

        # Данные борцов
        self.athlete1_name = ""
        self.athlete1_club = ""
        self.athlete1_score = 0
        self.athlete1_warnings = 0
        self.athlete1_hold_time = 0

        self.athlete2_name = ""
        self.athlete2_club = ""
        self.athlete2_score = 0
        self.athlete2_warnings = 0
        self.athlete2_hold_time = 0
        self.athlete1_joint_time = 0
        self.athlete2_joint_time = 0
        # Время матча
        self.match_time = "3:00"
        self.match_seconds = 180

        # Флаг окончания матча
        self.match_is_over = False

        # История действий для отмены
        self.action_history = []

    def update_joint_time(self, athlete_num, seconds):
        if athlete_num == 1:
            self.athlete1_joint_time = seconds
        else:
            self.athlete2_joint_time = seconds
        self.joint_lock_time_changed.emit(athlete_num, f"{seconds:02d}")

    def save_state(self):
        """Сохранить текущее состояние для возможности отмены"""
        return {
            'athlete1_score': self.athlete1_score,
            'athlete2_score': self.athlete2_score,
            'athlete1_warnings': self.athlete1_warnings,
            'athlete2_warnings': self.athlete2_warnings,
            'athlete1_hold_time': self.athlete1_hold_time,
            'athlete2_hold_time': self.athlete2_hold_time,
            'match_is_over': self.match_is_over
        }

    def restore_state(self, state):
        """Восстановить состояние"""
        self.athlete1_score = state['athlete1_score']
        self.athlete2_score = state['athlete2_score']
        self.athlete1_warnings = state['athlete1_warnings']
        self.athlete2_warnings = state['athlete2_warnings']
        self.athlete1_hold_time = state['athlete1_hold_time']
        self.athlete2_hold_time = state['athlete2_hold_time']
        self.match_is_over = state['match_is_over']

    def add_action(self, action_type, athlete_num, value):
        """Добавить действие в историю"""
        prev_state = self.save_state()
        action = MatchAction(action_type, athlete_num, value, prev_state)
        self.action_history.append(action)

        # Ограничиваем историю 20 последними действиями
        if len(self.action_history) > 20:
            self.action_history.pop(0)

    def undo_last_action(self):
        """Отменить последнее действие"""
        if not self.action_history:
            return False

        last_action = self.action_history.pop()
        self.restore_state(last_action.prev_state)

        # Испускаем сигналы обновления для всех элементов
        self.score_changed.emit(1, self.athlete1_score)
        self.score_changed.emit(2, self.athlete2_score)
        self.warning_added.emit(1, self.athlete1_warnings)
        self.warning_added.emit(2, self.athlete2_warnings)
        self.action_undone.emit()

        return True

    def update_score(self, athlete_num, points):
        """Обновить счет борца с проверкой правил FIAS"""
        if self.match_is_over:
            return False

        # Сохраняем действие
        self.add_action('score', athlete_num, points)

        if athlete_num == 1:
            self.athlete1_score += points
            self.score_changed.emit(1, self.athlete1_score)
            current_score = self.athlete1_score
            opponent_score = self.athlete2_score
        else:
            self.athlete2_score += points
            self.score_changed.emit(2, self.athlete2_score)
            current_score = self.athlete2_score
            opponent_score = self.athlete1_score

        # Проверка тотальной победы по разнице очков (12+ очков)
        score_diff = abs(current_score - opponent_score)
        if score_diff >= 12:
            self.match_is_over = True
            winner = athlete_num if current_score > opponent_score else (3 - athlete_num)
            self.match_ended.emit(winner, "Тотальная победа (превосходство 12+ очков)")
            return True

        return False

    def add_warning(self, athlete_num):
        """Добавить предупреждение с учетом правил FIAS"""
        if self.match_is_over:
            return False

        # Сохраняем действие
        self.add_action('warning', athlete_num, 1)

        if athlete_num == 1:
            if self.athlete1_warnings >= 3:
                return "disqualify"
            self.athlete1_warnings += 1
            warnings_count = self.athlete1_warnings
            opponent = 2
        else:
            if self.athlete2_warnings >= 3:
                return "disqualify"
            self.athlete2_warnings += 1
            warnings_count = self.athlete2_warnings
            opponent = 1

        self.warning_added.emit(athlete_num, warnings_count)

        # Начисление очков сопернику согласно правилам FIAS
        if warnings_count == 1:
            bonus_points = 1
        elif warnings_count == 2:
            bonus_points = 2
        elif warnings_count == 3:
            bonus_points = 1
        else:
            bonus_points = 0

        if bonus_points > 0:
            # НЕ добавляем в историю, т.к. это часть текущего действия
            if opponent == 1:
                self.athlete1_score += bonus_points
                self.score_changed.emit(1, self.athlete1_score)
            else:
                self.athlete2_score += bonus_points
                self.score_changed.emit(2, self.athlete2_score)

        return True

    def disqualify_athlete(self, athlete_num):
        """Дисквалифицировать борца (4-е предупреждение)"""
        self.match_is_over = True
        winner = 3 - athlete_num
        self.match_ended.emit(winner, f"Дисквалификация борца {athlete_num}")
        return True

    def check_hold_down_points(self, athlete_num, hold_seconds):
        """Проверить начисление очков за удержание"""
        if hold_seconds == 10:
            self.update_score(athlete_num, 2)
        elif hold_seconds == 20:
            self.update_score(athlete_num, 4)
            self.match_is_over = True
            self.match_ended.emit(athlete_num, "Тотальная победа (удержание 20 сек)")
            return True
        return False

    def update_time(self, time_string, seconds):
        """Обновить время матча"""
        self.match_time = time_string
        self.match_seconds = seconds
        self.time_changed.emit(time_string)

    def update_hold_time(self, athlete_num, hold_seconds):
        """Обновить время удержания с проверкой правил"""
        if athlete_num == 1:
            self.athlete1_hold_time = hold_seconds
        else:
            self.athlete2_hold_time = hold_seconds
        self.hold_time_changed.emit(athlete_num, f"{hold_seconds:02d}")

        # Проверка начисления очков за удержание
        self.check_hold_down_points(athlete_num, hold_seconds)

    def update_athlete_info(self, athlete_num, name, club):
        """Обновить информацию о борце"""
        if athlete_num == 1:
            self.athlete1_name = name
            self.athlete1_club = club
        else:
            self.athlete2_name = name
            self.athlete2_club = club
        self.athlete_info_changed.emit(athlete_num, name, club)

    def reset_all(self):
        """Сбросить все данные"""
        self.athlete1_score = 0
        self.athlete2_score = 0
        self.athlete1_warnings = 0
        self.athlete2_warnings = 0
        self.athlete1_hold_time = 0
        self.athlete2_hold_time = 0
        self.match_seconds = 180
        self.match_time = "3:00"
        self.match_is_over = False
        self.action_history = []  # Очистить историю
        self.match_reset.emit()         # не сомнительная темка, соединяет сигналом с
                                        # обновлением зрительского экрана!!!! TODO
        self.athlete1_joint_time = 0
        self.athlete2_joint_time = 0

    def get_winner_at_end(self):
        """Определить победителя по окончанию времени согласно правилам FIAS"""
        score_diff = abs(self.athlete1_score - self.athlete2_score)

        if score_diff >= 8:
            winner = 1 if self.athlete1_score > self.athlete2_score else 2
            return winner, "Победа по преимуществу (8-11 очков)"
        elif score_diff >= 1:
            winner = 1 if self.athlete1_score > self.athlete2_score else 2
            return winner, "Победа по очкам"
        else:
            if self.athlete1_warnings < self.athlete2_warnings:
                return 1, "Победа по меньшему количеству предупреждений"
            elif self.athlete2_warnings < self.athlete1_warnings:
                return 2, "Победа по меньшему количеству предупреждений"
            else:
                return 0, "Ничья - требуется судейское решение"
