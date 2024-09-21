# main.py

import cv2
import sys
import asyncio
import random
from gesture_detection import GestureDetector
from game_logic import RockPaperScissorsGame, HandGestureCountingGame
from game_manager import GameManager
from network_client import NetworkClient

def run_webcam(game_manager, gesture_detector, game, game_type, mode):
    """
    Function to handle webcam feed and gesture detection.
    This runs in a separate thread to avoid blocking the asyncio event loop.
    """
    cap = cv2.VideoCapture(0)

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip and resize the image
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            # Process frame for gesture detection
            frame = gesture_detector.process_frame(frame)
            user_gesture, gesture_confidence = gesture_detector.get_gesture()

            # If in self-play mode, skip user gesture input
            if mode == 'self-play':
                user_gesture = None  # Or implement auto-response
                gesture_confidence = 1.0

            # Update game state based on user input
            if user_gesture:
                # Calculate actual_response_time based on gesture detection
                actual_response_time = 1000  # milliseconds (1 second)
                # Schedule the coroutine in the event loop
                asyncio.run_coroutine_threadsafe(
                    game_manager.receive_response(
                        player_id=game_manager.player_id,
                        user_gesture=user_gesture,
                        response_time=actual_response_time,
                        confidence_score=gesture_confidence
                    ), asyncio.get_event_loop())
            elif mode == 'local' and game_manager.game_state == 'prompted':
                # Simulate a response for local mode if user_gesture is None
                # For example, randomly choose a gesture
                if game_type == 'rps':
                    simulated_gesture = random.choice(['Rock', 'Paper', 'Scissors'])
                elif game_type == 'counting':
                    simulated_gesture = str(random.randint(1, 5))
                else:
                    simulated_gesture = 'N/A'
                actual_response_time = 1000  # milliseconds (1 second)
                asyncio.run_coroutine_threadsafe(
                    game_manager.receive_response(
                        player_id=game_manager.player_id,
                        user_gesture=simulated_gesture,
                        response_time=actual_response_time,
                        confidence_score=0.9
                    ), asyncio.get_event_loop())

            # Get display texts from the game
            if game_type == 'rps':
                system_gesture = game_manager.prompt if game_manager.prompt else 'N/A'
                result_text = game_manager.result_text if game_manager.result_text else 'N/A'
            elif game_type == 'counting':
                system_gesture = game_manager.prompt if game_manager.prompt else 'N/A'
                result_text = game_manager.result_text if game_manager.result_text else 'N/A'

            display_texts = game.get_display_text(
                user_gesture=user_gesture if user_gesture else 'N/A',
                system_gesture=system_gesture,
                result_text=result_text,
                response_timeout=game_manager.response_timeout,
                response_time=actual_response_time // 1000  # Convert to seconds
            )

            # Overlay Information on Image
            for text, position, color, font_scale, font_thickness in display_texts:
                if not isinstance(text, str):
                    text = str(text)  # Ensure text is a string
                cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale, color, font_thickness, cv2.LINE_AA)

            # Display the output
            cv2.imshow('Game Window', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        gesture_detector.release()

        # Ensure to disconnect when done
        asyncio.run_coroutine_threadsafe(game_manager.stop_game(), asyncio.get_event_loop())
        if game_manager.network_client:
            asyncio.run_coroutine_threadsafe(game_manager.network_client.disconnect(), asyncio.get_event_loop())

async def main():
    """
    Main asynchronous function to initialize and run the game.
    """
    # Determine game type and mode based on command-line arguments
    # Usage: python main.py [mode] [game_type]
    # Example: python main.py networked rps
    # Modes: networked, local, self-play
    # Game Types: rps, counting

    mode = 'networked'
    game_type = 'rps'

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    if len(sys.argv) > 2:
        game_type = sys.argv[2].lower()

    # Initialize NetworkClient if in networked mode
    network_client = None
    if mode == 'networked':
        server_url = 'http://localhost:5000'  # Update with your server URL
        network_client = NetworkClient(server_url=server_url)
        await network_client.connect()

    # Initialize GameManager
    game_manager = GameManager(game_type=game_type, network_client=network_client, mode=mode)

    # Initialize Game Logic
    if game_type == 'rps':
        game = RockPaperScissorsGame(game_manager)
    elif game_type == 'counting':
        game = HandGestureCountingGame(game_manager)
    else:
        print("Unsupported game type. Choose 'rps' or 'counting'.")
        return

    # Initialize Gesture Detector
    gesture_detector = GestureDetector(mode=game_type)

    # Start the game loop as a separate asynchronous task
    game_task = asyncio.create_task(game_manager.start_game(total_rounds=5))

    # Start the webcam feed in a separate thread
    await asyncio.to_thread(run_webcam, game_manager, gesture_detector, game, game_type, mode)

    # Wait for the game task to complete
    await game_task

if __name__ == "__main__":
    asyncio.run(main())
