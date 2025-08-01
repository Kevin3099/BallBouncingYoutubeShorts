CONFIG = {
    "DEV_MODE": False,
    "VIDEO_DURATION": 28,
    "VIDEO_SIZE": (1080, 1920),
    "FPS": 60,
    "BACKGROUND_COLOR": (20, 20, 20),
    "FONT_PATH": "fonts/OpenSans_Condensed-Bold.ttf",
    "OUTPUT_FILE": "output/MillionDollarBaby.mp4",
    "SONG_PATH": "sounds/MillionDollarBaby.mp3",
    "VOLUME": 0.6,
    "AUDIO_FPS": 44100,
    "TEXT_COLOR": (255, 255, 255),
    "TEXT_CLIPS": [
        {"text": "Guess the song challenge!", "font_size": 50, "position": ("center", 200), "opacity": 1.0},
        {"text": "I'll Pin First Correct Comment!!", "font_size": 50, "position": ("center", 270), "opacity": 1.0},
        {"text": "@BallPlayingMusic", "font_size": 20, "position": ("center", 1600), "opacity": 0.9}
    ],
    "AUDIO_MODE": "mixed",
    "BALL_AUDIO": {
        "0": {"mode": "song", "path": "sounds/MillionDollarBaby.mp3"},
    },

    # "BALL_AUDIO": {
    # str(i): {"mode": "song", "path": "sounds/KSI.mp3"} for i in range(18)
    # },
    "BALL_SETTINGS": {
        "radius": 30,
        "start_speed": 200,
        "speed_increment": 70,
        "start_color": (255, 0, 0),
        "start_time": 0,
        "move_start_time": 0,
        "free_time": 35,
        "start_pos": (560, 460), #540 960
        "id": 0,
        "border_color": (0, 0, 0),
        "trail_enabled": True,
        "trail_lock_appearance": True, 
        "trail_length": 1000,
        "trail_fade_time": 1000,
        "trail_thickness": 30,
        "trail_color_mode": "fade",
        "trail_color": (0, 0, 255),
        "trail_match_radius": True,
        "bounce_on_edges": False,
        "gravity_enabled": True,
        "gravity_strength": 80,
        "restitution": 1,
        "grow_start_radius": 30,
        "grow_end_radius": 500,
        "grow_start_time": 1,
        "grow_end_time": 38,
        "border_color_mode": "cycle",  # or "static"
        "border_color": (0, 0, 0),     # starting border color if static
        "initial_velocity": [1,-1],  # vx, vy in pixels/sec
    },
    "CIRCLE_OBSTACLE_COUNT": 1,
    "CIRCLE_OBSTACLE_START_RADIUS": 550,
    "CIRCLE_OBSTACLE_RADIUS_STEP": 50,
    "CIRCLE_OBSTACLE_END_RADIUS_STEP": 700,
    "ROTATION_SPEED_DEG": 60,
    "GAP_ANGLE_DEG": 0,
    "START_TIME": 0,
    "END_TIME": 9999,
    "CIRCLE_FILL_COLOR": (255,255,255)
}

# Apply dev-mode overrides
if CONFIG["DEV_MODE"]:
    CONFIG["VIDEO_SIZE"] = (1080, 1920)
    CONFIG["FPS"] = 15
    CONFIG["VIDEO_DURATION"] = 15
