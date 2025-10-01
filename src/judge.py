"""
Judge Module - Rock-Paper-Scissors Judging Logic

TDD GREEN Phase: Minimal implementation to pass tests
"""
from typing import Dict


def judge_rps(left_gesture: str, right_gesture: str) -> Dict[str, str]:
    """
    Judge Rock-Paper-Scissors game between left and right hand

    Args:
        left_gesture: "rock" | "paper" | "scissors"
        right_gesture: "rock" | "paper" | "scissors"

    Returns:
        {
            "result": "left" | "right" | "draw",
            "message": "左手獲勝" | "右手獲勝" | "平手"
        }

    Examples:
        >>> judge_rps("rock", "scissors")
        {"result": "left", "message": "左手獲勝"}

        >>> judge_rps("paper", "rock")
        {"result": "left", "message": "左手獲勝"}

        >>> judge_rps("rock", "rock")
        {"result": "draw", "message": "平手"}
    """
    # Draw condition
    if left_gesture == right_gesture:
        return {"result": "draw", "message": "平手"}

    # Define winning combinations (left hand wins)
    left_wins = {
        ("rock", "scissors"),
        ("scissors", "paper"),
        ("paper", "rock")
    }

    # Check if left hand wins
    if (left_gesture, right_gesture) in left_wins:
        return {"result": "left", "message": "左手獲勝"}
    else:
        return {"result": "right", "message": "右手獲勝"}


# TDD GREEN: All tests should now pass!
# Run: pytest tests/test_judge.py -v
