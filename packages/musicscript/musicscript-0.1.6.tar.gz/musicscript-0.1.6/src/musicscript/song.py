class Song:
    lyrics: str = ""
    genius_url: str = ""
    performer: str = ""
    comment: str = ""
    composer: str = ""
    grouping: str = ""
    copyright: str = ""
    description: str = ""
    synopsis: str = ""
    path: str = ""
    album_artist: str = ""
    album_name: str = ""
    year: str = ""
    genre: str = ""

    def __init__(self, artist: str, title: str, ext: str, cover: str, track: str = ""):
        self.artist = artist
        self.title = title
        self.ext = ext
        self.cover = cover
        self.track = track
