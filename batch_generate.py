import os
import random
import json
import math
import colorsys
import concurrent.futures
import contextlib
import io
from config import CONFIG as BASE_CONFIG
from BallPlayingMusicFill import generate_video

# SETTINGS
ENABLE_MULTIPROCESSING = True
MAX_WORKERS = 5
SKIP_EXISTING = True
SILENT_MODE = True

def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

def generate_multi_stop_gradient(hues, steps=32):
    gradient = []
    segments = len(hues) - 1
    steps_per_segment = steps // segments
    remainder = steps % segments
    for i in range(segments):
        s_hue, e_hue = hues[i], hues[i + 1]
        seg_steps = steps_per_segment + (1 if i < remainder else 0)
        for j in range(seg_steps):
            ratio = j / (seg_steps - 1)
            h = (s_hue + ratio * (e_hue - s_hue)) % 1.0
            rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            gradient.append(tuple(int(c * 255) for c in rgb))
    return gradient

def generate_many_gradients(n=50, steps=32, stops_range=(2, 5)):
    gradients = []
    for _ in range(n):
        base = random.random()
        num_stops = random.randint(*stops_range)
        stops = [(base + i / num_stops) % 1.0 for i in range(num_stops)]
        gradients.append(generate_multi_stop_gradient(stops, steps))
    return gradients

def generate_start_inside_circle(circle_center, min_r, max_r):
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(min_r, max_r)
    x = circle_center[0] + r * math.cos(angle)
    y = circle_center[1] + r * math.sin(angle)
    return [int(x), int(y)]

# Curated + generated gradients
CURATED_HUES = [
    [0.0, 0.1, 0.2], [0.9, 0.7, 0.5], [0.0, 0.33, 0.66, 0.0],
    [0.0, 0.08, 0.17, 0.33], [0.6, 0.4, 0.2, 0.0],
    [0.0, 0.17, 0.33, 0.5], [0.83, 0.66, 0.5, 0.33], [0.0, 0.1, 0.5, 0.9],
]
ALL_GRADIENTS = [generate_multi_stop_gradient(h, 32) for h in CURATED_HUES] + generate_many_gradients(50)

def pick_text_variant():
    options = [
        "Guess the song challenge!",
        "Who know's the song?",
        "Most people don't know the song!",
        "Guess in the comments!",
        "Guess the song! Ball gets bigger and faster!"
    ]
    return random.choice(options)

def build_config(song, output_path):
    song_name = os.path.splitext(song)[0]
    config = json.loads(json.dumps(BASE_CONFIG))

    duration = random.choice([25, 26, 28, 30, 32, 35])
    config["VIDEO_DURATION"] = duration
    config["SONG_PATH"] = os.path.join("sounds", song)

    start_speed = random.randint(180, 250)
    speed_increment = random.randint(40, 100)
    gradient = random.choice(ALL_GRADIENTS)

    config["BALL_SETTINGS"]["start_speed"] = start_speed
    config["BALL_SETTINGS"]["speed_increment"] = speed_increment
    config["BALL_SETTINGS"]["start_color"] = gradient[0]

    circle_radius = config["CIRCLE_OBSTACLE_START_RADIUS"]
    ball_radius = config["BALL_SETTINGS"]["radius"]
    center = [540, 960]

    # Spawn farther from edge, closer to center
    min_r = 100
    max_r = int(circle_radius * 0.6)
    start_pos = generate_start_inside_circle(center, min_r, max_r)
    config["BALL_SETTINGS"]["start_pos"] = start_pos

    # Velocity aimed toward edge
    vx = start_pos[0] - center[0]
    vy = start_pos[1] - center[1]
    config["BALL_SETTINGS"]["initial_velocity"] = [vx, vy]

    config["TEXT_CLIPS"][0]["text"] = pick_text_variant()
    config["OUTPUT_FILE"] = output_path

    return config, gradient

def render_video(song):
    song_name = os.path.splitext(song)[0]
    safe_name = sanitize_filename(song_name)
    output_path = os.path.join("output", f"BallPlay_{safe_name}.mp4")

    if SKIP_EXISTING and os.path.exists(output_path):
        print(f"⏭️  Skipping: {output_path} (already exists)")
        return

    for attempt in range(2):
        try:
            config, gradient = build_config(song, output_path)

            print(f"\n🎵 {song_name} (Attempt {attempt + 1})")
            print(f"   🎨 Colors: {gradient[0]} ➝ {gradient[-1]}")
            print(f"   📽️ Output: {output_path}")

            if SILENT_MODE:
                with contextlib.redirect_stdout(io.StringIO()):
                    generate_video(config, colors=gradient)
            else:
                generate_video(config, colors=gradient)

            return  # success

        except Exception as e:
            print(f"❌ Error generating {song_name} (attempt {attempt + 1}): {e}")

    print(f"🚫 Skipped {song_name} after 2 failed attempts.\n")

def generate_batch():
    os.makedirs("output", exist_ok=True)
    songs = [f for f in os.listdir("sounds") if f.endswith(".mp3")]

    print(f"🔄 Starting batch: {len(songs)} songs")
    if ENABLE_MULTIPROCESSING:
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(render_video, songs)
    else:
        for song in songs:
            render_video(song)
    print("\n✅ Batch complete!")

if __name__ == "__main__":
    generate_batch()
