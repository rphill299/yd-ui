import yt_dlp
import sys
import os
from pathlib import Path

DOWNLOADS_FOLDER = str(Path.home() / 'Downloads')

def get_ffmpeg_path():
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    filename = r'ffmpeg\ffmpeg.exe' if sys.platform.startswith("win") else "ffmpeg"
    path = os.path.join(base, filename)
    return(path)

def get_all_formats(yt_url, neither=False) :

    # set options

    ydl_opts = {
        "ffmpeg_location": get_ffmpeg_path(),
        'quiet': True,          # like verbose = False
        'skip_download': True,   # does not download = Faster
    }

    # get available formats

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(yt_url, download=False)
        formats = info.get('formats', [])

    # split formats into audio, video, and audiovisual (also neither if neither)

    audios = []
    videos = []
    audiovisuals = []
    neithers = []

    for f in formats:

        acodec = f.get('acodec', 'none')
        vcodec = f.get('vcodec', 'none')
        fps = f.get('fps', 0)

        has_audio = acodec != 'none' or fps == 0
        has_video = vcodec != 'none'

        if has_audio and not has_video :
            # audio only
            audios.append(f)

        elif not has_audio and has_video :
            # video only
            videos.append(f)

        elif has_audio and has_video :
            #audiovisual
            audiovisuals.append(f)

        elif neither :
            # no audio or video (i.e. storyboard)
            # no use a.t.m.
            neithers.append(f)

    # return neithers if requested by caller

    if neither :
        return audios, videos, audiovisuals, neithers
    else :
        return audios, videos, audiovisuals

def download(yt_url, audio_id, video_id, out_format='mp4', out_name_template=os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s'))  :

    # set options

    ydl_opts = {
        "ffmpeg_location": get_ffmpeg_path(),
        'format': f'{video_id}+{audio_id}',
        'outtmpl': out_name_template,
        'merge_output_format': out_format,
    }

    # download

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])