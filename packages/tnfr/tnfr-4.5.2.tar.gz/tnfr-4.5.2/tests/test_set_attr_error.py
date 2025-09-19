"""Pruebas de ``set_attr_generic`` para conversiones nulas."""

from tnfr.alias import set_attr_generic


def test_set_attr_allows_none_conversion():
    """``set_attr_generic`` debe permitir valores ``None``."""
    d = {}
    set_attr_generic(d, ("x",), 123, conv=lambda v: None)
    assert "x" in d and d["x"] is None
