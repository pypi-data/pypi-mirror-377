from musicscript.lyrics import build_link

link_tests = [
    (
        ("Mozzy & Kalan.FrFr", "SPEEDIN!"),
        "https://genius.com/Mozzy-and-kalanfrfr-speedin-lyrics",
    ),
    (
        ("Mozzy & Kalan.FrFr", "SIZE ME UP (Ft. Skilla Baby)"),
        "https://genius.com/Mozzy-and-kalanfrfr-size-me-up-lyrics",
    ),
    (
        ("Mozzy & Kalan.FrFr", "BBL (Ft. Rob49)"),
        "https://genius.com/Mozzy-and-kalanfrfr-bbl-lyrics",
    ),
    (
        ("Mozzy & Kalan.FrFr", "BBL (Ft. Rob49)"),
        "https://genius.com/Mozzy-and-kalanfrfr-bbl-lyrics",
    ),
    (
        ("Future, Metro Boomin & Kendrick Lamar", "Like That"),
        "https://genius.com/Future-metro-boomin-and-kendrick-lamar-like-that-lyrics",
    ),
    (
        ("Future & Metro Boomin", "We Don't Trust You"),
        "https://genius.com/Future-and-metro-boomin-we-dont-trust-you-lyrics",
    ),
]


def test_build_link():
    for test in link_tests:
        res = build_link(*test[0])
        assert res.lower() == test[1].lower()
