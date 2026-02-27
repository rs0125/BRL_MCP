"""Tests for the transport layer (socket bridge)."""

from unittest.mock import MagicMock, patch

from brlcad_mcp.transport.socket_bridge import send_command


@patch("brlcad_mcp.transport.socket_bridge.socket.socket")
def test_send_command_success(mock_socket_cls):
    """send_command should transmit the command and return the response."""
    mock_sock = MagicMock()
    mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
    mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_sock.recv.return_value = b"SUCCESS: done"

    result = send_command("in ball.s sph 0 0 0 10")

    mock_sock.sendall.assert_called_once_with(b"in ball.s sph 0 0 0 10\n")
    assert result == "SUCCESS: done"


@patch("brlcad_mcp.transport.socket_bridge.socket.socket")
def test_send_command_timeout(mock_socket_cls):
    """send_command should raise TimeoutError on socket timeout."""
    import socket as _socket

    mock_sock = MagicMock()
    mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
    mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_sock.connect.side_effect = _socket.timeout("timed out")

    try:
        send_command("ls")
        assert False, "Expected TimeoutError"
    except TimeoutError:
        pass
