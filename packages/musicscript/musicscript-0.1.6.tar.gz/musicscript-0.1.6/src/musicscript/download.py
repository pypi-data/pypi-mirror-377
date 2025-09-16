import os
from musicscript.album import Album
from musicscript.program_runner import ProgramRunner


def download(album: Album, log=False):
    """Download songs using yt-dlp"""

    if album.download_path:
        os.makedirs(album.download_path, exist_ok=True)
    else:
        raise ValueError("[download]: Please provide download directory")

    args = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "-P",
        album.download_path,
        "-vU",
        "-R",
        "inf",
        "--file-access-retries",
        "inf",
        "--fragment-retries",
        "inf",
        "-o",
        "%(playlist_index)02d %(title)s.%(ext)s",
        album.url,
    ]

    p = ProgramRunner(program=args)
    res = p.run()
    if log:
        print("📦 Finished Running download", res[1])
        if res[0].stdout:
            print("🪵 Log: ", res[0].stdout)

    print("🗂️ Download Results: ", res[1])
