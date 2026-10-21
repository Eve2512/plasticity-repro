from harness.keys import load_key


def test_environment_wins_over_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OPENROUTER_API_KEY=from-file\n")
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-env")
    assert load_key("OPENROUTER_API_KEY", env) == "from-env"


def test_reads_quoted_value_from_file(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("# keys\nOTHER=x\nOPENROUTER_API_KEY='sk-or-abc'\n")
    assert load_key("OPENROUTER_API_KEY", env) == "sk-or-abc"


def test_missing_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert load_key("OPENROUTER_API_KEY", tmp_path / "none") is None
