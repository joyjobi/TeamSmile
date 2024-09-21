# game_manager.py

class GameManager:
    def __init__(self, game_type, network_client=None):
        self.game_type = game_type  # 'rps' or 'counting'
        self.network_client = network_client
        self.is_networked = network_client is not None
        self.prompt = None
        self.round_score = 0
        # Define response_timeout
        if game_type == 'rps':
            self.response_timeout = 3  # seconds
        elif game_type == 'counting':
            self.response_timeout = 5  # seconds

    def start_new_round(self):
        if self.is_networked:
            # Request a new prompt from the server
            self.prompt = self.network_client.get_prompt()
        else:
            # Generate prompt locally
            if self.game_type == 'rps':
                self.prompt = self.get_local_rps_prompt()
            elif self.game_type == 'counting':
                self.prompt = self.get_local_counting_prompt()

    def get_local_rps_prompt(self):
        import random
        return random.choice(['Rock', 'Paper', 'Scissors'])

    def get_local_counting_prompt(self):
        import random
        return random.randint(1, 5)

    def submit_response(self, user_gesture, response_time, confidence_score):
        if self.is_networked:
            # Send response to the server and get the result
            result = self.network_client.submit_response(user_gesture, response_time, confidence_score)
            self.round_score = result['round_score']
            return result
        else:
            # Handle scoring locally
            if self.game_type == 'rps':
                return self.handle_local_rps_scoring(user_gesture, response_time, confidence_score)
            elif self.game_type == 'counting':
                return self.handle_local_counting_scoring(user_gesture, response_time, confidence_score)

    def handle_local_rps_scoring(self, user_gesture, response_time, confidence_score):
        system_gesture = self.prompt
        if user_gesture == system_gesture:
            outcome = 'Tie'
        elif (user_gesture == 'Rock' and system_gesture == 'Scissors') or \
            (user_gesture == 'Paper' and system_gesture == 'Rock') or \
            (user_gesture == 'Scissors' and system_gesture == 'Paper'):
            outcome = 'You Win!'
        else:
            outcome = 'You Lose!'

        # Calculate score
        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.response_timeout - response_time) / self.response_timeout)
        self.round_score = (confidence_score * confidence_weight + time_score * time_weight) * 100

        return {
            'result_text': f'{outcome} | Score: {self.round_score:.1f}',
            'round_score': self.round_score
        }

    def handle_local_counting_scoring(self, user_gesture, response_time, confidence_score):
        target_number = self.prompt
        if int(user_gesture) == target_number:
            correctness = 'Correct!'
            score_increment = 100
        else:
            correctness = f'Incorrect! Target was {target_number}'
            score_increment = 0

        # Calculate score
        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.response_timeout - response_time) / self.response_timeout)
        self.round_score = (confidence_score * confidence_weight + time_score * time_weight) * score_increment / 100

        return {
            'result_text': f'{correctness} | Score: {self.round_score:.1f}',
            'round_score': self.round_score
        }