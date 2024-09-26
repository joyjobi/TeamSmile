# rock_paper_scissors.py

import logging

logger = logging.getLogger(__name__)

class RockPaperScissorsGame:
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

    def handle_scoring(self, user_gesture, response_time, confidence_score):
        system_gesture = self.game_manager.prompt
        outcome = self.determine_winner(user_gesture, system_gesture)
        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.game_manager.response_timeout - response_time) / self.game_manager.response_timeout)
        round_score = (confidence_score * confidence_weight + time_score * time_weight) * 100

        logger.info(f"RockPaperScissorsGame: Outcome: {outcome}, Round Score: {round_score}")
        self.game_manager.send_ui_message("result", outcome)

        return {
            'result_text': f'{outcome}',
            'round_score': round_score
        }
