import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from export_hf import _UNSCRUBBED, ROOT, scrub, secret_hits  # noqa: E402


def test_scrub_replaces_repo_home_and_temp_paths():
    text = (f"cd {ROOT}/runs/x; ls /Users/someone/Desktop; "
            "cat /var/folders/__/_abc123xyz/T/xcrun_db-1")
    out = scrub({"messages": [text]})["messages"][0]
    assert "<repo>/runs/x" in out
    assert "/Users/<user>/Desktop" in out
    assert "/var/folders/<tmp>/T/xcrun_db-1" in out
    assert "_abc123xyz" not in out and "someone" not in out


def test_secret_scan_flags_keys_and_emails():
    assert secret_hits("key sk-or-v1-abcdef123456") == ["openrouter key"]
    assert "email" in secret_hits("contact someone@example.com")
    assert secret_hits("Bearer abcdefghijklmnopqrstuvwxyz") == ["bearer token"]
    assert secret_hits("a clean game transcript: c3 d4 e2") == []


def test_no_false_alarms_on_code_or_bare_paths():
    assert secret_hits("return False\\n@functools.lru_cache(None)") == []
    assert "email" in secret_hits("mail me at first.last@example.org")
    assert not _UNSCRUBBED.search("ls -la /Users/\\n..")
    assert _UNSCRUBBED.search("cat /Users/alice/notes.txt")
    assert not _UNSCRUBBED.search("cat /Users/<user>/notes.txt and /var/folders/<tmp>/T/x")
