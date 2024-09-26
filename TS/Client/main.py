# main.py

import cv2
import sys
import asyncio
import signal
import threading
from queue import Queue, Empty
from tkinter import Tk, Label, Button, StringVar
from gesture_detection import GestureDetector
from game_manager import GameManager
from network_client import NetworkClient
import argparse
import logging
import time
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO to reduce verbosity; use DEBUG for more detailed logs
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

class App:
    def __init__(self, args):
        self.args = args
        self.exit_event = threading.Event()
        self.ui_queue = Queue()
        self.gesture_queue = Queue()  # Queue for gesture inputs

        # Initialize GameManager and GestureDetector
        self.game_manager = GameManager(game_type=args.game_type, mode=args.mode)
        self.gesture_detector = GestureDetector(mode=args.game_type)

        # Set the UI queue in GameManager
        self.game_manager.set_ui_queue(self.ui_queue)

        # Initialize NetworkClient if in networked mode
        if self.game_manager.is_networked:
            self.network_client = NetworkClient('http://localhost:5000', self.game_manager)
            self.game_manager.network_client = self.network_client
        else:
            self.network_client = None

        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)

        # Use asyncio.new_event_loop() for networked mode to avoid DeprecationWarning
        if self.game_manager.is_networked:
            self.loop = asyncio.new_event_loop()
            self.asyncio_thread = threading.Thread(target=self.start_asyncio_loop, daemon=True)
            self.asyncio_thread.start()
        else:
            self.loop = asyncio.get_event_loop()

        # Start the webcam thread
        self.webcam_thread = threading.Thread(target=self.run_webcam, daemon=True)
        self.webcam_thread.start()

        # Gesture Buffer Configuration
        self.gesture_buffer = []
        self.buffer_duration = 0.5  # seconds
        self.buffer_lock = threading.Lock()  # To ensure thread-safe access to the buffer
        self.response_sent = False  # Flag to indicate if response has been sent for current prompt

        # Start the gesture processing thread
        self.gesture_processing_thread = threading.Thread(target=self.process_gesture_buffer, daemon=True)
        self.gesture_processing_thread.start()

        # Setup the Tkinter UI in the main thread
        self.setup_ui()

    def signal_handler(self, sig, frame):
        logger.info("App: Exiting gracefully...")
        self.exit_event.set()
        if self.network_client:
            asyncio.run_coroutine_threadsafe(self.network_client.disconnect(), self.loop)
        sys.exit(0)

    def start_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        if self.network_client:
            asyncio.run_coroutine_threadsafe(self.network_client.connect(), self.loop)
            # Start processing responses in networked mode
            asyncio.run_coroutine_threadsafe(self.process_responses(), self.loop)
        self.loop.run_forever()

    def run_webcam(self):
        logger.info("App: Starting webcam feed...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("App: Could not open webcam. Please check if it's connected and not used by another application.")
            self.exit_event.set()
            return

        logger.info("App: Webcam feed started successfully.")
        try:
            while cap.isOpened() and not self.exit_event.is_set():
                success, frame = cap.read()
                if not success:
                    logger.warning("App: Ignoring empty camera frame.")
                    continue

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (640, 480))

                # Process frame for gesture detection
                annotated_frame = self.gesture_detector.process_frame(frame)

                # Retrieve the current gesture and its confidence
                gesture, confidence = self.gesture_detector.get_gesture()

                # Log the detected gesture and confidence
                logger.debug(f"App: Detected Gesture: {gesture}, Confidence: {confidence:.1f}")

                # Determine if the gesture should be sent to the server
                if self.game_manager.game_state == 'prompted' and not self.game_manager.response_sent:
                    if gesture != 'None' and confidence >= 0.6:  # Adjust confidence threshold as needed
                        logger.info(f"App: Preparing to submit gesture '{gesture}' to the server.")
                        asyncio.run_coroutine_threadsafe(
                            self.network_client.submit_response(gesture, response_time=1, confidence_score=confidence),
                            self.network_client.loop
                        )
                        self.game_manager.response_sent = True
                        logger.info(f"App: Submitted gesture '{gesture}' to the server.")
                else:
                    # Optionally, log when a gesture is ignored due to no active prompt
                    if gesture != 'None':
                        logger.debug(f"App: Ignored gesture '{gesture}' as no active prompt.")

                # Display the annotated frame
                cv2.imshow('Game Window', annotated_frame)

                if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                    logger.info("App: Escape key pressed, exiting webcam feed.")
                    self.exit_event.set()
                    break

        except Exception as e:
            logger.error(f"App: Exception in webcam thread: {e}")

        finally:
            cap.release()
            try:
                cv2.destroyAllWindows()
            except cv2.error as e:
                logger.error(f"App: OpenCV cleanup error: {e}")
            self.gesture_detector.release()
            logger.info("App: Webcam feed ended.")

    def process_gesture_buffer(self):
        """
        Continuously process gestures from the gesture_queue,
        buffer them, and send the most frequent gesture.
        """
        while not self.exit_event.is_set():
            try:
                user_gesture, confidence_score = self.gesture_queue.get(timeout=0.1)
                with self.buffer_lock:
                    if self.game_manager.game_state == 'prompted' and not self.response_sent:
                        self.gesture_buffer.append((user_gesture, confidence_score))
                        logger.debug(f"App: Gesture added to buffer: {user_gesture} with confidence {confidence_score}")
                        # Start a timer to process the buffer after buffer_duration
                        threading.Thread(target=self.process_buffer_after_delay, daemon=True).start()
                    else:
                        logger.debug(f"App: Ignored gesture '{user_gesture}' as no active prompt.")
            except Empty:
                continue

    def process_buffer_after_delay(self):
        """
        Wait for buffer_duration seconds and then process the gesture buffer.
        """
        time.sleep(self.buffer_duration)
        with self.buffer_lock:
            if not self.gesture_buffer or self.response_sent:
                # If buffer is empty or response already sent, do nothing
                if self.gesture_buffer:
                    logger.debug("App: Clearing gesture buffer without processing.")
                self.gesture_buffer.clear()
                return
            # Extract only the gestures
            gestures = [gesture for gesture, conf in self.gesture_buffer]
            if not gestures:
                self.gesture_buffer.clear()
                logger.debug("App: No gestures detected in buffer.")
                return
            # Determine the most common gesture
            gesture_counts = Counter(gestures)
            most_common_gesture, count = gesture_counts.most_common(1)[0]
            logger.debug(f"App: Most common gesture: {most_common_gesture} with count {count}")
            # Clear the buffer
            self.gesture_buffer.clear()
            # Set response_sent to True to prevent multiple submissions
            self.response_sent = True
        # Send the most common gesture to the server
        asyncio.run_coroutine_threadsafe(
            self.handle_final_gesture(most_common_gesture),
            self.loop
        )

    async def handle_final_gesture(self, gesture):
        """
        Handle the final gesture by sending it to the GameManager and server.
        """
        logger.debug(f"App: Handling final gesture: {gesture}")
        # Assume a fixed response_time for simplicity
        response_time = 1  # seconds
        confidence_score = 1.0  # Since it's the median, assume high confidence
        response_accepted = await self.game_manager.receive_response(
            player_id=self.game_manager.player_id,
            user_gesture=gesture,
            response_time=response_time,
            confidence_score=confidence_score
        )
        if response_accepted and self.network_client:
            logger.debug(f"App: Submitting response to server: {gesture}")
            await self.network_client.submit_response(gesture, response_time, confidence_score)
        else:
            logger.debug("App: Response was not accepted or network_client is None.")

    async def process_responses(self):
        while not self.exit_event.is_set():
            try:
                user_gesture, confidence_score = self.gesture_queue.get_nowait()
                # This part is now handled by process_gesture_buffer
                # So you can remove or keep it as a backup
            except Empty:
                await asyncio.sleep(0.1)

    def setup_ui(self):
        # Setup tkinter UI
        self.root = Tk()
        self.root.title("Game Client")

        # Server connection status
        self.connection_status = StringVar(value="Disconnected" if self.game_manager.is_networked else "Local Mode")
        connection_label = Label(self.root, textvariable=self.connection_status)
        connection_label.pack()

        # Current Prompt
        self.current_prompt_var = StringVar(value="No Prompt")
        current_prompt_label = Label(self.root, textvariable=self.current_prompt_var, font=("Helvetica", 16))
        current_prompt_label.pack(pady=10)

        # Result Label
        self.result_var = StringVar(value="Result: N/A")
        result_label = Label(self.root, textvariable=self.result_var, font=("Helvetica", 14))
        result_label.pack(pady=10)

        # Score Label
        self.score_var = StringVar(value="Score: 0")
        score_label = Label(self.root, textvariable=self.score_var, font=("Helvetica", 14))
        score_label.pack(pady=10)

        # Start Game Button
        # Disable 'Start Game' if in networked mode
        self.start_button = Button(
            self.root,
            text="Start Game",
            state="disabled" if self.game_manager.is_networked else "normal",
            command=self.start_game
        )
        self.start_button.pack()

    # Function to update UI from main thread
        def process_ui_queue():
            try:
                while True:
                    msg_type, msg_text = self.ui_queue.get_nowait()
                    logger.debug(f"App: UI Message: {msg_type} - {msg_text}")  # Enabled debug logs
                    if msg_type == "result":
                        self.result_var.set(f"Result: {msg_text}")
                    elif msg_type == "score":
                        self.score_var.set(msg_text)
                    elif msg_type == "prompt":
                        self.current_prompt_var.set(f"Prompt: {msg_text}")
                        # Reset response_sent flag for new prompt
                        self.response_sent = False
                        logger.debug("App: response_sent flag reset to False for new prompt.")
                    elif msg_type == "Connected":
                        self.connection_status.set(msg_text)
                        self.start_button.config(state="disabled")  # Ensure it's disabled
                    elif msg_type == "Disconnected":
                        self.connection_status.set(msg_text)
                    elif msg_type == "Failed":
                        self.connection_status.set(msg_text)
                    elif msg_type == "Error":
                        self.result_var.set(f"Error: {msg_text}")  # Display errors in result label
            except Empty:
                pass
            self.root.after(100, process_ui_queue)


        # Start processing UI queue
        self.root.after(100, process_ui_queue)

        # Start the Tkinter main loop
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def start_game(self):
        logger.info("App: Starting the game...")
        # Disable the start button to prevent multiple clicks
        self.start_button.config(state="disabled")
        if self.network_client:
            # Do NOT emit 'admin_start_game' as this is not an admin client
            logger.warning("App: Cannot start game in networked mode as a non-admin.")
            self.game_manager.send_ui_message("Error", "Cannot start game in networked mode.")
        else:
            # In local mode, start the game locally
            asyncio.run_coroutine_threadsafe(self.game_manager.start_game(), self.loop)
            asyncio.run_coroutine_threadsafe(self.process_responses(), self.loop)

    async def reset_game(self):
        logger.info("App: Resetting the game...")
        if self.network_client:
            await self.network_client.sio.emit('reset')
        await self.game_manager.reset()
        self.start_button.config(state="normal")

    def on_close(self):
        logger.info("App: Closing application...")
        self.exit_event.set()
        if self.network_client:
            asyncio.run_coroutine_threadsafe(self.network_client.disconnect(), self.loop)
        self.root.destroy()

def main():
    parser = argparse.ArgumentParser(description="Run the game client.")
    parser.add_argument("mode", choices=["networked", "local"], help="Mode of the game")
    parser.add_argument("game_type", choices=["rps", "counting"], help="Type of the game")
    args = parser.parse_args()

    app = App(args)

if __name__ == "__main__":
    main()
