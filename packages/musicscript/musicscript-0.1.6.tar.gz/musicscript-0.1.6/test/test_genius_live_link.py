import requests
from musicscript.lyrics import build_link

link_tests = [
    (
        ("Mozzy & Kalan.FrFr", "SPEEDIN!"),
        "https://genius.com/Mozzy-and-kalanfrfr-speedin-lyrics",
    ),
    (
        ("Mozzy & Kalan.FrFr", "BBL (Ft. Rob49)"),
        "https://genius.com/Mozzy-and-kalanfrfr-bbl-lyrics",
    ),
    (
        ("Future, Metro Boomin & Kendrick Lamar", "Like That"),
        "https://genius.com/Future-metro-boomin-and-kendrick-lamar-like-that-lyrics",
    ),
]


def test_build_link():
    for test in link_tests:
        res = build_link(*test[0])
        try:
            response = requests.get(res)
        except:
            Exception("Request failed")

        assert response.status_code == 200
