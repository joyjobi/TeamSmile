# game_manager.py

import asyncio
import random
import logging

from rock_paper_scissors import RockPaperScissorsGame
from counting_game import CountingGame

logger = logging.getLogger(__name__)

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
        self.is_networked = self.mode == 'networked'  # Depend solely on mode
        self.prompt = None
        self.round_score = 0
        self.result_text = 'N/A'
        self.current_round = 0
        self.total_rounds = 5  # Default number of rounds
        self.score = 0
        self.game_state = 'waiting'  # 'waiting', 'prompted', 'responded'

        # Define response_timeout based on game type
        if game_type == 'rps':
            self.response_timeout = 3  # seconds
        elif game_type == 'counting':
            self.response_timeout = 5  # seconds

        # Initialize player_id
        self.player_id = 'LocalPlayer'  # Default for non-networked mode

        # Game loop task
        self.game_loop_task = None
        self.round_event = asyncio.Event()
        self.prompt_queue = asyncio.Queue()

        # Initialize specific game logic
        if self.game_type == 'rps':
            self.game_logic = RockPaperScissorsGame(self)
        elif self.game_type == 'counting':
            self.game_logic = CountingGame(self)
        else:
            logger.error(f"GameManager: Unsupported game type '{self.game_type}'.")
            self.game_logic = None

        # UI Queue for communication
        self.ui_queue = None  # To be set via set_ui_queue

    def set_ui_queue(self, ui_queue):
        """
        Set the UI queue for sending messages to the UI.

        :param ui_queue: Queue object for UI communication
        """
        self.ui_queue = ui_queue

    def send_ui_message(self, msg_type, msg_text):
        """
        Send a message to the UI via the ui_queue.

        :param msg_type: Type of the message (e.g., 'result', 'score')
        :param msg_text: The message content
        """
        if self.ui_queue:
            self.ui_queue.put((msg_type, msg_text))

    def set_player_id(self, player_id):
        """
        Set the player ID after network_client is connected.

        :param player_id: The unique player ID from the server
        """
        self.player_id = player_id
        logger.info(f"GameManager: Player ID set to {self.player_id}")

    async def start_game(self, total_rounds=5):
        """
        Start the game for a specified number of rounds.

        :param total_rounds: Number of rounds to play
        """
        self.total_rounds = total_rounds
        self.current_round = 0
        self.score = 0
        self.game_loop_task = asyncio.create_task(self.game_loop())
        logger.info(f"GameManager: Game '{self.game_type}' started for {self.total_rounds} rounds.")
        self.send_ui_message("prompt", f"Game '{self.game_type}' started for {self.total_rounds} rounds.")
        # Optionally notify via network_client
        if self.is_networked and self.network_client:
            await self.network_client.sio.emit('admin_message', {
                'message': f"Game '{self.game_type}' started for {self.total_rounds} rounds."
            })

    async def stop_game(self):
        """
        Stop the game loop.
        """
        if self.game_loop_task:
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                logger.info("GameManager: Game loop task cancelled successfully.")
            self.game_loop_task = None
            self.game_state = 'waiting'
            logger.info(f"GameManager: Game '{self.game_type}' has been stopped.")
            if self.is_networked and self.network_client:
                await self.network_client.sio.emit('admin_message', {
                    'message': f"Game '{self.game_type}' has been stopped."
                })

    async def game_loop(self):
        """
        Main game loop managing the rounds.
        """
        try:
            while self.current_round < self.total_rounds:
                self.current_round += 1
                logger.info(f"GameManager: --- Round {self.current_round} of {self.total_rounds} ---")

                if self.is_networked:
                    # Wait for a prompt from the server
                    try:
                        event_type, data = await asyncio.wait_for(self.prompt_queue.get(), timeout=self.response_timeout)
                        if event_type == 'prompt':
                            self.prompt = data.get('prompt')
                            self.game_state = 'prompted'
                            await self.handle_prompt()
                    except asyncio.TimeoutError:
                        logger.warning("GameManager: No prompt received within the timeout.")
                        continue
                else:
                    # Generate local prompt
                    await self.get_prompt_local()

                # Wait for response or timeout
                try:
                    await asyncio.wait_for(self.round_event.wait(), timeout=self.response_timeout)
                except asyncio.TimeoutError:
                    logger.warning("GameManager: No response received within the timeout.")
                    self.round_score = 0
                    self.result_text = 'No response received.'
                    self.send_ui_message("result", self.result_text)
                    self.send_ui_message("score", f"Score: {self.score:.1f}")
                    self.game_state = 'waiting'  # Reset state after timeout

                self.round_event.clear()

            logger.info(f"GameManager: Game ended. Total score: {self.score}")
            self.send_ui_message("result", f"Game ended. Total score: {self.score}")
            if self.is_networked and self.network_client:
                await self.network_client.sio.emit('admin_message', {
                    'message': f"Game ended. Total score: {self.score}"
                })
        except asyncio.CancelledError:
            logger.info("GameManager: Game loop has been cancelled.")
            pass

    async def handle_prompt(self):
        """Handle prompt received from the server or generated locally."""
        logger.info(f"GameManager: Handling prompt '{self.prompt}'.")
        # Additional prompt handling logic here
        # For example, update UI or notify players

    async def get_prompt_local(self):
        """Generate a new prompt locally."""
        if self.game_type == 'rps':
            self.prompt = random.choice(['Rock', 'Paper', 'Scissors'])
        elif self.game_type == 'counting':
            self.prompt = random.randint(1, 5)
        logger.info(f"GameManager: Generated local prompt: {self.prompt}")
        self.game_state = 'prompted'
        self.send_ui_message("prompt", f"Round {self.current_round}: {self.prompt}")

    async def receive_prompt(self, prompt_data):
        """
        Receive a prompt from the server and enqueue it for processing.

        :param prompt_data: Data containing the prompt
        """
        if self.is_networked:
            await self.prompt_queue.put(('prompt', prompt_data))
            logger.debug(f"GameManager: Prompt received and enqueued: {prompt_data}")
        else:
            logger.warning("GameManager: Received prompt in non-networked mode.")

    async def receive_response(self, player_id, user_gesture, response_time, confidence_score):
        """
        Receive response from player.

        :param player_id: ID of the player
        :param user_gesture: Gesture submitted by the player
        :param response_time: Time taken to respond (in seconds)
        :param confidence_score: Confidence in the gesture
        :return: True if response was accepted, False otherwise
        """
        if self.game_state != 'prompted':
            logger.warning("GameManager: No active prompt to receive responses.")
            return False  # Response not accepted

        # Handle response based on game logic
        if self.game_logic:
            result = self.game_logic.handle_scoring(user_gesture, response_time, confidence_score)
        else:
            result = {'result_text': 'Game logic not initialized.', 'round_score': 0}

        self.round_score = result['round_score']
        self.score += self.round_score
        self.result_text = result['result_text']
        self.game_state = 'responded'  # Prevent further responses for this prompt
        logger.info(f"GameManager: Player {player_id}: {self.result_text} | Round Score: {self.round_score:.1f}")

        # Update UI
        self.send_ui_message("result", self.result_text)
        self.send_ui_message("score", f"Score: {self.score:.1f}")

        # Set event to proceed to next round
        self.round_event.set()

        return True  # Response accepted

    async def reset(self):
        """
        Reset the game state.
        """
        self.current_round = 0
        self.score = 0
        self.game_state = 'waiting'
        self.prompt = None
        self.round_score = 0
        self.result_text = 'N/A'
        logger.info("GameManager: Game has been reset.")
        self.send_ui_message("result", "Game has been reset.")
        self.send_ui_message("score", "Score: 0")

    async def change_game_type(self, new_game_type):
        """
        Change the current game type.

        :param new_game_type: 'rps' or 'counting'
        """
        if new_game_type not in ['rps', 'counting']:
            logger.error(f"GameManager: Unsupported game type '{new_game_type}'.")
            self.send_ui_message("Error", f"Unsupported game type '{new_game_type}'.")
            return

        self.game_type = new_game_type
        self.game_state = 'waiting'
        self.prompt = None
        self.round_score = 0
        self.result_text = 'N/A'
        self.current_round = 0
        self.score = 0

        # Re-initialize game logic
        if self.game_type == 'rps':
            self.game_logic = RockPaperScissorsGame(self)
        elif self.game_type == 'counting':
            self.game_logic = CountingGame(self)

        logger.info(f"GameManager: Game type changed to '{self.game_type}'.")
        self.send_ui_message("prompt", f"Game type changed to '{self.game_type}'.")
