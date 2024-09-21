# network_client.py

import socketio
import time

class NetworkClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.connected = False
        self.sio = socketio.Client()
        self.prompt = None
        self.result = None

        # Define event handlers
        @self.sio.event
        def connect():
            print("Connected to server")
            self.connected = True
            # Send a join message
            self.sio.emit('join', {'player_id': 'player1'})

        @self.sio.event
        def disconnect():
            print("Disconnected from server")
            self.connected = False

        @self.sio.on('prompt')
        def on_prompt(data):
            print("Received prompt:", data)
            self.prompt = data['prompt']

        @self.sio.on('result')
        def on_result(data):
            print("Received result:", data)
            self.result = data

    def connect(self):
        try:
            self.sio.connect(self.server_url)
            self.sio.wait(seconds=1)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
        return self.connected

    def get_prompt(self):
        # Wait for a prompt to be received
        while self.prompt is None:
            self.sio.wait(seconds=0.1)
        prompt = self.prompt
        self.prompt = None  # Reset for next prompt
        return prompt

    def submit_response(self, user_gesture, response_time, confidence_score):
        self.sio.emit('response', {
            'player_id': 'player1',
            'gesture': user_gesture,
            'response_time': response_time * 1000,  # Convert to milliseconds
            'confidence_score': confidence_score
        })
        # Wait for result
        while self.result is None:
            self.sio.wait(seconds=0.1)
        result = self.result
        self.result = None  # Reset for next result
        # Process result
        for res in result['results']:
            if res['player_id'] == 'player1':
                return {
                    'result_text': res['result_text'],
                    'round_score': res['round_score']
                }
        return None

    def disconnect(self):
        self.sio.disconnect()
