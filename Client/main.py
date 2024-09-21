# main.py

import cv2
import sys
import time  # Import time for the visual indicator
from gesture_detection import GestureDetector
from game_logic import RockPaperScissorsGame, HandGestureCountingGame
from game_manager import GameManager
from network_client import NetworkClient

def main():

    # Initialize NetworkClient
    server_url = 'http://localhost:3000'  # Update with your server URL
    network_client = NetworkClient(server_url=server_url)
    network_client.connect()

    # Check for game selection
    if len(sys.argv) > 1 and sys.argv[1] == 'counting':
        gesture_mode = 'count'
        window_title = 'Hand Gesture Counting Game'
        game_type = 'counting'
    else:
        gesture_mode = 'rps'
        window_title = 'Rock-Paper-Scissors Game'
        game_type = 'rps'

    # Initialize GameManager
    game_manager = GameManager(game_type=game_type, network_client=network_client if network_client.connected else None)

    # Initialize Game
    if game_type == 'rps':
        game = RockPaperScissorsGame(game_manager)
    else:
        game = HandGestureCountingGame(game_manager)
        
    # Initialize Gesture Detector with the correct mode
    gesture_detector = GestureDetector(mode=gesture_mode)

    # Start the webcam feed
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip and resize the image
        image = cv2.flip(image, 1)
        image = cv2.resize(image, (640, 480))

        # Process frame for gesture detection
        image = gesture_detector.process_frame(image)
        user_gesture, gesture_confidence = gesture_detector.get_gesture()

        # Update game state based on user input
        game.update(user_gesture, gesture_confidence)

        # Get text overlays from the game
        display_texts = game.get_display_text(user_gesture)

        # Overlay Information on Image
        for text, position, color, font_scale, font_thickness in display_texts:
            cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness, cv2.LINE_AA)

        # Visual Indicator for New Game (if not already in get_display_text)
        if game.game_state == 'prompted':
            elapsed_time = time.time() - game.game_start_time
            radius = int(20 + (elapsed_time % 1) * 10)  # Animate radius
            cv2.circle(image, (int(game.screen_width / 2), 50), radius, (0, 0, 255), 2)

        # Display the output
        cv2.imshow(window_title, image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    gesture_detector.release()

    # Ensure to disconnect when done
    network_client.disconnect()

if __name__ == "__main__":
    main()
