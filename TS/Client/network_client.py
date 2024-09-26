# network_client.py

import socketio
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)

class NetworkClient:
    def __init__(self, server_url, game_manager):
        """
        Initialize the NetworkClient.

        :param server_url: URL of the game server
        :param game_manager: Instance of GameManager to communicate with
        """
        self.server_url = server_url
        self.game_manager = game_manager
        self.sio = socketio.AsyncClient(logger=True, engineio_logger=True)
        self.player_id = str(uuid.uuid4())
        self.connected = False

        # Bind event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error', self.on_error)
        self.sio.on('prompt', self.on_prompt)
        self.sio.on('result', self.on_result)
        self.sio.on('player_scores', self.on_player_scores)
        self.sio.on('reset', self.on_reset)
        self.sio.on('game_type_changed', self.on_game_type_changed)

    async def connect(self):
        try:
            await self.sio.connect(self.server_url)
            self.connected = True
            logger.info("NetworkClient: Connected to the server.")
            await self.sio.wait()
        except socketio.exceptions.ConnectionError as e:
            logger.error(f"NetworkClient: Connection failed: {e}")
            self.game_manager.send_ui_message("Failed", "Connection to server failed.")

    async def disconnect(self):
        if self.connected:
            await self.sio.disconnect()
            self.connected = False
            logger.info("NetworkClient: Disconnected from the server.")
            self.game_manager.send_ui_message("Disconnected", "Disconnected from server.")

    async def on_connect(self):
        logger.info("NetworkClient: Successfully connected to the server.")
        # Emit 'join' event with player_id
        await self.sio.emit('join', {'player_id': self.player_id})
        logger.info(f"NetworkClient: Emitted 'join' event with Player ID: {self.player_id}")
        
        # Set player_id in GameManager
        self.game_manager.set_player_id(self.player_id)
        
        self.game_manager.send_ui_message("Connected", "Connected to server.")

    async def on_disconnect(self):
        logger.info("NetworkClient: Disconnected from the server.")
        self.connected = False
        self.game_manager.send_ui_message("Disconnected", "Disconnected from server.")

    async def on_error(self, data):
        logger.error(f"NetworkClient: Error from server: {data.get('message')}")
        self.game_manager.send_ui_message("Error", data.get('message', 'Unknown error.'))

    async def on_prompt(self, data):
        """
        Handle incoming 'prompt' event from the server.
        """
        logger.info(f"NetworkClient: Received prompt: {data}")
        await self.game_manager.receive_prompt(data)
        prompt_text = data.get('prompt', 'No Prompt')
        self.game_manager.send_ui_message("prompt", prompt_text)

    async def on_result(self, data):
        """
        Handle incoming 'result' event from the server.
        """
        logger.info(f"NetworkClient: Received result: {data}")
        # Process and update UI if needed
        result_text = data.get('result_text', 'Result received.')
        self.game_manager.send_ui_message("result", result_text)

    async def on_player_scores(self, data):
        """
        Handle incoming 'player_scores' event from the server.
        """
        logger.info(f"NetworkClient: Received player scores: {data}")
        # Process and update UI if needed
        scores_text = "Scores updated."
        self.game_manager.send_ui_message("score", scores_text)

    async def on_reset(self, data):
        """
        Handle incoming 'reset' event from the server.
        """
        logger.info("NetworkClient: Received reset event from the server.")
        await self.game_manager.reset()
        self.game_manager.send_ui_message("result", "Game has been reset.")

    async def on_game_type_changed(self, data):
        """
        Handle incoming 'game_type_changed' event from the server.
        """
        new_game_type = data.get('gameType')
        logger.info(f"NetworkClient: Game type changed to '{new_game_type}'.")
        await self.game_manager.change_game_type(new_game_type)
        self.game_manager.send_ui_message("prompt", f"Game type changed to '{new_game_type}'.")

    async def submit_response(self, gesture, response_time, confidence_score):
        """
        Submit the player's response to the server.
        """
        try:
            await self.sio.emit('response', {
                'player_id': self.player_id,
                'gesture': gesture,
                'response_time': response_time,
                'confidence_score': confidence_score
            })
            logger.info(f"NetworkClient: Submitted response: Gesture={gesture}, Time={response_time}s, Confidence={confidence_score}")
        except Exception as e:
            logger.error(f"NetworkClient: Error in submit_response: {e}")
            self.game_manager.send_ui_message("Error", "Failed to submit response.")
