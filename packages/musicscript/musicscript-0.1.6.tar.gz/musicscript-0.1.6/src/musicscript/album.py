from typing import List
from musicscript.song import Song


class Album:
    """Class that describes an Album"""

    year: str = ""
    genre: str = ""
    cover: str = ""
    copyright: str = ""

    def __init__(self, url: str, album_artist: str, album_name: str, cover: str):
        self.songs: List[Song] = []
        self.url = url
        self.album_artist = album_artist
        self.album_name = album_name
        self.path = "music/" + album_artist + " - " + album_name + "/"
        self.download_path = self.path + "download/"
        self.cover = cover
