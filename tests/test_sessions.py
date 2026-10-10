import pytest
from telegram_manager.session_import import parse_session_text, validate_zip_members
import zipfile, io

def test_parse_json_session():
    assert parse_session_text('{"session_string":"' + "x"*100 + '"}') == "x"*100

def test_reject_short_text():
    with pytest.raises(ValueError):
        parse_session_text("short")

def test_zip_path_traversal_rejected():
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        z.writestr("../evil.txt", "x")
    bio.seek(0)
    with zipfile.ZipFile(bio) as z:
        with pytest.raises(ValueError):
            validate_zip_members(z, 1000)
