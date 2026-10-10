def test_callback_prefix_contract():
    # Callback routing uses explicit menu:<action> prefixes.
    assert "menu:accounts".split(":", 1) == ["menu", "accounts"]
    assert "confirm:delete:token".split(":", 2)[1] == "delete"
