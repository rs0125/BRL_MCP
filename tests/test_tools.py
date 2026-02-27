"""Tests for MCP tool functions."""

from unittest.mock import patch


@patch("brlcad_mcp.server.tools.primitives.send_command")
def test_create_sphere(mock_send):
    mock_send.return_value = "SUCCESS"

    from brlcad_mcp.server.tools.primitives import create_sphere

    result = create_sphere(name="ball.s", x=0, y=0, z=0, radius=10)

    assert "ball.s" in result
    assert "SUCCESS" in result
    # Should send: create command, draw, autoview
    assert mock_send.call_count == 3


@patch("brlcad_mcp.server.tools.boolean.send_command")
def test_boolean_combination_invalid_operator(mock_send):
    from brlcad_mcp.server.tools.boolean import boolean_combination

    result = boolean_combination(
        output_name="result.c",
        base_object="a.s",
        operator="x",
        target_object="b.s",
    )
    assert "Error" in result
    mock_send.assert_not_called()
