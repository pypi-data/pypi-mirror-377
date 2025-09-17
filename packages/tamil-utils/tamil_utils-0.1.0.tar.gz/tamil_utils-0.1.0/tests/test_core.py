from tamil_utils import transliterate_iso15919, script_of, token_scripts

def test_transliterate_basic():
    assert transliterate_iso15919("தமிழ்")[:4] == "tami"  # loose check
    assert transliterate_iso15919("ஆதி") == "ādi"

def test_script_detection():
    ts = token_scripts(["தமிழ்", "hello", "AI", "கோட்123"])
    assert ts[0][1] == "Tamil"
    assert ts[1][1] == "Latin"
    assert any(s in {"Mixed","Other"} for _, s in ts if _=="கோட்123")
