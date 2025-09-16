import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


def linkify(s: str) -> str:
    s = s.replace("&", "and")
    s = re.sub(r"[^\w\s]", "", s)
    s = s.replace(" ", "-")
    return s


def remove_feat(song_title: str) -> str:
    _lookup = ["ft.", "ft", "feat", "feat."]
    pattern = r"(\(|\[)(ft|Ft|Feat|feat)(.)+?(\)|\])\s|(Ft|ft|feat|Feat)([^\[\(|\n]+)\s"
    title = re.sub(pattern, "", song_title + "\n")
    return title.strip()


def build_link(artist: str, title: str) -> str:
    BASE_URL = "https://genius.com/"
    SUFFIX = "-lyrics"

    artist = linkify(artist)

    title = linkify(remove_feat(title))

    if artist:
        return BASE_URL + unidecode(artist + "-" + title) + SUFFIX
    else:
        return BASE_URL + unidecode(title) + SUFFIX


def get_lyrics(artist: str, title: str) -> str:
    url = build_link(artist, title)
    try:
        response = requests.get(url)
    except:
        print("[Get Lyrics]: request failed")
        return ""

    soup = BeautifulSoup(response.content, features="html.parser")
    div = soup.find_all(attrs={"data-lyrics-container": "true"})

    if div:
        lyrics = "\n".join([lyrics.get_text(separator="\n") for lyrics in div])
        return lyrics
    else:
        return ""
