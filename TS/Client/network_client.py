# network_client.py

import socketio
import asyncio
import uuid
import random
import logging

# Configure logging to display debug messages
logging.basicConfig(level=logging.DEBUG)

class NetworkClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.sio = socketio.AsyncClient(logger=True, engineio_logger=True)
        self.player_id = str(uuid.uuid4())
        self.connected = False

        # Bind event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error', self.on_error)
        self.sio.on('prompt', self.on_prompt)
        self.sio.on('result', self.on_result)
        self.sio.on('game_end', self.on_game_end)

    async def connect(self):
        try:
            await self.sio.connect(self.server_url)
            self.connected = True
            print("NetworkClient: Connected to the server.")
            await self.sio.wait()
        except socketio.exceptions.ConnectionError as e:
            print(f"NetworkClient: Connection failed: {e}")

    async def disconnect(self):
        if self.connected:
            await self.sio.disconnect()
            self.connected = False
            print("NetworkClient: Disconnected from the server.")

    async def on_connect(self):
        print("NetworkClient: Successfully connected to the server.")
        # Emit 'join' event with player_id
        await self.sio.emit('join', {'player_id': self.player_id})
        print(f"NetworkClient: Emitted 'join' event with Player ID: {self.player_id}")

    async def on_disconnect(self):
        print("NetworkClient: Disconnected from the server.")
        self.connected = False

    async def on_error(self, data):
        print(f"NetworkClient: Error from server: {data.get('message')}")

    async def on_prompt(self, data):
        """
        Handle incoming 'prompt' event from the server.
        """
        try:
            prompt = data.get('prompt')
            response_timeout = data.get('responseTimeout')
            current_round = data.get('currentRound')
            total_rounds = data.get('totalRounds')

            print(f"\nNetworkClient: --- Round {current_round} of {total_rounds} ---")
            print(f"NetworkClient: Received Prompt: {prompt}")
            print(f"NetworkClient: Response Timeout: {response_timeout} ms")

            # Simulate response after a short delay
            await asyncio.sleep(1)  # Simulate response time (1 second)
            gesture, confidence = self.get_simulated_gesture(prompt)
            response_time = 1000  # milliseconds (1 second)
            await self.submit_response(gesture, response_time, confidence)
            print(f"NetworkClient: Emitted 'response' event with gesture: {gesture}")
        except Exception as e:
            print(f"NetworkClient: Error in on_prompt: {e}")

    async def on_result(self, data):
        """
        Handle incoming 'result' event from the server.
        """
        try:
            results = data.get('results', [])
            print("\nNetworkClient: --- Round Results ---")
            for result in results:
                player_id = result.get('player_id')
                result_text = result.get('result_text')
                round_score = result.get('round_score')
                print(f"NetworkClient: Player {player_id}: {result_text} | Round Score: {round_score}")
        except Exception as e:
            print(f"NetworkClient: Error in on_result: {e}")

    async def on_game_end(self, data):
        """
        Handle incoming 'game_end' event from the server.
        """
        try:
            player_scores = data.get('playerScores', {})
            print("\nNetworkClient: --- Game Ended ---")
            for player_id, scores in player_scores.items():
                print(f"Player {player_id}: {scores}")
            await self.disconnect()
        except Exception as e:
            print(f"NetworkClient: Error in on_game_end: {e}")

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
            print(f"NetworkClient: Submitted response: Gesture={gesture}, Time={response_time}ms, Confidence={confidence_score}")
        except Exception as e:
            print(f"NetworkClient: Error in submit_response: {e}")

    def get_simulated_gesture(self, prompt):
        """
        Simulate a gesture based on the prompt.
        """
        if isinstance(prompt, str):
            # Assume 'rps' mode
            gesture = random.choice(['Rock', 'Paper', 'Scissors'])
            confidence = 0.9
        elif isinstance(prompt, int):
            # Assume 'counting' mode
            gesture = str(random.randint(1, prompt))
            confidence = 0.9
        else:
            gesture = 'Rock'
            confidence = 0.5
        return gesture, confidence

if __name__ == "__main__":
    server_url = 'http://localhost:5000'  # Update if different
    client = NetworkClient(server_url)
    asyncio.run(client.connect())
