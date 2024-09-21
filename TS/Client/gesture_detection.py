# gesture_detection.py

import cv2
import mediapipe as mp
from collections import deque, Counter

class GestureDetector:
    def __init__(self, max_buffer_len=5, mode='rps'):
        """
        Initialize the GestureDetector.

        :param max_buffer_len: Maximum length of the gesture buffer for smoothing
        :param mode: 'rps' for Rock-Paper-Scissors, 'count' for finger counting
        """
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        self.gesture_buffer = deque(maxlen=max_buffer_len)
        self.current_gesture = 'None'
        self.gesture_confidence = 0
        self.mode = mode  # 'rps' for Rock-Paper-Scissors, 'count' for finger counting

    def classify_gesture_rps(self, hand_landmarks):
        """
        Classify the hand gesture for Rock-Paper-Scissors based on landmarks.

        :param hand_landmarks: Detected hand landmarks
        :return: 'Rock', 'Paper', 'Scissors', or 'Unknown'
        """
        finger_tips_ids = [self.mp_hands.HandLandmark.THUMB_TIP,
                           self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
                           self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                           self.mp_hands.HandLandmark.RING_FINGER_TIP,
                           self.mp_hands.HandLandmark.PINKY_TIP]

        finger_mcp_ids = [self.mp_hands.HandLandmark.THUMB_IP,
                          self.mp_hands.HandLandmark.INDEX_FINGER_MCP,
                          self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                          self.mp_hands.HandLandmark.RING_FINGER_MCP,
                          self.mp_hands.HandLandmark.PINKY_MCP]

        landmarks = hand_landmarks.landmark
        fingers_open = []

        for tip_id, mcp_id in zip(finger_tips_ids, finger_mcp_ids):
            if landmarks[tip_id].y < landmarks[mcp_id].y:
                fingers_open.append(1)  # Finger is open
            else:
                fingers_open.append(0)  # Finger is closed

        # Classify gestures based on finger states
        if fingers_open == [0, 0, 0, 0, 0]:
            return 'Rock'
        elif fingers_open == [1, 1, 1, 1, 1]:
            return 'Paper'
        elif fingers_open == [0, 1, 1, 0, 0]:
            return 'Scissors'
        else:
            return 'Unknown'

    def count_fingers(self, hand_landmarks):
        """
        Count the number of fingers up for the Counting game.

        :param hand_landmarks: Detected hand landmarks
        :return: String representation of the number of fingers up
        """
        finger_tips_ids = [self.mp_hands.HandLandmark.THUMB_TIP,
                           self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
                           self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                           self.mp_hands.HandLandmark.RING_FINGER_TIP,
                           self.mp_hands.HandLandmark.PINKY_TIP]

        finger_pip_ids = [self.mp_hands.HandLandmark.THUMB_IP,
                          self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
                          self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                          self.mp_hands.HandLandmark.RING_FINGER_PIP,
                          self.mp_hands.HandLandmark.PINKY_PIP]

        landmarks = hand_landmarks.landmark
        fingers_up = []

        # For the thumb (assuming right hand)
        if landmarks[finger_tips_ids[0]].x > landmarks[finger_pip_ids[0]].x:
            fingers_up.append(1)  # Thumb is up
        else:
            fingers_up.append(0)  # Thumb is down

        # For other fingers
        for tip_id, pip_id in zip(finger_tips_ids[1:], finger_pip_ids[1:]):
            if landmarks[tip_id].y < landmarks[pip_id].y:
                fingers_up.append(1)  # Finger is up
            else:
                fingers_up.append(0)  # Finger is down

        total_fingers = sum(fingers_up)
        return str(total_fingers)

    def process_frame(self, image):
        """
        Process the incoming frame for gesture detection.

        :param image: BGR image from the webcam
        :return: Annotated image with hand landmarks and gesture classification
        """
        # Convert and preprocess the image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.GaussianBlur(image_rgb, (5, 5), 0)

        # Process the image for hands
        results_hands = self.hands.process(image_rgb)

        # Initialize variables
        self.current_gesture = 'None'
        self.gesture_confidence = 0

        # Draw hand landmarks and classify gesture
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2))

                # Recognize gesture based on mode
                if self.mode == 'rps':
                    gesture = self.classify_gesture_rps(hand_landmarks)
                elif self.mode == 'count':
                    gesture = self.count_fingers(hand_landmarks)
                else:
                    gesture = 'Unknown'

                self.gesture_buffer.append(gesture)

                # Determine the most common gesture in the buffer
                gesture_counts = Counter(self.gesture_buffer)
                most_common_gesture, count = gesture_counts.most_common(1)[0]
                self.gesture_confidence = count / self.gesture_buffer.maxlen  # Confidence as a fraction

                self.current_gesture = most_common_gesture
        else:
            self.gesture_buffer.append('None')

        return image  # Return the image with annotations

    def get_gesture(self):
        """
        Retrieve the current gesture and its confidence.

        :return: Tuple of (gesture, confidence)
        """
        return self.current_gesture, self.gesture_confidence

    def release(self):
        """
        Release MediaPipe resources.
        """
        self.hands.close()
