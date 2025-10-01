"""
GestureClassifier V2 - Optimized for Laptop Webcam
改進版手勢分類器 - 針對筆電鏡頭優化

Key Improvements:
1. 放寬手勢判定邏輯（允許部分手指模糊）
2. 多關節平均角度檢測（更穩定）
3. 自適應閾值系統
4. 視覺調試模式（顯示角度值）
"""
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class GestureResult:
    """Gesture classification result with debug info"""
    gesture: str  # "rock" | "paper" | "scissors" | "unknown"
    finger_states: List[int]  # [thumb, index, middle, ring, pinky]
    confidence: float
    debug_angles: List[float]  # 每根手指的實際角度（用於調試）
    finger_names: List[str] = None  # 手指名稱

    def __post_init__(self):
        if self.finger_names is None:
            self.finger_names = ["拇指", "食指", "中指", "無名指", "小指"]


class GestureClassifierV2:
    """
    Optimized gesture classifier for laptop webcam usage
    針對筆電前鏡頭優化的手勢分類器

    Key features:
    - 放寬角度閾值（更容易識別）
    - 多關節檢測（更穩定）
    - 模糊匹配（允許部分誤差）
    - 調試模式（顯示詳細資訊）
    """

    def __init__(self,
                 angle_threshold: float = 140.0,  # 放寬閾值 130→140
                 use_fuzzy_matching: bool = True,
                 debug_mode: bool = False):
        """
        Initialize optimized classifier

        Args:
            angle_threshold: 手指伸直判定角度（度）- 更寬鬆
            use_fuzzy_matching: 是否使用模糊匹配（允許1-2根手指誤判）
            debug_mode: 是否啟用調試模式（顯示角度值）
        """
        self.angle_threshold = angle_threshold
        self.use_fuzzy_matching = use_fuzzy_matching
        self.debug_mode = debug_mode

        # 針對不同手指設定不同閾值（更符合實際）
        self.finger_thresholds = {
            "thumb": 120.0,   # 大拇指較難伸直，降低閾值
            "index": 140.0,   # 食指標準閾值
            "middle": 140.0,  # 中指標準閾值
            "ring": 135.0,    # 無名指較難獨立控制，降低閾值
            "pinky": 130.0    # 小指最難控制，最低閾值
        }

    def _calculate_angle(self, p1, p2, p3) -> float:
        """Calculate angle at p2 formed by p1-p2-p3"""
        radians1 = math.atan2(p1.y - p2.y, p1.x - p2.x)
        radians3 = math.atan2(p3.y - p2.y, p3.x - p2.x)
        angle = abs(math.degrees(radians1 - radians3))
        if angle > 180:
            angle = 360 - angle
        return angle

    def _calculate_multi_joint_angle(self, landmarks, joints: List[Tuple[int, int, int]]) -> float:
        """
        Calculate average angle across multiple joints (more stable)
        計算多個關節的平均角度（更穩定）

        Args:
            landmarks: MediaPipe landmarks
            joints: List of (j1, j2, j3) joint triplets

        Returns:
            Average angle across all joints
        """
        angles = []
        for j1, j2, j3 in joints:
            angle = self._calculate_angle(landmarks[j1], landmarks[j2], landmarks[j3])
            angles.append(angle)

        return sum(angles) / len(angles) if angles else 0.0

    def _compute_finger_states(self, landmarks) -> Tuple[List[int], List[float]]:
        """
        Compute binary finger states with per-finger thresholds
        使用每根手指專屬閾值計算手指狀態

        Returns:
            (finger_states, debug_angles)
        """
        finger_configs = [
            ("thumb", [(1, 2, 3), (2, 3, 4)]),        # 大拇指：兩個關節
            ("index", [(5, 6, 7), (6, 7, 8)]),        # 食指：兩個關節
            ("middle", [(9, 10, 11), (10, 11, 12)]),  # 中指：兩個關節
            ("ring", [(13, 14, 15), (14, 15, 16)]),   # 無名指：兩個關節
            ("pinky", [(17, 18, 19), (18, 19, 20)])   # 小指：兩個關節
        ]

        finger_states = []
        debug_angles = []

        for finger_name, joints in finger_configs:
            # 計算多關節平均角度（更穩定）
            avg_angle = self._calculate_multi_joint_angle(landmarks, joints)
            debug_angles.append(avg_angle)

            # 使用該手指的專屬閾值
            threshold = self.finger_thresholds[finger_name]
            state = 1 if avg_angle > threshold else 0
            finger_states.append(state)

        return finger_states, debug_angles

    def _fuzzy_match_gesture(self, finger_states: List[int]) -> str:
        """
        Fuzzy gesture matching allowing 1-2 finger errors
        模糊匹配：允許1-2根手指誤判

        Examples:
        - Rock [0,0,0,0,0] also matches [1,0,0,0,0] (thumb extended)
        - Scissors [0,1,1,0,0] also matches [0,1,1,1,0] (ring finger up)
        """
        # 精確匹配模式
        exact_patterns = {
            "rock": [0, 0, 0, 0, 0],
            "paper": [1, 1, 1, 1, 1],
            "scissors": [0, 1, 1, 0, 0]
        }

        # 先嘗試精確匹配
        for gesture_name, pattern in exact_patterns.items():
            if finger_states == pattern:
                return gesture_name

        if not self.use_fuzzy_matching:
            return "unknown"

        # 模糊匹配規則
        def hamming_distance(a, b):
            """計算兩個列表的差異數量"""
            return sum(1 for x, y in zip(a, b) if x != y)

        # Rock 模糊匹配：允許大拇指或小指誤判
        rock_variants = [
            [0, 0, 0, 0, 0],  # 標準
            [1, 0, 0, 0, 0],  # 大拇指微開
            [0, 0, 0, 0, 1],  # 小指微開
        ]
        for variant in rock_variants:
            if hamming_distance(finger_states, variant) <= 1:
                return "rock"

        # Paper 模糊匹配：允許1根手指未完全伸直
        if sum(finger_states) >= 4:  # 至少4根手指伸直
            return "paper"

        # Scissors 模糊匹配：食指+中指必須伸直，其他可有1根誤判
        if finger_states[1] == 1 and finger_states[2] == 1:  # 食指+中指伸直
            other_fingers = [finger_states[0], finger_states[3], finger_states[4]]
            if sum(other_fingers) <= 1:  # 其他手指最多1根伸直
                return "scissors"

        return "unknown"

    def _exact_match_gesture(self, finger_states: List[int]) -> str:
        """Exact pattern matching (original logic)"""
        patterns = {
            "rock": [0, 0, 0, 0, 0],
            "paper": [1, 1, 1, 1, 1],
            "scissors": [0, 1, 1, 0, 0]
        }

        for gesture_name, pattern in patterns.items():
            if finger_states == pattern:
                return gesture_name

        return "unknown"

    def classify(self, landmarks) -> GestureResult:
        """
        Classify hand gesture with enhanced detection

        Returns:
            GestureResult with debug information
        """
        # Compute finger states with debug angles
        finger_states, debug_angles = self._compute_finger_states(landmarks)

        # Match gesture (fuzzy or exact)
        if self.use_fuzzy_matching:
            gesture = self._fuzzy_match_gesture(finger_states)
        else:
            gesture = self._exact_match_gesture(finger_states)

        # Calculate confidence
        if gesture == "unknown":
            confidence = 0.5
        elif self.use_fuzzy_matching:
            # 模糊匹配的confidence較低
            confidence = 0.85
        else:
            # 精確匹配的confidence較高
            confidence = 1.0

        return GestureResult(
            gesture=gesture,
            finger_states=finger_states,
            confidence=confidence,
            debug_angles=debug_angles
        )

    def get_debug_info(self, result: GestureResult) -> str:
        """
        Format debug information for display
        格式化調試資訊
        """
        if not self.debug_mode:
            return ""

        lines = []
        lines.append("=== Debug Info ===")

        for i, (name, state, angle) in enumerate(zip(
            result.finger_names,
            result.finger_states,
            result.debug_angles
        )):
            threshold = list(self.finger_thresholds.values())[i]
            status = "伸直✓" if state == 1 else "彎曲✗"
            lines.append(f"{name}: {angle:.1f}° ({status}, 閾值{threshold:.0f}°)")

        lines.append(f"手勢: {result.gesture.upper()}")
        lines.append(f"信心: {result.confidence:.2f}")

        return "\n".join(lines)


# Backward compatibility: alias to V2
GestureClassifier = GestureClassifierV2

print("✅ GestureClassifier V2 loaded - Optimized for laptop webcam")
