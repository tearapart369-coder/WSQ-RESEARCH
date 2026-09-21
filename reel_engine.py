"""Local reel export with optional footage and a quiet background track."""
from contextlib import ExitStack
from pathlib import Path
import numpy as np
from PIL import Image
from moviepy.editor import (
    AudioFileClip, ColorClip, CompositeAudioClip, CompositeVideoClip,
    VideoFileClip, concatenate_audioclips, vfx,
)
from audio_layering import prepare_ambient_track
from logo_overlay import create_logo_overlay


def render_reel(narration_paths, output_path, video_path=None,
                ambient_path=None, volume=0.08, fade=1.5,
                size=(540, 960), show_logo=True):
    with ExitStack() as cleanup:
        def own(clip):
            cleanup.callback(clip.close)
            return clip

        narration = own(concatenate_audioclips(
            [own(AudioFileClip(str(path))) for path in narration_paths]
        ))
        duration = narration.duration
        if duration is None or not np.isfinite(duration) or duration <= 0:
            raise ValueError("Please provide a narration file with audible duration.")
        tracks = [narration]
        if ambient_path:
            tracks.append(own(prepare_ambient_track(
                str(ambient_path), duration, volume, fade
            )))
        audio = own(CompositeAudioClip(tracks).set_duration(duration))

        if video_path:
            original = own(VideoFileClip(str(video_path), audio=False))
            if not original.duration or original.duration <= 0:
                raise ValueError("The background video has no duration.")
            video = original.fx(vfx.loop, duration=duration)

            def fit(frame):
                image = Image.fromarray(frame)
                scale = max(size[0] / image.width, size[1] / image.height)
                image = image.resize(
                    (round(image.width * scale), round(image.height * scale)),
                    Image.Resampling.LANCZOS,
                )
                left = (image.width - size[0]) // 2
                top = (image.height - size[1]) // 2
                return np.array(image.crop((left, top, left+size[0], top+size[1])))

            video = video.fl_image(fit)
        else:
            video = own(ColorClip(size, color=(5, 34, 28), duration=duration))
        layers = [video]
        if show_logo:
            layers.append(own(create_logo_overlay(duration, size)))
        final = own(CompositeVideoClip(layers, size=size).set_duration(duration).set_audio(audio))
        final.write_videofile(
            str(output_path), fps=24, codec="libx264", audio_codec="aac",
            audio_bitrate="192k", preset="ultrafast", threads=4, logger=None,
            temp_audiofile=str(Path(output_path).with_suffix(".audio.m4a")),
            remove_temp=True,
        )
    return str(output_path)
