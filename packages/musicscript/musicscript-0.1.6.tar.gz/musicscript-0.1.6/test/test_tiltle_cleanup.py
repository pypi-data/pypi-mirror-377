from musicscript.utils import remove_title_artifacts

artifacts_tests = [
    ("Artist - Song Title (Official Video)", "Artist - Song Title"),
    ("Artist - Song Title (Official Music Video)", "Artist - Song Title"),
    ("Artist - Song Title (Official Visualizer)", "Artist - Song Title"),
    ("Artist - Song Title (Audio)", "Artist - Song Title"),
    ("Artist - Song Title (Official Audio)", "Artist - Song Title"),
    ("Artist - Song Title [Official Audio]", "Artist - Song Title"),
    ("Artist - Song Title (Lyric Video)", "Artist - Song Title"),
    ("Artist - Song Title (Lyric Video)", "Artist - Song Title"),
    ("Artist - Song Title (Visualizer)", "Artist - Song Title"),
    ("Artist - Song Title (OFFICIAL VIDEO)", "Artist - Song Title"),
    ("Artist - Song Title (Music Video)", "Artist - Song Title"),
    ("Artist - Song Title (Exclusive Music VIDEO)", "Artist - Song Title"),
    ("Artist - Song Title - Visualizer", "Artist - Song Title"),
]


def test_remove_title_artifacts():
    for test in artifacts_tests:
        res = remove_title_artifacts(test[0])
        assert res == test[1]
