import os
from musicscript.program_runner import ProgramRunner
from musicscript.runner import Runner
from musicscript.song import Song
from musicscript.album import Album
from musicscript.utils import get_name_format
from musicscript.lyrics import get_lyrics


def add_songs(album: Album, log=False):
    """Populate songs array in Album data structure"""

    files = os.listdir(album.download_path)

    for file in files:
        # 1. Add song title, and track number
        (track, artists, title, ext) = get_name_format(file)
        song = Song(
            artist=artists, title=title, track=track, cover=album.cover, ext=ext
        )

        # 2. Add artist(s)
        if not artists:
            song.artist = album.album_artist

        # 3. Add song lyrics from genius
        lyrics = get_lyrics(song.artist, song.title)
        song.lyrics = lyrics

        # 4. Rename song path
        old_path = album.download_path + file
        assert os.path.isfile(old_path), f"[Path Error]: New path not found {old_path}"

        new_path = album.download_path + song.title + ext
        os.rename(old_path, new_path)

        assert os.path.isfile(new_path), f"[Path Error]: New path not found {new_path}"

        # 5. TODO: Add composers & Other metadata
        song.copyright = album.copyright
        song.year = album.year
        song.genre = album.genre

        # 6. Add song to album
        album.songs.append(song)

    if log:
        print("📦 Renamed Songs Complete")


def write_metadata(album: Album, log=False):
    """Add song metadata, ex. Artist Name, Album Name"""

    for song in album.songs:
        # Create and merge cover stream
        album_name = "album=" + f"{album.album_name}"
        title = "title=" + f"{song.title}"
        artist = "artist=" + f"{song.artist}"
        album_artist = "album_artist=" + f"{album.album_artist}"
        year = "year=" + f"{song.year}"
        track = "track=" + f"{song.track}"
        comment = "comment=" + f"{song.comment}"
        genre = "genre=" + f"{song.genre}"
        copyright = "copyright=" + f"{song.copyright}"
        description = "description=" + f"{song.description}"
        grouping = "grouping=" + f"{song.grouping}"
        lyrics = "lyrics=" + f"{song.lyrics}"

        old_path = album.download_path + song.title + song.ext
        # assert os.path.isfile(old_path), f"[Path Error]: Old path not valid {old_path}"
        song.path = album.path + song.title + song.ext

        metadata_args = [
            "ffmpeg",
            "-i",
            old_path,
            "-i",
            song.cover,
            "-map",
            "0",
            "-map",
            "1",
            "-c",
            "copy",
            "-disposition:1",
            "attached_pic",
            "-y",
            "-metadata",
            album_name,
            "-metadata",
            artist,
            "-metadata",
            album_artist,
            "-metadata",
            title,
            "-metadata",
            year,
            "-metadata",
            track,
            "-metadata",
            comment,
            "-metadata",
            genre,
            "-metadata",
            copyright,
            "-metadata",
            description,
            "-metadata",
            grouping,
            "-metadata",
            lyrics,
            song.path,
        ]

        # Run ffmpeg with cover args
        p = ProgramRunner(program=metadata_args)
        res = p.run()

        if log:
            print("📦 Adding Song metadata:", res[1], song.path)
            if res[0].stderr:
                print("🪵 Log:", res[0].stderr)
            if res[1] == Runner().PASS:
                args = ["rm", f"{old_path}"]
                p = ProgramRunner(program=args)
                p.run()

    # Clean download directory
    if len(os.listdir(album.download_path)) == 0:
        args = ["rm", "-rf", f"{album.download_path}"]
        p = ProgramRunner(program=args)
        p.run()
        print("🧹 Cleaned download directory")
    else:
        print("⚠️ Error: Download directory has aritfacts, something went wrong")
