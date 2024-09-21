# game_logic.py

import time
import random
import game_manager

class Game:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.score = 0
        self.total_games = 0

    def start_new_round(self):
        pass

    def update(self, user_gesture, gesture_confidence):
        pass

    def get_display_text(self, user_gesture):
        pass

class RockPaperScissorsGame(Game):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.system_gesture = None
        self.game_start_time = None
        self.response_time = None
        self.game_state = 'waiting'  # 'waiting', 'prompted', 'responded'
        self.confidence_weight = 0.7
        self.time_weight = 0.3
        self.prompt_interval = 5  # Time between prompts in seconds
        self.response_timeout = self.game_manager.response_timeout
        self.last_prompt_time = time.time() - self.prompt_interval  # Ensure immediate prompt on start
        self.result_text = ''
        self.round_score = 0
        self.screen_width = 640  # Set screen width (adjust if needed)
        self.screen_height = 480  # Set screen height (adjust if needed)
        self.gestures = ['Rock', 'Paper', 'Scissors']  # Define gestures

    def start_new_round(self):
        self.system_gesture = random.choice(self.gestures)
        self.game_start_time = time.time()
        self.response_time = None
        self.game_state = 'prompted'
        print(f"System Gesture: {self.system_gesture}")  # For debugging

    def determine_winner(self, player_gesture):
        system_gesture = self.system_gesture
        if player_gesture == system_gesture:
            return 'Tie'
        elif (player_gesture == 'Rock' and system_gesture == 'Scissors') or \
             (player_gesture == 'Paper' and system_gesture == 'Rock') or \
             (player_gesture == 'Scissors' and system_gesture == 'Paper'):
            return 'You Win!'
        else:
            return 'You Lose!'

    def update(self, user_gesture, gesture_confidence):
        current_time = time.time()

        # Start a new round if needed
        if self.game_state == 'waiting' and current_time - self.last_prompt_time >= self.prompt_interval:
            self.start_new_round()
            self.last_prompt_time = current_time

        # Game Logic
        if self.game_state == 'prompted':
            # Check if user has responded within the timeout
            if user_gesture in self.gestures:
                self.response_time = current_time - self.game_start_time
                if self.response_time <= self.response_timeout:
                    # Calculate score
                    confidence_score = gesture_confidence  # Between 0 and 1
                    time_score = max(0, (self.response_timeout - self.response_time) / self.response_timeout)
                    self.round_score = (confidence_score * self.confidence_weight + time_score * self.time_weight) * 100  # Weighted score
                    self.score += self.round_score
                    self.total_games += 1

                    # Determine winner
                    result = self.determine_winner(user_gesture)
                    self.result_text = f'{result} | Score: {self.round_score:.1f}'
                else:
                    self.result_text = 'Too Slow!'
                    self.total_games += 1
                self.game_state = 'responded'
            elif current_time - self.game_start_time > self.response_timeout:
                self.result_text = 'No Response!'
                self.total_games += 1
                self.game_state = 'responded'

        elif self.game_state == 'responded':
            # Display result for a while before starting a new round
            if current_time - self.game_start_time > self.response_timeout + 2:
                self.game_state = 'waiting'

    def get_display_text(self, user_gesture):
        texts = []
        # Font settings
        font_scale = 0.9  # Slightly larger font for clarity
        font_thickness = 2  # Thicker font for crispness

        # Define column positions
        col1_x = 10
        col2_x = int(self.screen_width * 0.6)

        # System gesture in the first column
        if self.game_state in ['prompted', 'responded']:
            texts.append(('System: ' + self.system_gesture, (col1_x, 30), (0, 0, 0), font_scale, font_thickness))

        # User's gesture in the second column
        texts.append(('You: ' + user_gesture, (col2_x, 30), (0, 0, 0), font_scale, font_thickness))

        # Result text centered below the gestures
        if self.game_state == 'responded':
            texts.append((self.result_text, (int(self.screen_width / 2) - 100, 80), (0, 0, 0), font_scale, font_thickness))

        # Time left displayed below the result text, centered
        if self.game_state == 'prompted':
            time_left = max(0, int(self.response_timeout - (time.time() - self.game_start_time)))
            texts.append((f'Time Left: {time_left}s', (int(self.screen_width / 2) - 80, 120), (0, 0, 0), font_scale, font_thickness))

            # Flashing "New Round!" text below the time left
            if int(time.time() * 2) % 2 == 0:
                texts.append(('New Round!', (int(self.screen_width / 2) - 80, 160), (0, 0, 0), font_scale, font_thickness))

        return texts


class HandGestureCountingGame(Game):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.target_number = None
        self.game_start_time = None
        self.response_time = None
        self.game_state = 'waiting'  # 'waiting', 'prompted', 'responded'
        self.confidence_weight = 0.7
        self.time_weight = 0.3
        self.prompt_interval = 5  # Time between prompts in seconds
        self.response_timeout = 5  # Time allowed for user response in seconds
        self.last_prompt_time = time.time() - self.prompt_interval  # Ensure immediate prompt on start
        self.result_text = ''
        self.round_score = 0
        self.screen_width = 640  # Set screen width (adjust if needed)
        self.screen_height = 480  # Set screen height (adjust if needed)

    def start_new_round(self):
        self.game_manager.start_new_round()
        self.target_number = self.game_manager.prompt
        self.game_start_time = time.time()
        self.response_time = None
        self.game_state = 'prompted'
        print(f"Target Number: {self.target_number}")  # For debugging

    def update(self, user_gesture, gesture_confidence):
        current_time = time.time()

        # Start a new round if needed
        if self.game_state == 'waiting' and current_time - self.last_prompt_time >= self.prompt_interval:
            self.start_new_round()
            self.last_prompt_time = current_time

        # Game Logic
        if self.game_state == 'prompted':
            # Check if user has responded within the timeout
            if user_gesture.isdigit():
               
                # Calculate response time
                self.response_time = time.time() - self.game_start_time
                result = self.game_manager.submit_response(
                    user_gesture, self.response_time, gesture_confidence)
                # Handle result
                self.result_text = result['result_text']
                self.round_score = result['round_score']
                self.score += self.round_score
                self.total_games += 1
                self.game_state = 'responded'

                if self.response_time <= self.response_timeout:
                    # Calculate score
                    confidence_score = gesture_confidence  # Between 0 and 1
                    time_score = max(0, (self.response_timeout - self.response_time) / self.response_timeout)
                    self.round_score = (confidence_score * self.confidence_weight + time_score * self.time_weight) * 100  # Weighted score

                    # Determine correctness
                    if int(user_gesture) == self.target_number:
                        self.result_text = f'Correct! | Score: {self.round_score:.1f}'
                        self.score += self.round_score
                    else:
                        self.result_text = f'Incorrect! Target was {self.target_number}'
                    self.total_games += 1
                else:
                    self.result_text = 'Too Slow!'
                    self.total_games += 1
                self.game_state = 'responded'
            elif current_time - self.game_start_time > self.response_timeout:
                self.result_text = f'No Response! Target was {self.target_number}'
                self.total_games += 1
                self.game_state = 'responded'

        elif self.game_state == 'responded':
            # Display result for a while before starting a new round
            if current_time - self.game_start_time > self.response_timeout + 2:
                self.game_state = 'waiting'

    def get_display_text(self, user_gesture):
        texts = []
        # Font settings
        font_scale = 0.9  # Slightly larger font for clarity
        font_thickness = 2  # Thicker font for crispness

        # Define column positions
        col1_x = 10
        col2_x = int(self.screen_width * 0.6)

        # Target number in the first column
        if self.game_state in ['prompted', 'responded']:
            texts.append((f'Show: {self.target_number}', (col1_x, 30), (0, 0, 0), font_scale, font_thickness))

        # User's input in the second column
        texts.append((f'You: {user_gesture}', (col2_x, 30), (0, 0, 0), font_scale, font_thickness))

        # Result text centered below the gestures
        if self.game_state == 'responded':
            texts.append((self.result_text, (int(self.screen_width / 2) - 100, 80), (0, 0, 0), font_scale, font_thickness))

        # Time left displayed below the result text, centered
        if self.game_state == 'prompted':
            time_left = max(0, int(self.response_timeout - (time.time() - self.game_start_time)))
            texts.append((f'Time Left: {time_left}s', (int(self.screen_width / 2) - 80, 120), (0, 0, 0), font_scale, font_thickness))

            # Flashing "New Round!" text below the time left
            if int(time.time() * 2) % 2 == 0:
                texts.append(('New Round!', (int(self.screen_width / 2) - 80, 160), (0, 0, 0), font_scale, font_thickness))

        return texts