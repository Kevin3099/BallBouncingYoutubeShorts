# 🎬 Short Social Media Video Generator

A visually stunning and musically interactive video generator where bouncing balls trigger audio and respond to dynamic obstacles — built with Python, OpenCV, and MoviePy.

---

## 🧠 Concept

This project simulates animated balls moving through rotating obstacles and filling space with music. Each ball collision — with walls, obstacles, or other balls — triggers sound playback or contributes to syncing with a backing track. The resulting video is energetic, rhythmic, and ready for platforms like YouTube Shorts or TikTok.

---

## ✨ Features

- 📽️ High-resolution animated video output (1080x1920, 60 FPS)
- 🟠 Dynamic balls with trails, gravity, edge bounces, and color cycling
- 🔄 Rotating circular obstacles with timed gaps and collision handling
- 🎧 Two audio modes:
  - **Clip Mode**: Plays a sound on each collision
  - **Song Mode**: Builds audio synced to bounce intervals
- 🎨 Configurable text overlays and visual style
- ⚙️ Modular, extensible architecture

---

## 📁 Project Structure

```bash
.
├── BallPlayingMusicFill.py   # Main entry point
├── ball.py                   # Ball simulation and rendering
├── obstacle.py               # Obstacle definitions and collision logic
├── music.py                  # Audio syncing and generation
├── config.py                 # Centralized configuration
├── output/                   # Output videos
├── fonts/                    # Custom fonts (e.g., OpenSans)
└── sounds/                   # Sound clips or full songs
```

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install numpy opencv-python moviepy
```

Ensure you have **FFmpeg** installed and available in your system path (required by MoviePy).

---

## 🚀 Quick Start

1. **Add your music** to the `sounds/` directory. Update `SONG_PATH` in `config.py`.

2. **Customize settings** in `config.py`:
   - Ball behavior
   - Visual effects
   - Text overlays
   - Audio mode (`clip` or `song`)

3. **Run the generator**:

```bash
python BallPlayingMusicFill.py
```

4. Your video will be saved to `output/PleasePlease.mp4`.

---

## 🧩 Customization

- **Multiple balls**: Add entries to `BALL_AUDIO` with different IDs and settings.
- **Obstacle designs**: Adjust rotation speed, count, size, and gap logic.
- **Visual themes**: Change trail color modes, text styles, and background color.
- **Audio strategy**: Mix `clip` mode and `song` mode for layered playback.

---

## 🎯 Use Cases

- Music visualizers
- “Guess the Song” challenge videos
- Dynamic intros or shorts for content creators
- Generative art/music experiments

---

## 🧹 Clean & Modular Code

All modules are self-contained, and behavior is configurable via the `CONFIG` dictionary. Add new obstacle types or animation logic without disrupting the core system.
