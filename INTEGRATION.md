# Background audio integration

## Supplied logo

The supplied PNG is saved unchanged as `brand_logo.png`, with its transparency
preserved. Place it and `logo_overlay.py` beside `app.py`.

For the Streamlit sidebar, add inside the existing `with st.sidebar:` block:

```python
from logo_overlay import LOGO_PATH, create_logo_overlay

st.image(str(LOGO_PATH), width=180)
```

Replace the final video composition line with this version to display the logo
at the upper left throughout the reel, above the existing subtitle overlays:

```python
logo_clip = create_logo_overlay(total_duration, (1080, 1920))
final_video = CompositeVideoClip(
    [bg_video, sub1, sub2, logo_clip]
).set_audio(full_audio)
```

The logo occupies 22% of the video width and preserves its aspect ratio. Its
position leaves a 4% left margin and an 8% top margin.

## Audio helper

Place `audio_layering.py` beside the supplied `app.py`. This helper targets the
MoviePy 1.x API already used throughout that app (`moviepy==1.0.3`). It is not
a MoviePy 2 migration of the application.

Add this import:

```python
from audio_layering import prepare_ambient_track
```

In `build_final_reel`, replace the existing “Ambient Music Setup” section with:

```python
bg_music = prepare_ambient_track(
    audio_path=ambient_audio_file,
    target_duration=total_duration,
    volume_level=music_volume,  # Existing slider; default 0.08
    fade_seconds=1.5,
)
full_audio = CompositeAudioClip([speech_audio, bg_music]).set_duration(
    total_duration
)
```

Keep the existing video attachment:

```python
final_video = CompositeVideoClip([bg_video, sub1, sub2]).set_audio(full_audio)
```

Keep file-backed clips open until `write_videofile` finishes. Use a `try/finally`
or `contextlib.ExitStack` around the build and register each file-backed clip's
`close` method immediately after opening it (including `bn_audio`, `ar_audio`,
`bg_music`, and the original background `VideoFileClip`). For example:

```python
from contextlib import ExitStack

with ExitStack() as cleanup:
    bn_audio = AudioFileClip(bn_audio_file)
    cleanup.callback(bn_audio.close)
    ar_audio = AudioFileClip(ar_audio_file)
    cleanup.callback(ar_audio.close)
    speech_audio = concatenate_audioclips([bn_audio, ar_audio])
    total_duration = speech_audio.duration

    bg_music = prepare_ambient_track(
        ambient_audio_file, total_duration, music_volume
    )
    cleanup.callback(bg_music.close)
    full_audio = CompositeAudioClip([speech_audio, bg_music]).set_duration(
        total_duration
    )

    # Continue your video/subtitle assembly here, inside the with block.
    # Register the original VideoFileClip before looping/cropping it:
    # cleanup.callback(bg_video.close)
    # Attach full_audio and finish write_videofile inside this block.
```

Start at 8% volume and adjust after listening; source loudness varies. Constant
attenuation does not dynamically duck during speech or guarantee against mix
clipping. The helper fades the outer edges; use a loopable track for smooth
internal repeats. No narration or background audio was supplied for a real mix.

MoviePy 2 uses different imports, effect classes, and `with_audio`:
[official migration guide](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html).
