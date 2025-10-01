"""
Configuration Management for RPS Gesture Referee System
"""
from dataclasses import dataclass, asdict
from typing import Optional
import yaml


@dataclass
class RPSConfig:
    """RPS System Configuration"""

    # Gesture Classification Parameters
    ANGLE_THRESHOLD: float = 130.0  # Finger extension angle threshold

    # State Machine Parameters
    STABLE_FRAMES: int = 5  # Number of stable frames required (N)
    LOCK_DELAY: float = 1.0  # Lock delay in seconds
    REVEAL_DURATION: float = 3.0  # Result display duration in seconds

    # MediaPipe Parameters
    MODEL_COMPLEXITY: int = 0  # 0=fast, 1=accurate
    MIN_DETECTION_CONFIDENCE: float = 0.7
    MIN_TRACKING_CONFIDENCE: float = 0.5
    MAX_NUM_HANDS: int = 2

    # UI Parameters
    MIRROR_MODE: bool = True  # Mirror mode (flip left-right)
    SHOW_LANDMARKS: bool = True  # Show skeleton overlay
    ICON_ALPHA: float = 0.7  # Icon transparency (0-1)

    # Performance Parameters
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    TARGET_FPS: int = 30

    @classmethod
    def from_yaml(cls, path: str) -> 'RPSConfig':
        """Load configuration from YAML file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str):
        """Save configuration to YAML file"""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)


# Default configuration instance
DEFAULT_CONFIG = RPSConfig()
