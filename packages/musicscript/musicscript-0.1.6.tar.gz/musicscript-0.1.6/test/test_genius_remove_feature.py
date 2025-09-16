from musicscript.lyrics import remove_feat

feature_tests = [
    ("Forgiveless (feat. Ol' Dirty Bastard)", "Forgiveless"),
    ("Forgiveless Feat. Ol' Dirty Bastard", "Forgiveless"),
    ("Forgiveless feat. Ol' Dirty Bastard (Interlude)", "Forgiveless (Interlude)"),
    ("Open Arms (Ft. Travis Scott)", "Open Arms"),
    ("30 For 30 (ft. Kendrick Lamar)", "30 For 30"),
    ("Used (Ft. Don Toliver) (Interlude)", "Used (Interlude)"),
    ("Used Ft. Don Toliver (Interlude)", "Used (Interlude)"),
    ("Used (Interlude) (ft. Don Toliver)", "Used (Interlude)"),
    ("Used (Interlude) Ft. Don Toliver", "Used (Interlude)"),
    ("Used Ft. Don Toliver [Interlude]", "Used [Interlude]"),
    ("Used [Ft. Don Toliver] [Interlude]", "Used [Interlude]"),
]


def test_remove_feat():
    for test in feature_tests:
        res = remove_feat(test[0])
        assert res.lower() == test[1].lower()
