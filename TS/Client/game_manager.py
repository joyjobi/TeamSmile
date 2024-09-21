# game_manager.py

import asyncio
import random
import time

class GameManager:
    def __init__(self, game_type, network_client=None, mode='networked'):
        """
        Initialize the GameManager.

        :param game_type: 'rps' or 'counting'
        :param network_client: Instance of NetworkClient for networked mode
        :param mode: 'networked', 'local', or 'self-play'
        """
        self.game_type = game_type  # 'rps' or 'counting'
        self.network_client = network_client
        self.mode = mode  # 'networked', 'local', 'self-play'
        self.is_networked = self.mode == 'networked' and network_client is not None
        self.prompt = None
        self.round_score = 0
        self.result_text = 'N/A'  # Initialize result_text
        self.current_round = 0
        self.total_rounds = 5  # Default number of rounds
        self.score = 0
        self.game_state = 'waiting'  # 'waiting', 'prompted', 'responded'

        # Define response_timeout based on game type
        if game_type == 'rps':
            self.response_timeout = 3  # seconds
        elif game_type == 'counting':
            self.response_timeout = 5  # seconds

        # Assign player_id based on mode
        if self.is_networked:
            self.player_id = self.network_client.player_id
        elif self.mode == 'self-play':
            self.player_id = 'System'
        else:
            self.player_id = 'LocalPlayer'

        # Game loop task
        self.game_loop_task = None
        self.round_event = asyncio.Event()

    async def start_game(self, total_rounds=5):
        """
        Start the game for a specified number of rounds.

        :param total_rounds: Number of rounds to play
        """
        if self.game_loop_task is None:
            self.total_rounds = total_rounds
            self.current_round = 0
            self.score = 0
            self.game_loop_task = asyncio.create_task(self.game_loop())
            print(f"GameManager: Game '{self.game_type}' started for {self.total_rounds} rounds.")
            # Optionally notify via network_client
            if self.is_networked:
                await self.network_client.send_admin_message(f"Game '{self.game_type}' started for {self.total_rounds} rounds.", type='info')

    async def stop_game(self):
        """
        Stop the game loop.
        """
        if self.game_loop_task:
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                pass
            self.game_loop_task = None
            self.game_state = 'waiting'
            print(f"GameManager: Game '{self.game_type}' has been stopped.")
            if self.is_networked:
                await self.network_client.send_admin_message(f"Game '{self.game_type}' has been stopped.", type='info')

    async def reset_game(self):
        """
        Reset the game state.
        """
        await self.stop_game()
        self.prompt = None
        self.round_score = 0
        self.result_text = 'N/A'  # Reset result_text
        self.current_round = 0
        self.score = 0
        self.game_state = 'waiting'
        print(f"GameManager: Game '{self.game_type}' has been reset.")
        if self.is_networked:
            await self.network_client.send_admin_message(f"Game '{self.game_type}' has been reset.", type='info')

    async def game_loop(self):
        """
        Main game loop managing the rounds.
        """
        try:
            while self.current_round < self.total_rounds:
                self.current_round += 1
                print(f"GameManager: --- Round {self.current_round} of {self.total_rounds} ---")

                # Get prompt based on mode
                if self.mode == 'networked':
                    await self.get_prompt_networked()
                elif self.mode == 'local':
                    await self.get_prompt_local()
                elif self.mode == 'self-play':
                    await self.get_prompt_self_play()

                # Notify game state
                self.game_state = 'prompted'

                # Wait for response or timeout
                try:
                    await asyncio.wait_for(self.round_event.wait(), timeout=self.response_timeout)
                except asyncio.TimeoutError:
                    # Handle timeout
                    self.game_state = 'responded'
                    print("GameManager: No response received within the timeout.")
                    # Calculate round score as 0
                    self.round_score = 0
                    self.result_text = 'No response received.'
                    # Notify result
                    if self.is_networked:
                        await self.network_client.send_round_result({
                            'player_id': self.player_id,
                            'result_text': self.result_text,
                            'round_score': self.round_score
                        })
                finally:
                    self.round_event.clear()

            # Game ended
            print(f"GameManager: Game ended. Total score: {self.score}")
            if self.is_networked:
                await self.network_client.send_admin_message(f"Game ended. Total score: {self.score}", type='info')
        except asyncio.CancelledError:
            print("GameManager: Game loop has been cancelled.")
            pass

    async def get_prompt_networked(self):
        """
        Request a new prompt from the server.
        """
        if self.network_client:
            prompt_data = await self.network_client.get_prompt()
            self.prompt = prompt_data.get('prompt')
            print(f"GameManager: Received prompt from server: {self.prompt}")
            self.game_state = 'prompted'  # Ensure game_state is set
        else:
            print("GameManager: No network client available for networked mode.")

    async def get_prompt_local(self):
        """
        Generate a new prompt locally.
        """
        if self.game_type == 'rps':
            self.prompt = random.choice(['Rock', 'Paper', 'Scissors'])
        elif self.game_type == 'counting':
            self.prompt = random.randint(1, 5)
        print(f"GameManager: Generated local prompt: {self.prompt}")

    async def get_prompt_self_play(self):
        """
        Generate a new prompt and automatically respond as both player and system.
        """
        if self.game_type == 'rps':
            self.prompt = random.choice(['Rock', 'Paper', 'Scissors'])
            system_gesture = random.choice(['Rock', 'Paper', 'Scissors'])
            print(f"GameManager: System Gesture: {system_gesture}")
            # Simulate system response
            await asyncio.sleep(1)  # Simulate response delay
            result = self.handle_local_rps_scoring(user_gesture=system_gesture, response_time=1, confidence_score=1.0)
            self.round_score = result['round_score']
            self.score += self.round_score
            self.result_text = result['result_text']
            print(f"GameManager: Round {self.current_round} Result: {self.result_text} | Round Score: {self.round_score:.1f}")
            if self.is_networked:
                await self.network_client.send_round_result({
                    'player_id': self.player_id,
                    'result_text': self.result_text,
                    'round_score': self.round_score
                })
        elif self.game_type == 'counting':
            self.prompt = random.randint(1, 5)
            target_number = self.prompt
            print(f"GameManager: Target Number: {target_number}")
            # Simulate system response
            system_response = str(target_number)  # Assume correct response
            response_time = 1  # seconds
            confidence_score = 1.0
            result = self.handle_local_counting_scoring(user_gesture=system_response, response_time=response_time, confidence_score=confidence_score)
            self.round_score = result['round_score']
            self.score += self.round_score
            self.result_text = result['result_text']
            print(f"GameManager: Round {self.current_round} Result: {self.result_text} | Round Score: {self.round_score:.1f}")
            if self.is_networked:
                await self.network_client.send_round_result({
                    'player_id': self.player_id,
                    'result_text': self.result_text,
                    'round_score': self.round_score
                })

    async def receive_response(self, player_id, user_gesture, response_time, confidence_score):
        """
        Receive response from player.

        :param player_id: ID of the player
        :param user_gesture: Gesture submitted by the player
        :param response_time: Time taken to respond
        :param confidence_score: Confidence in the gesture
        """
        if self.game_state != 'prompted':
            print("GameManager: No active prompt to receive responses.")
            return

        if self.game_type == 'rps':
            result = self.handle_local_rps_scoring(user_gesture, response_time, confidence_score)
        elif self.game_type == 'counting':
            result = self.handle_local_counting_scoring(user_gesture, response_time, confidence_score)
        else:
            result = {'result_text': 'Unknown game type.', 'round_score': 0}

        self.round_score = result['round_score']
        self.score += self.round_score
        self.result_text = result['result_text']
        self.game_state = 'responded'

        print(f"GameManager: Player {player_id}: {self.result_text} | Round Score: {self.round_score:.1f}")

        if self.is_networked:
            await self.network_client.send_round_result({
                'player_id': player_id,
                'result_text': self.result_text,
                'round_score': self.round_score
            })

        # Set event to proceed to next round
        self.round_event.set()

    def handle_local_rps_scoring(self, user_gesture, response_time, confidence_score):
        """
        Handle scoring for Rock-Paper-Scissors locally.

        :param user_gesture: Gesture submitted by the user
        :param response_time: Time taken to respond
        :param confidence_score: Confidence in the gesture
        :return: Result dictionary
        """
        system_gesture = self.prompt
        outcome = self.determine_winner(user_gesture, system_gesture)

        # Calculate score
        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.response_timeout - response_time) / self.response_timeout)
        round_score = (confidence_score * confidence_weight + time_score * time_weight) * 100

        return {
            'result_text': f'{outcome}',
            'round_score': round_score
        }

    def handle_local_counting_scoring(self, user_gesture, response_time, confidence_score):
        """
        Handle scoring for Counting game locally.

        :param user_gesture: Gesture submitted by the user
        :param response_time: Time taken to respond
        :param confidence_score: Confidence in the gesture
        :return: Result dictionary
        """
        try:
            user_number = int(user_gesture)
        except ValueError:
            return {
                'result_text': 'Invalid input.',
                'round_score': 0
            }

        target_number = self.prompt
        if user_number == target_number:
            correctness = 'Correct!'
            base_score = 100
        else:
            correctness = f'Incorrect! Target was {target_number}'
            base_score = 0

        # Calculate score
        time_weight = 0.3
        confidence_weight = 0.7
        time_score = max(0, (self.response_timeout - response_time) / self.response_timeout)
        round_score = (confidence_score * confidence_weight + time_score * time_weight) * base_score / 100

        return {
            'result_text': f'{correctness}',
            'round_score': round_score
        }

    def determine_winner(self, player_gesture, system_gesture):
        if player_gesture == system_gesture:
            return 'Tie'
        elif (player_gesture == 'Rock' and system_gesture == 'Scissors') or \
             (player_gesture == 'Paper' and system_gesture == 'Rock') or \
             (player_gesture == 'Scissors' and system_gesture == 'Paper'):
            return 'You Win!'
        else:
            return 'You Lose!'
