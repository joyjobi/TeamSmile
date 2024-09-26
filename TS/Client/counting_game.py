# counting_game.py

import logging

logger = logging.getLogger(__name__)

class CountingGame:
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def handle_scoring(self, user_gesture, response_time, confidence_score):
        try:
            user_number = int(user_gesture)
        except ValueError:
            logger.warning("CountingGame: Invalid input received.")
            return {
                'result_text': 'Invalid input.',
                'round_score': 0
            }

        target_number = self.game_manager.prompt
        correctness = 'Correct!' if user_number == target_number else f'Incorrect! Target was {target_number}'
        base_score = 100 if user_number == target_number else 0

        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.game_manager.response_timeout - response_time) / self.game_manager.response_timeout)
        round_score = (confidence_score * confidence_weight + time_score * time_weight) * base_score / 100

        logger.info(f"CountingGame: Outcome: {correctness}, Round Score: {round_score}")

        return {
            'result_text': f'{correctness}',
            'round_score': round_score
        }
