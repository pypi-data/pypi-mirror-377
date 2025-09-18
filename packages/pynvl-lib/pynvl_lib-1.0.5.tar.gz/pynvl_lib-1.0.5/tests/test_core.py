from pynvl.core import decode, nvl, sign, noneif, nvl2, coalesce


def test_nvl():
    assert nvl(expr=None, default=5) == 5
    assert nvl(expr=10, default=5) == 10
    assert nvl(nvl(nvl(None, None), None), "No contacts") == "No contacts"


def test_decode_basic_pairs():
    assert decode("A", "A", "Alpha", "B", "Beta") == "Alpha"
    assert decode("B", "A", "Alpha", "B", "Beta") == "Beta"


def test_decode_implicit_default():
    assert decode("Z", "A", "Alpha", "B", "Beta", "Unknown") == "Unknown"


def test_decode_explicit_default_overrides_implicit():
    assert decode("Z", "A", "Alpha", "B", "Beta", "X", default="Y") == "Y"


def test_decode_no_pairs_returns_none_or_explicit_default():
    assert decode("A") is None
    assert decode("A", default="D") == "D"


def test_decode_none_equals_none():
    assert decode(None, None, "N/A", "Should not see") == "N/A"
    assert decode(None, "X", "other", default="nope") == "nope"


def test_sign():
    assert sign(n=-5) == -1
    assert sign(n=0) == 0
    assert sign(n=9) == 1


def test_noneif_basic():
    assert noneif(5, 5) is None
    assert noneif(7, 8) == 7
    assert noneif("A", "B") == "A"
    assert noneif("A", "A") is None


def test_noneif_with_none_and_types():
    assert noneif(None, None) is None
    assert noneif(None, 0) is None


def test_nvl2():
    assert nvl2("x", "not-null", "is-null") == "not-null"
    assert nvl2(None, "not-null", "is-null") == "is-null"
    assert nvl2(0, "not-null", "is-null") == "not-null"  # 0 is not None


def test_coalesce():
    assert coalesce(None, None, 5, 10) == 5
    assert coalesce(None, "hello", "world") == "hello"
    assert coalesce(None, None, None) is None
    assert coalesce("first", "second") == "first"
    assert coalesce(None) is None
