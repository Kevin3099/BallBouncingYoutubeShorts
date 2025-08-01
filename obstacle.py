import numpy as np
import random
import cv2

def get_color(t, base_color, color_mode):
    if color_mode == "static":
        return base_color
    elif color_mode == "random":
        return tuple(random.randint(0, 255) for _ in range(3))
    elif color_mode == "time":
        r = int(127 + 127 * np.sin(t))
        g = int(127 + 127 * np.sin(t + 2))
        b = int(127 + 127 * np.sin(t + 4))
        return (r, g, b)
    else:
        return base_color

class BaseObstacle:
    def __init__(self, start_time=0, end_time=9999, color=(255, 255, 255), color_mode="static"):
        self.start_time = start_time
        self.end_time = end_time
        self.base_color = color
        self.color_mode = color_mode

    def is_active(self, t):
        return self.start_time <= t <= self.end_time

    def current_color(self, t):
        return get_color(t, self.base_color, self.color_mode)

    def draw(self, frame, t):
        pass

    def handle_collision(self, ball, t, on_collision=None):
        pass

class ObstacleCircle(BaseObstacle):
    def __init__(self, center, start_radius, end_radius, fill_color=None, **kwargs):
        super().__init__(**kwargs)
        self.center = np.array(center, dtype=float)
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.fill_color = fill_color

    def current_radius(self, t):
        if not self.is_active(t):
            return self.start_radius
        total_time = self.end_time - self.start_time
        progress = min(max((t - self.start_time) / total_time, 0), 1)
        return self.start_radius + (self.end_radius - self.start_radius) * progress

    def draw(self, frame, t):
        if not self.is_active(t):
            return
        radius = int(self.current_radius(t))
        color = self.current_color(t)
        center_int = tuple(self.center.astype(int))

        if self.fill_color:
            cv2.circle(frame, center_int, radius, self.fill_color, -1)

        cv2.circle(frame, center_int, radius, color, 3)

    def handle_collision(self, ball, t, on_collision=None):
        if not self.is_active(t):
            return
        radius = self.current_radius(t)
        delta = ball.pos - self.center
        dist = np.linalg.norm(delta)
        if dist + ball.radius > radius:
            if dist == 0:
                return
            norm = delta / dist
            ball.pos = self.center + norm * (radius - ball.radius)
            velocity_component = np.dot(ball.velocity, norm)
            restitution = getattr(ball, 'restitution', 1.0)
            ball.velocity -= (1 + restitution) * velocity_component * norm

            speed = np.linalg.norm(ball.velocity)
            if speed > 0:
                ball.velocity = (ball.velocity / speed) * (speed + ball.speed_increment)

            ball.next_color()

            if on_collision:
                on_collision(t, ball.id, "obstacle_circle")

class ObstacleSquare(BaseObstacle):
    def __init__(self, center, size, **kwargs):
        super().__init__(**kwargs)
        self.center = np.array(center, dtype=float)
        self.size = size

    def draw(self, frame, t):
        if not self.is_active(t):
            return
        half = self.size // 2
        top_left = (self.center - half).astype(int)
        bottom_right = (self.center + half).astype(int)
        color = self.current_color(t)
        cv2.rectangle(frame, tuple(top_left), tuple(bottom_right), color, 3)

    def handle_collision(self, ball, t, on_collision=None):
        if not self.is_active(t):
            return

        half = self.size / 2
        left = self.center[0] - half
        right = self.center[0] + half
        top = self.center[1] - half
        bottom = self.center[1] + half

        ball_left = ball.pos[0] - ball.radius
        ball_right = ball.pos[0] + ball.radius
        ball_top = ball.pos[1] - ball.radius
        ball_bottom = ball.pos[1] + ball.radius

        if (ball_right > left and ball_left < right and
            ball_bottom > top and ball_top < bottom):

            dx = ball.pos[0] - self.center[0]
            dy = ball.pos[1] - self.center[1]

            if abs(dx) > abs(dy):
                ball.velocity[0] *= -1
            else:
                ball.velocity[1] *= -1

            speed = np.linalg.norm(ball.velocity)
            if speed > 0:
                ball.velocity = (ball.velocity / speed) * (speed + ball.speed_increment)

            while (ball.pos[0] + ball.radius > left and ball.pos[0] - ball.radius < right and
                   ball.pos[1] + ball.radius > top and ball.pos[1] - ball.radius < bottom):
                ball.pos += ball.velocity * 0.01

            ball.next_color()

            if on_collision:
                on_collision(t, ball.id, "obstacle_square")

class CircleWithGap(ObstacleCircle):
    def __init__(self, center, start_radius, end_radius,
                 gap_angle_deg=45, gap_offset_deg=0,
                 rotation_speed_deg=30, rotation_mode="clockwise",
                 disappear_on_gap_pass=False, fill_color=None, **kwargs):
        super().__init__(center, start_radius, end_radius, fill_color=fill_color, **kwargs)
        self.gap_angle_rad = np.deg2rad(gap_angle_deg)
        self.gap_offset_rad = np.deg2rad(gap_offset_deg)
        self.rotation_speed_rad = np.deg2rad(rotation_speed_deg)
        self.rotation_mode = rotation_mode
        self.disappear_on_gap_pass = disappear_on_gap_pass
        self.active = True

    def is_active(self, t):
        return super().is_active(t) and self.active

    def current_gap_angle(self, t):
        if not self.is_active(t):
            return self.gap_offset_rad
        if self.rotation_mode == "none":
            return self.gap_offset_rad
        direction = -1 if self.rotation_mode == "clockwise" else 1
        return (self.gap_offset_rad + self.rotation_speed_rad * t * direction) % (2 * np.pi)

    def draw(self, frame, t):
        if not self.is_active(t):
            return
        radius = int(self.current_radius(t))
        color = self.current_color(t)
        center_int = tuple(self.center.astype(int))

        if self.fill_color:
            cv2.circle(frame, center_int, radius, self.fill_color, -1)

        gap_center = self.current_gap_angle(t)
        start_angle = np.rad2deg((gap_center + self.gap_angle_rad / 2)) % 360
        end_angle = np.rad2deg((gap_center - self.gap_angle_rad / 2)) % 360

        gap_start_deg = end_angle % 360
        gap_end_deg = start_angle % 360

        cv2.ellipse(frame, center_int, (radius, radius), 0, gap_end_deg, 360, color, 3)
        cv2.ellipse(frame, center_int, (radius, radius), 0, 0, gap_start_deg, color, 3)

    def handle_collision(self, ball, t, on_collision=None):
        if not self.is_active(t):
            return

        radius = self.current_radius(t)
        delta = ball.pos - self.center
        dist = np.linalg.norm(delta)

        if dist + ball.radius > radius:
            if dist == 0:
                return

            angle = np.arctan2(delta[1], delta[0]) % (2 * np.pi)
            gap_center = self.current_gap_angle(t)
            gap_start = (gap_center - self.gap_angle_rad / 2) % (2 * np.pi)
            gap_end = (gap_center + self.gap_angle_rad / 2) % (2 * np.pi)

            in_gap = gap_start < gap_end and gap_start <= angle <= gap_end or \
                     gap_start > gap_end and (angle >= gap_start or angle <= gap_end)

            if in_gap:
                if self.disappear_on_gap_pass:
                    self.active = False
            else:
                norm = delta / dist
                ball.pos = self.center + norm * (radius - ball.radius)
                velocity_component = np.dot(ball.velocity, norm)
                restitution = getattr(ball, 'restitution', 1.0)
                ball.velocity -= (1 + restitution) * velocity_component * norm

                speed = np.linalg.norm(ball.velocity)
                if speed > 0:
                    ball.velocity = (ball.velocity / speed) * (speed + ball.speed_increment)

                ball.next_color()

                if on_collision:
                    on_collision(t, ball.id, "circle_with_gap")
