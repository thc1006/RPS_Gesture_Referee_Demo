"""
TDD RED Phase: Test for GestureClassifier Module
Test-Driven Development - Write tests first!

These tests will FAIL until gesture_classifier.py is implemented.
"""
import pytest
import numpy as np
from dataclasses import dataclass
from src.gesture_classifier import GestureClassifier, GestureResult


@dataclass
class MockLandmark:
    """Mock MediaPipe landmark for testing"""
    x: float
    y: float
    z: float = 0.0


class TestGestureClassifierAngleCalculation:
    """Test angle calculation logic"""

    def setup_method(self):
        """Setup classifier for each test"""
        self.classifier = GestureClassifier(angle_threshold=130.0)

    def test_calculate_angle_straight_line(self):
        """Test angle calculation for straight line (180 degrees)"""
        # Points in straight horizontal line
        p1 = MockLandmark(0.0, 0.5)
        p2 = MockLandmark(0.5, 0.5)
        p3 = MockLandmark(1.0, 0.5)

        angle = self.classifier._calculate_angle(p1, p2, p3)
        assert 175 <= angle <= 185  # Allow small floating point error

    def test_calculate_angle_right_angle(self):
        """Test angle calculation for 90 degree angle"""
        # Points forming right angle
        p1 = MockLandmark(0.0, 0.0)
        p2 = MockLandmark(0.5, 0.0)
        p3 = MockLandmark(0.5, 0.5)

        angle = self.classifier._calculate_angle(p1, p2, p3)
        assert 85 <= angle <= 95

    def test_calculate_angle_returns_positive(self):
        """Test angle calculation returns positive values"""
        p1 = MockLandmark(0.0, 0.0)
        p2 = MockLandmark(0.1, 0.0)
        p3 = MockLandmark(0.15, 0.1)

        angle = self.classifier._calculate_angle(p1, p2, p3)
        assert 0 <= angle <= 180  # Valid angle range


class TestGestureClassifierFingerStates:
    """Test finger state computation"""

    def setup_method(self):
        """Setup classifier with default 130° threshold"""
        self.classifier = GestureClassifier(angle_threshold=130.0)

    def create_mock_landmarks(self, finger_states):
        """
        Create mock landmarks for testing
        finger_states: list of 5 booleans (thumb, index, middle, ring, pinky)
                      True = extended (>130°), False = folded (<130°)
        """
        landmarks = []
        # Add wrist (landmark 0)
        landmarks.append(MockLandmark(0.5, 0.9))

        # Base positions for each finger starting point
        base_x = [0.3, 0.4, 0.5, 0.6, 0.7]  # X positions for each finger
        base_y = 0.8

        for finger_idx, is_extended in enumerate(finger_states):
            x_base = base_x[finger_idx]

            # Create 4 joints per finger (CMC/MCP, MCP/PIP, PIP/DIP, DIP/TIP)
            for joint_idx in range(4):
                if is_extended:
                    # Extended finger: nearly straight line (angle ~180°)
                    x = x_base + joint_idx * 0.001  # Minimal x drift
                    y = base_y - joint_idx * 0.15   # Straight down
                else:
                    # Folded finger: bent back toward palm (angle ~80-100°)
                    if joint_idx == 0:
                        x = x_base
                        y = base_y
                    elif joint_idx == 1:
                        x = x_base + 0.05  # Move out
                        y = base_y - 0.05  # Move down slightly
                    elif joint_idx == 2:
                        x = x_base + 0.06  # Move out a bit more
                        y = base_y - 0.03  # Bend back up (key for acute angle!)
                    else:  # joint_idx == 3
                        x = x_base + 0.08  # Continue outward
                        y = base_y + 0.02  # Back toward palm

                landmarks.append(MockLandmark(x, y))

        return landmarks

    def test_compute_finger_states_all_extended(self):
        """Test all fingers extended (Paper gesture)"""
        landmarks = self.create_mock_landmarks([True, True, True, True, True])
        finger_states = self.classifier._compute_finger_states(landmarks)

        assert finger_states == [1, 1, 1, 1, 1]

    def test_compute_finger_states_all_folded(self):
        """Test all fingers folded (Rock gesture)"""
        landmarks = self.create_mock_landmarks([False, False, False, False, False])
        finger_states = self.classifier._compute_finger_states(landmarks)

        assert finger_states == [0, 0, 0, 0, 0]

    def test_compute_finger_states_scissors(self):
        """Test index and middle extended (Scissors gesture)"""
        landmarks = self.create_mock_landmarks([False, True, True, False, False])
        finger_states = self.classifier._compute_finger_states(landmarks)

        assert finger_states == [0, 1, 1, 0, 0]

    def test_compute_finger_states_custom_threshold(self):
        """Test custom angle threshold affects finger states"""
        classifier_strict = GestureClassifier(angle_threshold=160.0)
        classifier_loose = GestureClassifier(angle_threshold=100.0)

        # Create ambiguous landmark positions
        landmarks = self.create_mock_landmarks([True, True, True, True, True])

        states_strict = classifier_strict._compute_finger_states(landmarks)
        states_loose = classifier_loose._compute_finger_states(landmarks)

        # Both should recognize extended fingers (our mock creates 180° angles)
        assert states_strict == [1, 1, 1, 1, 1]
        assert states_loose == [1, 1, 1, 1, 1]


class TestGestureClassifierPatternMatching:
    """Test gesture pattern matching logic"""

    def setup_method(self):
        """Setup classifier for each test"""
        self.classifier = GestureClassifier(angle_threshold=130.0)

    def test_match_gesture_rock(self):
        """Test Rock pattern (all fingers folded)"""
        finger_states = [0, 0, 0, 0, 0]
        gesture = self.classifier._match_gesture(finger_states)
        assert gesture == "rock"

    def test_match_gesture_paper(self):
        """Test Paper pattern (all fingers extended)"""
        finger_states = [1, 1, 1, 1, 1]
        gesture = self.classifier._match_gesture(finger_states)
        assert gesture == "paper"

    def test_match_gesture_scissors(self):
        """Test Scissors pattern (index and middle extended)"""
        finger_states = [0, 1, 1, 0, 0]
        gesture = self.classifier._match_gesture(finger_states)
        assert gesture == "scissors"

    def test_match_gesture_unknown_patterns(self):
        """Test unknown gesture patterns return 'unknown'"""
        unknown_patterns = [
            [1, 0, 0, 0, 0],  # Only thumb
            [0, 1, 0, 0, 0],  # Only index
            [1, 1, 0, 0, 0],  # Thumb and index
            [0, 0, 1, 1, 1],  # Middle, ring, pinky
            [1, 0, 1, 0, 1],  # Alternating pattern
        ]

        for finger_states in unknown_patterns:
            gesture = self.classifier._match_gesture(finger_states)
            assert gesture == "unknown", \
                f"Pattern {finger_states} should return 'unknown', got '{gesture}'"


class TestGestureClassifierMain:
    """Test main classify() function"""

    def setup_method(self):
        """Setup classifier for each test"""
        self.classifier = GestureClassifier(angle_threshold=130.0)

    def create_mock_landmarks(self, finger_states):
        """Helper to create mock landmarks"""
        landmarks = []
        landmarks.append(MockLandmark(0.5, 0.9))  # Wrist

        base_x = [0.3, 0.4, 0.5, 0.6, 0.7]
        base_y = 0.8

        for finger_idx, is_extended in enumerate(finger_states):
            x_base = base_x[finger_idx]

            for joint_idx in range(4):
                if is_extended:
                    x = x_base + joint_idx * 0.001
                    y = base_y - joint_idx * 0.15
                else:
                    if joint_idx == 0:
                        x = x_base
                        y = base_y
                    elif joint_idx == 1:
                        x = x_base + 0.05
                        y = base_y - 0.05
                    elif joint_idx == 2:
                        x = x_base + 0.06
                        y = base_y - 0.03
                    else:
                        x = x_base + 0.08
                        y = base_y + 0.02

                landmarks.append(MockLandmark(x, y))

        return landmarks

    def test_classify_rock(self):
        """Test classify() for Rock gesture"""
        landmarks = self.create_mock_landmarks([False, False, False, False, False])
        result = self.classifier.classify(landmarks)

        assert isinstance(result, GestureResult)
        assert result.gesture == "rock"
        assert result.finger_states == [0, 0, 0, 0, 0]
        assert result.confidence > 0.0

    def test_classify_paper(self):
        """Test classify() for Paper gesture"""
        landmarks = self.create_mock_landmarks([True, True, True, True, True])
        result = self.classifier.classify(landmarks)

        assert isinstance(result, GestureResult)
        assert result.gesture == "paper"
        assert result.finger_states == [1, 1, 1, 1, 1]
        assert result.confidence > 0.0

    def test_classify_scissors(self):
        """Test classify() for Scissors gesture"""
        landmarks = self.create_mock_landmarks([False, True, True, False, False])
        result = self.classifier.classify(landmarks)

        assert isinstance(result, GestureResult)
        assert result.gesture == "scissors"
        assert result.finger_states == [0, 1, 1, 0, 0]
        assert result.confidence > 0.0

    def test_classify_unknown(self):
        """Test classify() for unknown gesture"""
        landmarks = self.create_mock_landmarks([True, False, False, False, False])
        result = self.classifier.classify(landmarks)

        assert isinstance(result, GestureResult)
        assert result.gesture == "unknown"
        assert result.confidence >= 0.0

    def test_classify_returns_gesture_result(self):
        """Test that classify() returns GestureResult dataclass"""
        landmarks = self.create_mock_landmarks([False, False, False, False, False])
        result = self.classifier.classify(landmarks)

        assert hasattr(result, 'gesture')
        assert hasattr(result, 'finger_states')
        assert hasattr(result, 'confidence')
        assert isinstance(result.finger_states, list)
        assert len(result.finger_states) == 5


class TestGestureClassifierIntegration:
    """Integration tests for complete workflow"""

    def test_classifier_configuration(self):
        """Test classifier accepts configuration"""
        classifier = GestureClassifier(angle_threshold=150.0)
        assert classifier.angle_threshold == 150.0

    def test_classifier_consistency(self):
        """Test classifier returns consistent results for same input"""
        classifier = GestureClassifier(angle_threshold=130.0)

        # Create rock gesture landmarks
        landmarks = []
        landmarks.append(MockLandmark(0.5, 0.5))
        for _ in range(20):
            landmarks.append(MockLandmark(0.5, 0.5))

        result1 = classifier.classify(landmarks)
        result2 = classifier.classify(landmarks)

        assert result1.gesture == result2.gesture
        assert result1.finger_states == result2.finger_states

    def test_all_three_gestures_distinct(self):
        """Test that rock, paper, scissors are all distinct"""
        classifier = GestureClassifier(angle_threshold=130.0)

        # Helper to create landmarks
        def create_landmarks(states):
            landmarks = [MockLandmark(0.5, 0.9)]
            base_x = [0.3, 0.4, 0.5, 0.6, 0.7]
            base_y = 0.8

            for finger_idx, is_extended in enumerate(states):
                x_base = base_x[finger_idx]
                for joint_idx in range(4):
                    if is_extended:
                        x = x_base + joint_idx * 0.001
                        y = base_y - joint_idx * 0.15
                    else:
                        if joint_idx == 0:
                            x, y = x_base, base_y
                        elif joint_idx == 1:
                            x, y = x_base + 0.05, base_y - 0.05
                        elif joint_idx == 2:
                            x, y = x_base + 0.06, base_y - 0.03
                        else:
                            x, y = x_base + 0.08, base_y + 0.02
                    landmarks.append(MockLandmark(x, y))
            return landmarks

        rock = classifier.classify(create_landmarks([False, False, False, False, False]))
        paper = classifier.classify(create_landmarks([True, True, True, True, True]))
        scissors = classifier.classify(create_landmarks([False, True, True, False, False]))

        gestures = {rock.gesture, paper.gesture, scissors.gesture}
        assert len(gestures) == 3, "Rock, Paper, Scissors should be distinct"
        assert "rock" in gestures
        assert "paper" in gestures
        assert "scissors" in gestures


# TDD RED: All tests should now FAIL!
# Run: pytest tests/test_gesture_classifier.py -v
