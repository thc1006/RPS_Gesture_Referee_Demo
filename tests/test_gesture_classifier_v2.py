"""
Tests for GestureClassifier V2
測試改進版手勢分類器
"""
import pytest
from dataclasses import dataclass
from src.gesture_classifier_v2 import GestureClassifierV2, GestureResult


@dataclass
class MockLandmark:
    """Mock MediaPipe landmark"""
    x: float
    y: float
    z: float = 0.0


class TestGestureClassifierV2FuzzyMatching:
    """Test fuzzy matching logic"""

    def test_rock_with_thumb_extended(self):
        """Test rock gesture with thumb slightly extended (common issue)"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        # Simulate: thumb extended, other fingers folded
        finger_states = [1, 0, 0, 0, 0]
        gesture = classifier._fuzzy_match_gesture(finger_states)

        assert gesture == "rock"  # Should still recognize as rock

    def test_paper_with_one_finger_bent(self):
        """Test paper with one finger not fully extended"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        # 4 out of 5 fingers extended
        finger_states = [1, 1, 1, 1, 0]  # Pinky bent
        gesture = classifier._fuzzy_match_gesture(finger_states)

        assert gesture == "paper"

    def test_scissors_with_ring_finger_up(self):
        """Test scissors with ring finger slightly up (common issue)"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        # Index + middle + ring extended
        finger_states = [0, 1, 1, 1, 0]
        gesture = classifier._fuzzy_match_gesture(finger_states)

        assert gesture == "scissors"  # Should still match

    def test_exact_patterns_still_work(self):
        """Test that exact patterns still match correctly"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        assert classifier._fuzzy_match_gesture([0, 0, 0, 0, 0]) == "rock"
        assert classifier._fuzzy_match_gesture([1, 1, 1, 1, 1]) == "paper"
        assert classifier._fuzzy_match_gesture([0, 1, 1, 0, 0]) == "scissors"

    def test_unknown_patterns(self):
        """Test that truly unknown patterns return unknown"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        # Only thumb extended
        assert classifier._fuzzy_match_gesture([1, 0, 0, 0, 0]) == "rock"  # Fuzzy match to rock

        # Only index extended
        assert classifier._fuzzy_match_gesture([0, 1, 0, 0, 0]) == "unknown"

        # Thumb + pinky (rock sign)
        assert classifier._fuzzy_match_gesture([1, 0, 0, 0, 1]) == "rock"  # Fuzzy match


class TestGestureClassifierV2PerFingerThresholds:
    """Test per-finger threshold system"""

    def test_different_thresholds_per_finger(self):
        """Test that different fingers have different thresholds"""
        classifier = GestureClassifierV2()

        assert classifier.finger_thresholds["thumb"] == 120.0   # Lowest
        assert classifier.finger_thresholds["index"] == 140.0   # Standard
        assert classifier.finger_thresholds["middle"] == 140.0  # Standard
        assert classifier.finger_thresholds["ring"] == 135.0    # Slightly lower
        assert classifier.finger_thresholds["pinky"] == 130.0   # Lower

    def test_thumb_easier_to_extend(self):
        """Test that thumb threshold is more lenient"""
        classifier = GestureClassifierV2()

        # Thumb at 125° should be extended (threshold 120°)
        # But index at 125° should be folded (threshold 140°)
        assert 125 > classifier.finger_thresholds["thumb"]    # Extended
        assert 125 < classifier.finger_thresholds["index"]    # Folded


class TestGestureClassifierV2DebugMode:
    """Test debug mode functionality"""

    def test_debug_info_available(self):
        """Test that debug angles are returned"""
        classifier = GestureClassifierV2(debug_mode=True)

        # Create simple landmarks (extended fingers)
        landmarks = []
        landmarks.append(MockLandmark(0.5, 0.9))  # Wrist

        base_x = [0.3, 0.4, 0.5, 0.6, 0.7]
        base_y = 0.8

        for finger_idx in range(5):
            x_base = base_x[finger_idx]
            for joint_idx in range(4):
                x = x_base + joint_idx * 0.001
                y = base_y - joint_idx * 0.15
                landmarks.append(MockLandmark(x, y))

        result = classifier.classify(landmarks)

        assert len(result.debug_angles) == 5  # One angle per finger
        assert all(isinstance(angle, float) for angle in result.debug_angles)

    def test_get_debug_info_format(self):
        """Test debug info formatting"""
        classifier = GestureClassifierV2(debug_mode=True)

        result = GestureResult(
            gesture="rock",
            finger_states=[0, 0, 0, 0, 0],
            confidence=1.0,
            debug_angles=[110.0, 115.0, 120.0, 125.0, 130.0]
        )

        debug_text = classifier.get_debug_info(result)

        assert "=== Debug Info ===" in debug_text
        assert "拇指" in debug_text
        assert "食指" in debug_text
        assert "手勢: ROCK" in debug_text
        assert "信心" in debug_text


class TestGestureClassifierV2Compatibility:
    """Test backward compatibility"""

    def test_can_disable_fuzzy_matching(self):
        """Test that fuzzy matching can be disabled"""
        classifier = GestureClassifierV2(use_fuzzy_matching=False)

        # With fuzzy matching disabled, this should be unknown
        finger_states = [1, 0, 0, 0, 0]  # Thumb extended
        gesture = classifier._exact_match_gesture(finger_states)

        assert gesture == "unknown"

    def test_default_parameters(self):
        """Test default configuration"""
        classifier = GestureClassifierV2()

        assert classifier.angle_threshold == 140.0
        assert classifier.use_fuzzy_matching == True
        assert classifier.debug_mode == False


class TestGestureClassifierV2Integration:
    """Integration tests"""

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
                        x, y = x_base, base_y
                    elif joint_idx == 1:
                        x, y = x_base + 0.05, base_y - 0.05
                    elif joint_idx == 2:
                        x, y = x_base + 0.06, base_y - 0.03
                    else:
                        x, y = x_base + 0.08, base_y + 0.02

                landmarks.append(MockLandmark(x, y))

        return landmarks

    def test_rock_gesture_full_flow(self):
        """Test complete rock gesture recognition"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True, debug_mode=True)

        landmarks = self.create_mock_landmarks([False, False, False, False, False])
        result = classifier.classify(landmarks)

        assert result.gesture == "rock"
        assert result.confidence > 0.5
        assert len(result.debug_angles) == 5

    def test_paper_gesture_full_flow(self):
        """Test complete paper gesture recognition"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        landmarks = self.create_mock_landmarks([True, True, True, True, True])
        result = classifier.classify(landmarks)

        assert result.gesture == "paper"

    def test_scissors_gesture_full_flow(self):
        """Test complete scissors gesture recognition"""
        classifier = GestureClassifierV2(use_fuzzy_matching=True)

        landmarks = self.create_mock_landmarks([False, True, True, False, False])
        result = classifier.classify(landmarks)

        assert result.gesture == "scissors"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
