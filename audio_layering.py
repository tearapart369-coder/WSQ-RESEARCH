"""Background audio helper for the supplied MoviePy 1.x reel pipeline."""

from math import isfinite

from moviepy.editor import AudioFileClip, afx


def prepare_ambient_track(
    audio_path: str,
    target_duration: float,
    volume_level: float = 0.08,
    fade_seconds: float = 1.5,
):
    """Return a quiet background clip matching the narration duration.

    Close the returned clip AFTER rendering; its effects share a file reader.
    This is constant attenuation, not speech-responsive ducking. Loop seams
    depend on the source track; only the overall beginning and end are faded.
    """
    if not isfinite(target_duration) or target_duration <= 0:
        raise ValueError("target_duration must be finite and greater than zero")
    if not isfinite(volume_level) or not 0 <= volume_level <= 1:
        raise ValueError("volume_level must be between 0 and 1")
    if not isfinite(fade_seconds) or fade_seconds < 0:
        raise ValueError("fade_seconds must be finite and nonnegative")

    source = AudioFileClip(audio_path)
    try:
        if source.duration is None or not isfinite(source.duration) or source.duration <= 0:
            raise ValueError("Background audio must have a positive finite duration")

        background = source.fx(afx.volumex, volume_level)
        if source.duration < target_duration:
            background = background.fx(afx.audio_loop, duration=target_duration)
        else:
            background = background.subclip(0, target_duration)

        # Avoid overlapping fades on very short reels.
        fade = min(fade_seconds, target_duration / 2)
        if fade:
            background = background.fx(afx.audio_fadein, fade)
            background = background.fx(afx.audio_fadeout, fade)
        background = background.set_duration(target_duration)
        # audio_loop returns a composite whose close() does not own the reader.
        # Preserve one explicit owner for the original file across both paths.
        background.close = source.close
        return background
    except Exception:
        source.close()
        raise
