import cv2
import numpy as np
from moviepy import VideoClip, CompositeVideoClip, CompositeAudioClip, TextClip, ColorClip
from ball import Ball
from music import build_song_audio, build_clip_audio, merge_bounce_times
from obstacle import CircleWithGap
from config import CONFIG as DEFAULT_CONFIG
import os

bounce_times = []

def record_bounce(t):
    bounce_times.append(t)

def create_balls(config):
    balls = []
    balls.append(Ball(config["VIDEO_SIZE"], **config["BALL_SETTINGS"]))
    return balls

def create_obstacles(config):
    obstacles = []
    rotation_modes = ["clockwise", "anti-clockwise"]
    for i in range(config["CIRCLE_OBSTACLE_COUNT"]):
        start_radius = config["CIRCLE_OBSTACLE_START_RADIUS"] + i * config["CIRCLE_OBSTACLE_RADIUS_STEP"]
        end_radius = 30 + i * config["CIRCLE_OBSTACLE_END_RADIUS_STEP"]
        rotation_mode = rotation_modes[i % len(rotation_modes)]
        obstacles.append(CircleWithGap(
            center=(540,960),
            start_radius=start_radius,
            end_radius=end_radius,
            gap_angle_deg=config["GAP_ANGLE_DEG"],
            gap_offset_deg=0,
            rotation_speed_deg=config["ROTATION_SPEED_DEG"],
            rotation_mode=rotation_mode,
            disappear_on_gap_pass=True,
            start_time=config["START_TIME"],
            end_time=config["END_TIME"],
            color=(255, 255, 255),
            color_mode="static",
            fill_color=config["CIRCLE_FILL_COLOR"]
        ))
    return obstacles

def resolve_ball_collision(ball1, ball2):
    delta = ball1.pos - ball2.pos
    dist = np.linalg.norm(delta)
    if dist == 0 or dist >= ball1.radius + ball2.radius:
        return False

    norm = delta / dist
    rel_vel = ball1.velocity - ball2.velocity
    vel_along_norm = np.dot(rel_vel, norm)
    if vel_along_norm > 0:
        return False

    restitution = min(ball1.restitution, ball2.restitution)
    impulse = -(1 + restitution) * vel_along_norm / 2
    impulse_vec = impulse * norm

    if ball1.is_moving and ball2.is_moving:
        ball1.velocity += -impulse_vec
        ball2.velocity += impulse_vec
    elif ball1.is_moving:
        ball1.velocity += -2 * impulse_vec
    elif ball2.is_moving:
        ball2.velocity += 2 * impulse_vec

    overlap = (ball1.radius + ball2.radius - dist) / 2
    if ball1.is_moving:
        ball1.pos += norm * overlap
    if ball2.is_moving:
        ball2.pos -= norm * overlap

    return True

def make_frame_factory(balls, obstacles, bounce_times, collision_events, config):
    previous_t = [0.0]
    collided_pairs = set()

    def make_frame(t):
        real_dt = t - previous_t[0]
        previous_t[0] = t
        collided_pairs.clear()

        for ball in balls:
            ball.update(real_dt, t)

        frame = np.full((config["VIDEO_SIZE"][1], config["VIDEO_SIZE"][0], 3), config["BACKGROUND_COLOR"], dtype=np.uint8)

        for obstacle in obstacles:
            for ball in balls:
                def on_collision(t=t, ball_id=ball.id, *_):
                    ball_cfg = config["BALL_AUDIO"].get(str(ball_id), {})
                    mode = ball_cfg.get("mode", "clip")
                    path = ball_cfg.get("path")
                    if mode == "clip" and path:
                        collision_events.append((t, path))
                    elif mode == "song":
                        bounce_times.append(t)
                obstacle.handle_collision(ball, t, on_collision=on_collision)
            obstacle.draw(frame, t)

        for i, ball1 in enumerate(balls):
            for j, ball2 in enumerate(balls):
                if j <= i:
                    continue
                pair_key = tuple(sorted((ball1.id, ball2.id)))
                if pair_key not in collided_pairs:
                    if resolve_ball_collision(ball1, ball2):
                        collided_pairs.add(pair_key)
                        for b in (ball1, ball2):
                            ball_cfg = config["BALL_AUDIO"].get(str(b.id), {})
                            mode = ball_cfg.get("mode", "clip")
                            path = ball_cfg.get("path")
                            if mode == "clip" and path:
                                collision_events.append((t, path))
                            elif mode == "song":
                                bounce_times.append(t)

        for ball in balls:
            ball.draw(frame, t)

        return frame

    return make_frame

def create_text_clips(config):
    clips = []
    for clip_cfg in config["TEXT_CLIPS"]:
        clip = TextClip(
            font=config["FONT_PATH"],
            text=clip_cfg["text"],
            font_size=clip_cfg["font_size"],
            color="#%02x%02x%02x" % tuple(config["TEXT_COLOR"])
        ).with_duration(config["VIDEO_DURATION"]).with_position(clip_cfg["position"]).with_opacity(clip_cfg["opacity"])
        clips.append(clip)
    return clips

# 🔧 MAIN FUNCTION — NEW
def generate_video(config, colors=None):
    global bounce_times

    if colors:
        Ball.COLORS = colors

    background = ColorClip(size=config["VIDEO_SIZE"], color=config["BACKGROUND_COLOR"], duration=config["VIDEO_DURATION"])

    bounce_times = []
    collision_events = []

    balls = create_balls(config)
    obstacles = create_obstacles(config)

    frame_fn_track = make_frame_factory(balls, obstacles, bounce_times, collision_events, config)
    clip_track = VideoClip(lambda t: frame_fn_track(t), duration=config["VIDEO_DURATION"])
    video_track = CompositeVideoClip([background, clip_track] + ([] if config["DEV_MODE"] else create_text_clips(config)))
    video_track.write_videofile("temp_tracking_pass.mp4", fps=config["FPS"], codec="libx264", audio=False)

    collision_intervals = merge_bounce_times(bounce_times)

    balls = create_balls(config)
    obstacles = create_obstacles(config)
    frame_fn_final = make_frame_factory(balls, obstacles, bounce_times=[], collision_events=[], config=config)
    clip_final = VideoClip(lambda t: frame_fn_final(t), duration=config["VIDEO_DURATION"])
    video_final = CompositeVideoClip([background, clip_final] + create_text_clips(config))

    song_audio = build_song_audio(
        duration=config["VIDEO_DURATION"],
        collision_intervals=collision_intervals,
        song_path=config["SONG_PATH"],
        volume=config["VOLUME"],
        fps=config["AUDIO_FPS"]
    )

    clip_audio = build_clip_audio(
        duration=config["VIDEO_DURATION"],
        collision_events=collision_events,
        fps=config["AUDIO_FPS"]
    )

    if song_audio and clip_audio:
        combined_audio = CompositeAudioClip([song_audio, clip_audio])
        video_final = video_final.with_audio(combined_audio)
    elif song_audio:
        video_final = video_final.with_audio(song_audio)
    elif clip_audio:
        video_final = video_final.with_audio(clip_audio)

    os.makedirs(os.path.dirname(config["OUTPUT_FILE"]), exist_ok=True)
    video_final.write_videofile(config["OUTPUT_FILE"], fps=config["FPS"], codec="libx264", audio_codec="aac", preset="ultrafast", threads=2)

# 🔁 Legacy support: run one video directly
if __name__ == "__main__":
    generate_video(DEFAULT_CONFIG)
# If you want to run this script directly, it will generate a video using the default configuration.
