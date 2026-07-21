import math
from constants import MAP_WIDTH, MAP_HEIGHT

class Camera:
    def __init__(self, view_width: int, view_height: int, shake_duration: int = 600, shake_intensity: int = 80):
        self.view_width = view_width
        self.view_height = view_height
        self.shake_trigger_time = -1
        self.shake_duration = shake_duration
        self.shake_intensity = shake_intensity

    def trigger_shake(self, current_time: int):
        self.shake_trigger_time = current_time

    def get_shake_offset(self, current_time: int) -> int:
        if self.shake_trigger_time < 0:
            return 0
        time_since_hit = current_time - self.shake_trigger_time
        if 0 <= time_since_hit < self.shake_duration:
            progress = time_since_hit / self.shake_duration
            decay = 1.0 - progress
            return int(math.sin(time_since_hit * 0.08) * self.shake_intensity * decay)
        return 0

    def get_camera_offset(self, target_x: float, target_y: float) -> tuple[float, float]:
        camera_x = target_x - self.view_width // 2
        camera_y = target_y - self.view_height // 2
        camera_x = max(0, min(camera_x, MAP_WIDTH - self.view_width))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - self.view_height))
        return camera_x, camera_y
