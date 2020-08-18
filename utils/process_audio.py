import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip


def get_jump_parts(video_clip: str,
                   threshold: float,
                   precision: float,
                   fade_out: float,
                   fade_in: float):
    fade_out = int(fade_out * precision)
    fade_in = int(fade_in * precision)
    clip = VideoFileClip(video_clip)
    cut = lambda i: clip.audio.subclip(i / precision, (i + 1) / precision).to_soundarray(fps=22000)
    volume = lambda array: np.sqrt(((1.0 * array) ** 2).mean())
    volumes = [volume(cut(i)) for i in range(0, int(clip.duration * precision))]

    volumnes_percentages = np.divide(volumes, max(volumes))

    # clip start positions (duration each 0.1 seconds)
    original = []

    for s, vol in enumerate(volumnes_percentages, 0):
        if vol > threshold:
            original.append(s)

    keep = original
    old1_ = keep

    if fade_out > 0:
        fade_list = []
        l = keep
        for i, j in zip(l, l[1:]):
            fade_list.extend(range(i, min(j, i + fade_out + 1)))
        keep = fade_list

    if fade_in > 0:
        fade_list = []
        l = list(reversed(keep))
        for i, j in zip(l, l[1:]):
            s = i - j
            if s > fade_in:
                s = fade_in

            fade_list.extend(reversed(range(i - s, i)))
        keep = list(reversed(fade_list))

    # create durations
    durations = []
    last = keep[0] - 1
    current = keep[0] - 1
    for i in keep:
        current += 1
        if current != i:
            durations.append(((last + 1) / precision, current / precision))
            last = i - 1
            current = i

    # for the last thing
    if last == -1:
        durations.append((0, current / precision))
    else:
        durations.append(((last + 1) / precision, current / precision))

    return [(s * 1000, e * 1000) for s, e in durations]
