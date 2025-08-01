from moviepy import AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np

def make_silence(duration, fps=44100):
    n_samples = int(duration * fps)
    silent_array = np.zeros((n_samples, 2), dtype=np.float32)  # Stereo silence
    return AudioArrayClip(silent_array, fps=fps)

def merge_bounce_times(bounce_times, chunk_duration=0.1):
    """Groups nearby bounce times into continuous intervals for song-mode syncing."""
    if not bounce_times:
        return []
    bounce_times.sort()
    intervals = []
    current_start = bounce_times[0]
    current_end = current_start + chunk_duration
    for t in bounce_times[1:]:
        if t <= current_end:
            current_end = max(current_end, t + chunk_duration)
        else:
            intervals.append((current_start, current_end))
            current_start = t
            current_end = t + chunk_duration
    intervals.append((current_start, current_end))
    return intervals

def build_song_audio(duration, collision_intervals, song_path, volume=1.0, fps=44100):
    try:
        full_audio = AudioFileClip(song_path)
    except Exception as e:
        print(f"Error loading song audio file: {e}")
        return None

    segments = []
    song_cursor = 0.0
    timeline_cursor = 0.0

    for start, end in collision_intervals:
        buffer = 0.1
        extended_end = min(end + buffer, duration)
        duration_chunk = extended_end - start

        if start > timeline_cursor:
            segments.append(make_silence(start - timeline_cursor, fps=fps))
            timeline_cursor = start

        if song_cursor + duration_chunk <= full_audio.duration:
            music_chunk = full_audio.subclipped(song_cursor, song_cursor + duration_chunk)
        else:
            music_chunk = full_audio.subclipped(song_cursor, full_audio.duration)

        segments.append(music_chunk)
        timeline_cursor = extended_end
        song_cursor += duration_chunk

        if timeline_cursor >= duration:
            break

    if timeline_cursor < duration:
        segments.append(make_silence(duration - timeline_cursor, fps=fps))

    return concatenate_audioclips(segments).with_duration(duration)

def build_clip_audio(duration, collision_events, fps=44100):
    """Constructs audio from short clips played on each collision event."""
    if not collision_events:
        return make_silence(duration, fps)

    try:
        clips = []
        last_time = 0.0
        for t, path in sorted(collision_events):
            if t > last_time:
                clips.append(make_silence(t - last_time, fps=fps))
            clip = AudioFileClip(path)
            clips.append(clip)
            last_time = t + clip.duration
        if last_time < duration:
            clips.append(make_silence(duration - last_time, fps=fps))
        return concatenate_audioclips(clips).with_duration(duration)
    except Exception as e:
        print(f"Error building clip audio: {e}")
        return make_silence(duration, fps)
