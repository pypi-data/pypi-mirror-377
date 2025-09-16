# Music Script

![PyPI - Version](https://img.shields.io/pypi/v/musicscript)
![PyPI - Downloads](https://img.shields.io/pypi/dm/musicscript)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/mmsaki/music-script)
![GitHub License](https://img.shields.io/github/license/mmsaki/music-script)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/mmsaki/music-script)
![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/msakiart)

Add metadata to your yt-dlp downloaded songs from Youtube Playlist.

- [x] 💿 Artist (+ muliple artists)
- [x] 💿 Album Artist
- [x] 💿 Album name
- [x] 💿 Album art
- [x] 💿 Song Title
- [x] 💿 Comment
- [x] 💿 Copyright
- [x] 💿 Track #No
- [x] 💿 Genre
- [x] 💿 Composser
- [x] 💿 Description
- [x] 💿 Year
- [x] 💿 Lyrics

![](./resources/lyrics-example.png)

## How to Install

Install from pypi:

```sh
pip install musicscript
```

Run `musicscript` in terminal:

```sh
# run in terminal
musicscript

# 👾 Hello, Music Script
# Enter Artist Name:
# Enter Album Name:
# Enter Yotube Playlist / Soundcloud Album:
```

## Local Setup

> [!NOTE]
>
> ### Installing UV
>
> Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) python package manager written in rust
>
> ```sh
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
>
> After install uv you can clone this project with:
>
> ```sh
> git clone https://github.com/mmsaki/music-script.git
> ```

Run inside project

```sh
cd music-script;

uv sync;

uv run musicscript;

# Answer input prompts
#
# 👾 Hello, Music Script
# Enter Artist Name:
# Enter Album Name:
# Enter Youtube Playlist:
# Enter Image:
# Enter Year:
# Enter Copyright:
# Enter Genre:
```

## Dependencies

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - used to download songs from youtube / soundcloud / spotify
- [ffmpeg](https://ffmpeg.org/download.html) - using for adding metadata to music files

## Test

Enjoy offline music, you can still pay for streaming!
