import re
from typing import Tuple


def get_name_format(file_name: str) -> Tuple[str, str, str, str]:
    _track = file_name[:2]
    _title = file_name[3:-4]
    _ext = file_name[-4:]

    try:
        track = get_track_number(_track)
        title = get_song_title(_title)
        artists = get_song_artists(_title)
        return (track, artists, title, _ext)
    except:
        return ("", "", file_name[:-4], _ext)


def get_track_number(track: str) -> str:
    if track == "NA":
        return ""
    try:
        return str(eval(track.lstrip("0")))
    except:
        raise ValueError("Got invalid track number")


def get_song_title(file_title: str) -> str:
    """Gets track name
    example:
        file_name = "01 Artist Name - Song Name.m4a"
        returns: Song Name
    """
    split = file_title.split(" - ")
    if len(split) > 1:
        return remove_title_artifacts("".join(split[1]))
    else:
        return remove_title_artifacts(split[0])


def remove_title_artifacts(title: str):
    split = title.split(" - ")
    if len(split) > 2:
      title = " - ".join(split[:2])
    pattern = r"\s(\(|\[)*(Official|official|Lyric|OFFICIAL|Audio|Visualizer|Exclusive|Music)([^\n\]\)])*(\)|\])*"
    new_title = re.sub(pattern, "", title + "\n")
    return new_title.strip()


def get_song_artists(file_name: str) -> str:
    """Returns multiple artist
    example:
        file_name = "Future & Metro Boomin - Like That"
        returns: Future & Metro Boomin
    """
    split = file_name.split(" - ")
    if len(split) > 1:
        return split[0]
    else:
        return ""
