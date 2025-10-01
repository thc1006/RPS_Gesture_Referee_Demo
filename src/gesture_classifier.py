"""
GestureClassifier Module - Hand Gesture Recognition
TDD GREEN Phase: Minimal implementation to pass tests
"""
import math
from dataclasses import dataclass
from typing import List


@dataclass
class GestureResult:
    """Result of gesture classification"""
    gesture: str  # "rock" | "paper" | "scissors" | "unknown"
    finger_states: List[int]  # [thumb, index, middle, ring, pinky] - 0=folded, 1=extended
    confidence: float  # Confidence score (0.0-1.0)


class GestureClassifier:
    """
    Classify hand gestures based on MediaPipe landmarks

    Uses angle-based finger state detection:
    - Angle > threshold → finger extended (1)
    - Angle ≤ threshold → finger folded (0)
    """

    def __init__(self, angle_threshold: float = 130.0):
        """
        Initialize classifier

        Args:
            angle_threshold: Angle threshold for finger extension detection (degrees)
        """
        self.angle_threshold = angle_threshold

    def _calculate_angle(self, p1, p2, p3) -> float:
        """
        Calculate angle at p2 formed by p1-p2-p3

        Reuses findAngleF logic from original notebook:
        - Calculate vectors from p2 to p1 and p2 to p3
        - Use arctan2 to get angles
        - Return absolute difference

        Args:
            p1, p2, p3: Landmarks with x, y attributes

        Returns:
            Angle in degrees (0-180)
        """
        # Calculate radians for each point relative to p2
        radians1 = math.atan2(p1.y - p2.y, p1.x - p2.x)
        radians3 = math.atan2(p3.y - p2.y, p3.x - p2.x)

        # Calculate angle difference
        angle = abs(math.degrees(radians1 - radians3))

        # Normalize to 0-180 range
        if angle > 180:
            angle = 360 - angle

        return angle

    def _compute_finger_states(self, landmarks) -> List[int]:
        """
        Compute binary finger states for all 5 fingers

        MediaPipe hand landmarks (21 points):
        - 0: Wrist
        - 1-4: Thumb (CMC, MCP, IP, TIP)
        - 5-8: Index (MCP, PIP, DIP, TIP)
        - 9-12: Middle (MCP, PIP, DIP, TIP)
        - 13-16: Ring (MCP, PIP, DIP, TIP)
        - 17-20: Pinky (MCP, PIP, DIP, TIP)

        For each finger, calculate angle at PIP joint:
        - Thumb: angle at landmark 2 (MCP-IP-TIP)
        - Others: angle at PIP joint

        Args:
            landmarks: List of 21 MediaPipe landmarks

        Returns:
            List of 5 integers [thumb, index, middle, ring, pinky]
            Each value is 0 (folded) or 1 (extended)
        """
        finger_states = []

        # Define finger joint indices for angle calculation
        # Format: (joint_before, joint_middle, joint_after)
        finger_joints = [
            (1, 2, 3),   # Thumb: CMC-MCP-IP
            (5, 6, 7),   # Index: MCP-PIP-DIP
            (9, 10, 11), # Middle: MCP-PIP-DIP
            (13, 14, 15),# Ring: MCP-PIP-DIP
            (17, 18, 19) # Pinky: MCP-PIP-DIP
        ]

        for j1, j2, j3 in finger_joints:
            angle = self._calculate_angle(
                landmarks[j1],
                landmarks[j2],
                landmarks[j3]
            )

            # Extended if angle > threshold
            state = 1 if angle > self.angle_threshold else 0
            finger_states.append(state)

        return finger_states

    def _match_gesture(self, finger_states: List[int]) -> str:
        """
        Match finger state pattern to gesture

        Patterns:
        - Rock: [0, 0, 0, 0, 0] - all fingers folded
        - Paper: [1, 1, 1, 1, 1] - all fingers extended
        - Scissors: [0, 1, 1, 0, 0] - index and middle extended

        Args:
            finger_states: List of 5 binary values

        Returns:
            Gesture name: "rock" | "paper" | "scissors" | "unknown"
        """
        # Define gesture patterns
        patterns = {
            "rock": [0, 0, 0, 0, 0],
            "paper": [1, 1, 1, 1, 1],
            "scissors": [0, 1, 1, 0, 0]
        }

        # Match against known patterns
        for gesture_name, pattern in patterns.items():
            if finger_states == pattern:
                return gesture_name

        return "unknown"

    def classify(self, landmarks) -> GestureResult:
        """
        Classify hand gesture from landmarks

        Args:
            landmarks: List of 21 MediaPipe hand landmarks

        Returns:
            GestureResult with gesture name, finger states, and confidence
        """
        # Compute finger states
        finger_states = self._compute_finger_states(landmarks)

        # Match to gesture pattern
        gesture = self._match_gesture(finger_states)

        # Calculate confidence (1.0 for known gestures, 0.5 for unknown)
        confidence = 1.0 if gesture != "unknown" else 0.5

        return GestureResult(
            gesture=gesture,
            finger_states=finger_states,
            confidence=confidence
        )


# TDD GREEN: All tests should now pass!
# Run: pytest tests/test_gesture_classifier.py -v
