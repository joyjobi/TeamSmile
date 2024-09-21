# game_logic.py

import time  # Importing the time module
from collections import deque, Counter

class Game:
    # Base Game class (assuming it exists)
    pass

class RockPaperScissorsGame(Game):
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def determine_winner(self, player_gesture, system_gesture):
        if player_gesture == system_gesture:
            return 'Tie'
        elif (player_gesture == 'Rock' and system_gesture == 'Scissors') or \
             (player_gesture == 'Paper' and system_gesture == 'Rock') or \
             (player_gesture == 'Scissors' and system_gesture == 'Paper'):
            return 'You Win!'
        else:
            return 'You Lose!'

    def calculate_score(self, correctness, response_time, confidence_score):
        if correctness == 'You Win!':
            base_score = 100
        elif correctness == 'Tie':
            base_score = 50
        else:
            base_score = 0

        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.game_manager.response_timeout - response_time) / self.game_manager.response_timeout)
        score = (confidence_score * confidence_weight + time_score * time_weight) * base_score / 100
        return score

    def get_display_text(self, user_gesture, system_gesture, result_text, response_timeout, response_time):
        texts = []
        # Define column positions
        screen_width = 640
        col1_x = 10
        col2_x = int(screen_width * 0.6)

        # System gesture
        texts.append((f'System: {system_gesture}', (col1_x, 30), (0, 0, 0), 0.9, 2))

        # User gesture
        texts.append((f'You: {user_gesture}', (col2_x, 30), (0, 0, 0), 0.9, 2))

        # Result text
        texts.append((result_text, (int(screen_width / 2) - 100, 80), (0, 0, 0), 0.9, 2))

        # Time left
        time_left = max(0, int(response_timeout - response_time))
        texts.append((f'Time Left: {time_left}s', (int(screen_width / 2) - 80, 120), (0, 0, 0), 0.9, 2))

        # Flashing "New Round!" text
        if int(time.time() * 2) % 2 == 0:
            texts.append(('New Round!', (int(screen_width / 2) - 80, 160), (0, 0, 0), 0.9, 2))

        return texts

class HandGestureCountingGame(Game):
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def determine_correctness(self, user_gesture, target_number):
        try:
            user_number = int(user_gesture)
        except ValueError:
            return 'Invalid input!', 0

        if user_number == target_number:
            return 'Correct!', 100
        else:
            return f'Incorrect! Target was {target_number}', 0

    def calculate_score(self, correctness, response_time, confidence_score):
        if correctness == 'Correct!':
            base_score = 100
        elif correctness.startswith('Incorrect'):
            base_score = 0
        else:
            base_score = 0

        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.game_manager.response_timeout - response_time) / self.game_manager.response_timeout)
        score = (confidence_score * confidence_weight + time_score * time_weight) * base_score / 100
        return score

    def get_display_text(self, user_gesture, target_number, result_text, response_timeout, response_time):
        texts = []
        # Define column positions
        screen_width = 640
        col1_x = 10
        col2_x = int(screen_width * 0.6)

        # Target number
        texts.append((f'Show: {target_number}', (col1_x, 30), (0, 0, 0), 0.9, 2))

        # User gesture
        texts.append((f'You: {user_gesture}', (col2_x, 30), (0, 0, 0), 0.9, 2))

        # Result text
        texts.append((result_text, (int(screen_width / 2) - 100, 80), (0, 0, 0), 0.9, 2))

        # Time left
        time_left = max(0, int(response_timeout - response_time))
        texts.append((f'Time Left: {time_left}s', (int(screen_width / 2) - 80, 120), (0, 0, 0), 0.9, 2))

        # Flashing "New Round!" text
        if int(time.time() * 2) % 2 == 0:
            texts.append(('New Round!', (int(screen_width / 2) - 80, 160), (0, 0, 0), 0.9, 2))

        return texts
