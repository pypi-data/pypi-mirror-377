import os
import requests
from musicscript.album import Album
from musicscript.download import download
from musicscript.metadata import write_metadata
from musicscript.metadata import add_songs


def main() -> None:
    print("👾 Hello, Music Script")

    # [0]: Get user inputs
    album_artist = input("Enter Artist Name: ")
    album_name = input("Enter Album Name: ")
    url = input("Enter Soundcloud / Youtube Playlist: ")
    cover = input("Enter Image: ")
    year = input("Enter Year: ")
    copyright_ = input("Enter Copyright: ")
    genre = input("Enter Genre: ")

    # Example
    # album_artist = "SZA"
    # album_name = "SOS Deluxe: LANA"
    # url = "https://www.youtube.com/watch?v=wk9kw_k4KNI&list=OLAK5uy_ke8Vb8WmKdgynHjSa7DSPguT58YKEEABQ&index=2"
    # cover = "/Users/meekmsaki/Downloads/sza_lana_cover_1_zujeyx-4125153700-2.jpg"
    # year = "2024"
    # copyright_ = "℗ 2024 Top Dawg Entertainment, under exclusive license to RCA Records"
    # genre = "R&B/SOUL"

    # [1] Test url reponse
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Request failed for url:{url}")
    except:
        raise ValueError(f"Request failed for url:{url}")

    # [2]: Create Album
    album = Album(
        url=url, album_artist=album_artist, album_name=album_name, cover=cover
    )
    album.year = year
    album.copyright = copyright_
    album.genre = genre

    print("📦 Album Directory: ", album.path)

    # [3]: Download songs
    download(album, log=True)

    # [4]: Rename songs
    add_songs(album=album, log=True)

    # [5]. Write metadata
    write_metadata(album, log=True)

    for song in album.songs:
        assert os.path.isfile(
            song.path
        ), f"[Song Path Error]: Can't find added song {song.path}"

    # [4]: Print Results
    print("🗂️ Job Completed: Open", os.getcwd() + "/" + album.path)
    print("💿 Album:", album.album_name)
    print("💿 Artist:", album.album_artist)
    print("💿 Cover:", album.cover)
    print("💿 Year:", album.year)
    print("💿 Genre:", album.genre)
    print("💿 Copyright:", album.copyright)
    print("💿 Songs:", len(album.songs))
    print("🔗 Url:", album.url)


if __name__ == "__main__":
    main()
