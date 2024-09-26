# gesture_detection.py

import cv2
import mediapipe as mp
from collections import deque, Counter
import logging

import time


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO or higher
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GestureDetector:



    def __init__(self, max_buffer_len=5, mode='rps'):
        self.last_gesture_time = 0
        self.debounce_time = 1  # seconds
        logger.info(f"GestureDetector: Initializing with mode '{mode}' and buffer length {max_buffer_len}.")
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
        self.mode = mode  # 'rps' or 'count'

    def classify_gesture_rps(self, hand_landmarks):
        """
        Classify the hand gesture for Rock-Paper-Scissors based on landmarks.

        :param hand_landmarks: Detected hand landmarks
        :return: 'Rock', 'Paper', 'Scissors', or 'Unknown'
        """
        logger.debug("GestureDetector: Classifying gesture for RPS.")
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
        logger.debug("GestureDetector: Counting fingers.")
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
        logger.debug(f"GestureDetector: Counted {total_fingers} fingers up.")
        return str(total_fingers)





    def process_frame(self, image):
        # Existing preprocessing
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.GaussianBlur(image_rgb, (5, 5), 0)
        results_hands = self.hands.process(image_rgb)
        self.current_gesture = 'None'
        self.gesture_confidence = 0

        current_time = time.time()

        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                # Existing drawing and classification
                if self.mode == 'rps':
                    gesture = self.classify_gesture_rps(hand_landmarks)
                elif self.mode == 'count':
                    gesture = self.count_fingers(hand_landmarks)
                else:
                    gesture = 'Unknown'

                self.gesture_buffer.append(gesture)

                gesture_counts = Counter(self.gesture_buffer)
                most_common_gesture, count = gesture_counts.most_common(1)[0]
                self.gesture_confidence = count / self.gesture_buffer.maxlen

                if (most_common_gesture != self.current_gesture and 
                    (current_time - self.last_gesture_time) > self.debounce_time):
                    logger.info(f"GestureDetector: Gesture changed to '{most_common_gesture}' with confidence {self.gesture_confidence:.2f}.")
                    self.current_gesture = most_common_gesture
                    self.last_gesture_time = current_time
        else:
            self.gesture_buffer.append('None')
            if self.current_gesture != 'None' and (current_time - self.last_gesture_time) > self.debounce_time:
                logger.info("GestureDetector: No hand detected.")
                self.current_gesture = 'None'
                self.gesture_confidence = 0
                self.last_gesture_time = current_time

        return image


    def get_gesture(self):
        """
        Retrieve the current gesture and its confidence.

        :return: Tuple of (gesture, confidence)
        """
        logger.debug(f"GestureDetector: Current gesture '{self.current_gesture}' with confidence {self.gesture_confidence:.2f}.")
        return self.current_gesture, self.gesture_confidence

    def release(self):
        """
        Release MediaPipe resources.
        """
        logger.info("GestureDetector: Releasing MediaPipe resources.")
        self.hands.close()
