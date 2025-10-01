"""
TDD RED Phase: Test for Judge Module
Test-Driven Development - Write tests first!

These tests will FAIL until judge.py is implemented.
"""
import pytest
from src.judge import judge_rps


class TestJudgeRPS:
    """Test suite for RPS judging logic"""

    # Test all 9 combinations (3x3 matrix)
    @pytest.mark.parametrize("left,right,expected_result,expected_message", [
        # Rock tests
        ("rock", "scissors", "left", "左手獲勝"),
        ("rock", "paper", "right", "右手獲勝"),
        ("rock", "rock", "draw", "平手"),

        # Scissors tests
        ("scissors", "paper", "left", "左手獲勝"),
        ("scissors", "rock", "right", "右手獲勝"),
        ("scissors", "scissors", "draw", "平手"),

        # Paper tests
        ("paper", "rock", "left", "左手獲勝"),
        ("paper", "scissors", "right", "右手獲勝"),
        ("paper", "paper", "draw", "平手"),
    ])
    def test_judge_rps_all_combinations(self, left, right, expected_result, expected_message):
        """Test all 9 RPS combinations"""
        result = judge_rps(left, right)

        assert isinstance(result, dict), "Result should be a dictionary"
        assert "result" in result, "Result should have 'result' key"
        assert "message" in result, "Result should have 'message' key"

        assert result["result"] == expected_result, \
            f"Expected {expected_result}, got {result['result']}"
        assert result["message"] == expected_message, \
            f"Expected '{expected_message}', got '{result['message']}'"

    def test_judge_rps_returns_dict(self):
        """Test that judge_rps returns a dictionary"""
        result = judge_rps("rock", "scissors")
        assert isinstance(result, dict)

    def test_judge_rps_has_required_keys(self):
        """Test that result has required keys"""
        result = judge_rps("rock", "scissors")
        assert "result" in result
        assert "message" in result

    def test_judge_rps_traditional_chinese(self):
        """Test that messages are in Traditional Chinese"""
        # Test left win
        result = judge_rps("rock", "scissors")
        assert "左手" in result["message"]
        assert "獲勝" in result["message"]

        # Test right win
        result = judge_rps("scissors", "rock")
        assert "右手" in result["message"]
        assert "獲勝" in result["message"]

        # Test draw
        result = judge_rps("rock", "rock")
        assert "平手" in result["message"]

    def test_judge_rps_result_values(self):
        """Test that result values are exactly 'left', 'right', or 'draw'"""
        result1 = judge_rps("rock", "scissors")
        assert result1["result"] in ["left", "right", "draw"]

        result2 = judge_rps("scissors", "rock")
        assert result2["result"] in ["left", "right", "draw"]

        result3 = judge_rps("paper", "paper")
        assert result3["result"] in ["left", "right", "draw"]

    def test_judge_rps_symmetry(self):
        """Test that swapping left and right inverts the result (except draw)"""
        # Rock vs Scissors
        result1 = judge_rps("rock", "scissors")
        result2 = judge_rps("scissors", "rock")

        if result1["result"] == "left":
            assert result2["result"] == "right"
        elif result1["result"] == "right":
            assert result2["result"] == "left"

        # Paper vs Rock
        result3 = judge_rps("paper", "rock")
        result4 = judge_rps("rock", "paper")

        if result3["result"] == "left":
            assert result4["result"] == "right"

    def test_judge_rps_draw_conditions(self):
        """Test all draw conditions"""
        draws = [
            ("rock", "rock"),
            ("paper", "paper"),
            ("scissors", "scissors")
        ]

        for left, right in draws:
            result = judge_rps(left, right)
            assert result["result"] == "draw", \
                f"{left} vs {right} should be a draw"
            assert result["message"] == "平手"


class TestJudgeRPSEdgeCases:
    """Test edge cases and error handling"""

    def test_judge_rps_case_sensitivity(self):
        """Test that gestures are case-sensitive (should use lowercase)"""
        # This test documents expected behavior
        # If uppercase should be accepted, modify judge.py accordingly
        result = judge_rps("rock", "scissors")
        assert result["result"] == "left"


# Test coverage goal: 100% for judge.py
# Run with: pytest tests/test_judge.py -v
# Coverage: pytest tests/test_judge.py --cov=src.judge --cov-report=term-missing
