"""Tests for brlcad_mcp.config."""

from brlcad_mcp.config import BRLCADConfig, LLMConfig, Settings


def test_default_brlcad_config():
    cfg = BRLCADConfig()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 5555
    assert cfg.timeout == 2.0
    assert cfg.buffer_size == 4096


def test_default_llm_config():
    cfg = LLMConfig()
    assert cfg.model == "gpt-4o"
    assert cfg.temperature == 0.0


def test_settings_composition():
    s = Settings()
    assert isinstance(s.brlcad, BRLCADConfig)
    assert isinstance(s.llm, LLMConfig)
