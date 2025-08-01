import cv2
import numpy as np

class Ball:
    COLORS = [
    (0, 0, 255), (14, 0, 255), (28, 0, 255), (42, 0, 255), (56, 0, 255), (71, 0, 255), (85, 0, 255), (99, 0, 255), (113, 0, 255), (128, 0, 255), (128, 0, 255), (113, 0, 255), (99, 0, 255), (85, 0, 255), (71, 0, 255), (56, 0, 255), (42, 0, 255), (28, 0, 255), (14, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255)
    ]


    BORDER_COLORS = [
        (0, 0, 0), (8, 8, 8), (16, 16, 16), (24, 24, 24), (32, 32, 32), (40, 40, 40), (48, 48, 48), (56, 56, 56),
        (64, 64, 64), (72, 72, 72), (80, 80, 80), (88, 88, 88), (96, 96, 96), (104, 104, 104), (112, 112, 112),
        (120, 120, 120), (128, 128, 128), (136, 136, 136), (144, 144, 144), (152, 152, 152), (160, 160, 160),
        (168, 168, 168), (176, 176, 176), (184, 184, 184), (192, 192, 192), (200, 200, 200), (208, 208, 208),
        (216, 216, 216), (220, 220, 220), (216, 216, 216), (208, 208, 208), (200, 200, 200), (192, 192, 192),
        (184, 184, 184), (176, 176, 176), (168, 168, 168), (160, 160, 160), (152, 152, 152), (144, 144, 144),
        (136, 136, 136), (128, 128, 128), (120, 120, 120), (112, 112, 112), (104, 104, 104), (96, 96, 96),
        (88, 88, 88), (80, 80, 80), (72, 72, 72), (64, 64, 64), (56, 56, 56), (48, 48, 48), (40, 40, 40),
        (32, 32, 32), (24, 24, 24), (16, 16, 16), (8, 8, 8)
    ]

    def __init__(self, video_size, radius=50, start_speed=300, speed_increment=30, frozen_color=(255, 255, 255),
                 start_color=None, start_time=0, move_start_time=0, free_time=None,
                 start_pos=None, id="ball", border_color=None,
                 trail_enabled=False, trail_length=20, trail_fade_time=1.0,
                 trail_thickness=2, trail_color_mode="fade", trail_color=(200, 200, 200),
                 trail_match_radius=False, bounce_on_edges=True, gravity_enabled=False,
                 gravity_strength=200, restitution=0.8,
                 grow_start_radius=None, grow_end_radius=None,
                 grow_start_time=None, grow_end_time=None,
                 initial_velocity=None, trail_lock_appearance=False,
                 border_color_mode="static"):
        self.id = id
        self.video_width, self.video_height = video_size
        self.radius = radius
        self.pos = np.array(start_pos if start_pos else [video_size[0] / 2, video_size[1] / 2], dtype=float)

        if initial_velocity is not None:
            direction = np.array(initial_velocity, dtype=float)
            norm = np.linalg.norm(direction)
            self.velocity = direction / norm * start_speed if norm > 0 else np.array([0, start_speed], dtype=float)
        else:
            self.velocity = np.array([0, start_speed], dtype=float)

        self.speed_increment = speed_increment
        self.border_color_mode = border_color_mode
        self.border_color_index = 0
        self.border_color = border_color if border_color is not None else self.BORDER_COLORS[0]
        self.start_time = start_time
        self.move_start_time = move_start_time
        self.free_time = free_time
        self.color_index = 0 if start_color is None else (
            self.COLORS.index(start_color) if start_color in self.COLORS else 0
        )
        self.color = self.COLORS[self.color_index]
        self.frozen_color = frozen_color
        self.trail_enabled = trail_enabled
        self.trail_length = trail_length
        self.trail_fade_time = trail_fade_time
        self.trail_thickness = trail_thickness
        self.trail_color_mode = trail_color_mode
        self.trail_color = trail_color
        self.trail_match_radius = trail_match_radius
        self.trail = []
        self.trail_lock_appearance = trail_lock_appearance
        self.is_visible = False
        self.is_moving = False
        self.gravity_enabled = gravity_enabled
        self.gravity_strength = gravity_strength
        self.bounce_on_edges = bounce_on_edges
        self.restitution = restitution
        self.grow_start_radius = grow_start_radius
        self.grow_end_radius = grow_end_radius
        self.grow_start_time = grow_start_time
        self.grow_end_time = grow_end_time

    def next_color(self):
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        self.color = self.COLORS[self.color_index]

    def update(self, dt, current_time, on_bounce=None):
        if self.grow_start_radius is not None and self.grow_end_radius is not None and \
           self.grow_start_time is not None and self.grow_end_time is not None and \
           self.grow_start_time <= current_time <= self.grow_end_time:
            progress = (current_time - self.grow_start_time) / (self.grow_end_time - self.grow_start_time)
            self.radius = self.grow_start_radius + progress * (self.grow_end_radius - self.grow_start_radius)

        self.is_visible = current_time >= self.start_time
        self.is_moving = current_time >= self.move_start_time

        if self.free_time and current_time >= self.free_time:
            self.is_moving = False
            self.color = self.frozen_color

        if not self.is_moving:
            return

        if self.gravity_enabled:
            self.velocity[1] += self.gravity_strength * dt

        if self.trail_enabled:
            if self.trail_lock_appearance:
                self.trail.append((self.pos.copy(), current_time, self.color, self.border_color, self.radius))
            else:
                self.trail.append((self.pos.copy(), current_time))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

        self.pos += self.velocity * dt
        bounced = False

        if self.bounce_on_edges:
            if self.pos[0] - self.radius <= 0:
                self.pos[0] = self.radius
                self.velocity[0] *= -1
                bounced = True
            elif self.pos[0] + self.radius >= self.video_width:
                self.pos[0] = self.video_width - self.radius
                self.velocity[0] *= -1
                bounced = True

            if self.pos[1] - self.radius <= 0:
                self.pos[1] = self.radius
                self.velocity[1] *= -1
                bounced = True
            elif self.pos[1] + self.radius >= self.video_height:
                self.pos[1] = self.video_height - self.radius
                self.velocity[1] *= -1
                bounced = True

        if bounced:
            if self.restitution == 0:
                self.velocity = np.zeros_like(self.velocity)
            else:
                self.velocity *= self.restitution

            speed = np.linalg.norm(self.velocity)
            if speed > 0:
                self.velocity = (self.velocity / speed) * (speed + self.speed_increment)

            self.next_color()

            if self.border_color_mode == "cycle":
                self.border_color_index = (self.border_color_index + 1) % len(self.BORDER_COLORS)
                self.border_color = self.BORDER_COLORS[self.border_color_index]

            if on_bounce:
                on_bounce(current_time)

        if np.linalg.norm(self.velocity) < 1e-3:
            self.velocity = np.zeros_like(self.velocity)

    def draw(self, frame, current_time):
        if not self.is_visible:
            return

        if self.trail_enabled:
            for trail_point in self.trail:
                if self.trail_lock_appearance:
                    pos, t, color, border_color, radius = trail_point
                else:
                    pos, t = trail_point
                    color = self.color if self.trail_color_mode == "fade" else self.trail_color
                    border_color = self.border_color
                    radius = self.radius if self.trail_match_radius else self.trail_thickness

                alpha = max(0, 1.0 - (current_time - t) / self.trail_fade_time)
                if alpha <= 0:
                    continue

                pos_int = tuple(np.round(pos).astype(int))
                draw_radius = int(radius if self.trail_lock_appearance else max(1, radius * alpha))

                if border_color is not None:
                    cv2.circle(frame, pos_int, draw_radius, border_color, -1)

                fill_radius = max(1, draw_radius - 3)
                draw_color = (np.array(color) * alpha).astype(np.uint8).tolist() if not self.trail_lock_appearance else color
                cv2.circle(frame, pos_int, fill_radius, draw_color, -1)

        cv2.circle(frame, tuple(self.pos.astype(int)), int(self.radius), self.color, -1)
        if self.border_color:
            cv2.circle(frame, tuple(self.pos.astype(int)), int(self.radius), self.border_color, 3)
