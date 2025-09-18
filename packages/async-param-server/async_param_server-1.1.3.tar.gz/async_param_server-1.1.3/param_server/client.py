
"""Python client library for Parameter Server (async and sync)."""


import asyncio
import json
import logging
import socket
import threading
from typing import Any, List, Optional, Union

from .store import ALLOWED_TYPE_UNION, ALLOWED_TYPES


logger = logging.getLogger(__name__)


class ParameterClient:
    """Synchronous client for Parameter Server with persistent connection."""

    def __init__(self, host: str = "localhost", port: int = 8888, auto_reconnect: bool = True):
        """Initialize the sync parameter client.

        Args:
            host: Server hostname or IP address
            port: Server port
            auto_reconnect: Automatically reconnect on connection loss
        """
        self.host = host
        self.port = port
        self.auto_reconnect = auto_reconnect
        self.sock: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.RLock()

    def _ensure_connection(self) -> None:
        """Ensure we have a valid connection, reconnecting if necessary."""
        with self._lock:
            if self._connected and self.sock:
                # Test connection with a simple ping
                try:
                    ping_msg = {"command": "ping"}
                    message_data = json.dumps(ping_msg).encode("utf-8")
                    message_length = len(message_data).to_bytes(4, byteorder="big")

                    self.sock.sendall(message_length + message_data)
                    length_data = self._recv_exactly(4)
                    response_length = int.from_bytes(length_data, byteorder="big")
                    _ = self._recv_exactly(response_length)
                    return  # Connection is good
                except Exception:
                    self._connected = False
                    self._cleanup_connection()

        # Connect or reconnect if needed
        if not self._connected and self.auto_reconnect:
            self._unguarded_connect()
        elif not self._connected:
            raise ConnectionError("Not connected to server and auto-reconnect is disabled")

    def _cleanup_connection(self) -> None:
        """Clean up the current connection."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self._connected = False

    def _unguarded_connect(self) -> None:
        """Connect to the parameter server without acquiring the lock."""
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self._connected = True
            logger.info(f"Connected to parameter server at {self.host}:{self.port}")
        except Exception as e:
            self._cleanup_connection()
            raise ConnectionError(f"Failed to connect to server: {e}")

    def connect(self) -> None:
        """Connect to the parameter server."""
        with self._lock:
            if self._connected:
                return
            self._cleanup_connection()
            self._unguarded_connect()

    def disconnect(self) -> None:
        """Disconnect from the parameter server."""
        with self._lock:
            self._cleanup_connection()

    def is_connected(self) -> bool:
        """Check if client is connected to server."""
        return self._connected and self.sock is not None

    def get(self, path: str) -> Any:
        """Get parameter value."""
        self._ensure_connection()
        response = self._send_message({"command": "get", "path": path})
        if response["status"] == "success":
            return response["value"]
        else:
            if "not found" in response["message"]:
                raise KeyError(response["message"])
            else:
                raise RuntimeError(response["message"])

    def set(self, path: str, value: ALLOWED_TYPE_UNION) -> None:
        """Set parameter value."""
        if not isinstance(value, ALLOWED_TYPES):
            raise ValueError(f"Unsupported parameter type: {type(value)}")
        self._ensure_connection()
        response = self._send_message({"command": "set", "path": path, "value": value})
        if response["status"] != "success":
            raise RuntimeError(response["message"])

    def delete(self, path: str) -> None:
        """Delete parameter."""
        self._ensure_connection()
        response = self._send_message({"command": "delete", "path": path})
        if response["status"] != "success":
            if "not found" in response["message"]:
                raise KeyError(response["message"])
            else:
                raise RuntimeError(response["message"])

    def list_params(self, prefix: str = "") -> List[str]:
        """List all parameters with optional prefix filter."""
        self._ensure_connection()
        response = self._send_message({"command": "list", "prefix": prefix})
        if response["status"] == "success":
            return response["parameters"]
        else:
            raise RuntimeError(response["message"])

    def ping(self) -> bool:
        """Ping the server to check connectivity."""
        try:
            self._ensure_connection()
            response = self._send_message({"command": "ping"})
            return response["status"] == "success"
        except Exception:
            return False

    def _send_message(self, message: dict) -> dict:
        """Send message to server and receive response."""
        with self._lock:
            try:
                message_data = json.dumps(message).encode("utf-8")
                message_length = len(message_data).to_bytes(4, byteorder="big")
                self.sock.sendall(message_length + message_data)
                length_data = self._recv_exactly(4)
                response_length = int.from_bytes(length_data, byteorder="big")
                response_data = self._recv_exactly(response_length)
                response = json.loads(response_data.decode("utf-8"))
                return response
            except (OSError, json.JSONDecodeError) as e:
                self._connected = False
                raise ConnectionError(f"Communication error: {e}")

    def _recv_exactly(self, n: int) -> bytes:
        """Receive exactly n bytes from the socket."""
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Socket connection broken")
            data += chunk
        return data

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        

class AsyncParameterClient:
    """Asynchronous client for Parameter Server with persistent connection."""

    def __init__(self, host: str = "localhost", port: int = 8888, auto_reconnect: bool = True):
        """Initialize the async parameter client.

        Args:
            host: Server hostname or IP address
            port: Server port
            auto_reconnect: Automatically reconnect on connection loss
        """
        self.host = host
        self.port = port
        self.auto_reconnect = auto_reconnect
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._lock = asyncio.Lock()

    async def _ensure_connection(self) -> None:
        """Ensure we have a valid connection, reconnecting if necessary."""
        async with self._lock:
            if self._connected and self.writer:
                # Test connection with a simple ping
                try:
                    ping_msg = {"command": "ping"}
                    message_data = json.dumps(ping_msg).encode("utf-8")
                    message_length = len(message_data).to_bytes(4, byteorder="big")

                    self.writer.write(message_length)
                    self.writer.write(message_data)
                    await asyncio.wait_for(self.writer.drain(), timeout=1.0)

                    # Try to receive response
                    length_data = await asyncio.wait_for(self.reader.readexactly(4), timeout=1.0)
                    response_length = int.from_bytes(length_data, byteorder="big")
                    _ = await asyncio.wait_for(self.reader.readexactly(response_length), timeout=1.0)

                    return  # Connection is good

                except (asyncio.IncompleteReadError, asyncio.TimeoutError, ConnectionError):
                    # Connection is bad, mark as disconnected
                    self._connected = False
                    await self._cleanup_connection()

        # Connect or reconnect if needed
        if not self._connected and self.auto_reconnect:
            await self._unguarded_connect()
        elif not self._connected:
            raise ConnectionError("Not connected to server and auto-reconnect is disabled")

    async def _cleanup_connection(self) -> None:
        """Clean up the current connection."""

        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass

        self.reader = None
        self.writer = None
        self._connected = False

    async def _unguarded_connect(self) -> None:
        """Connect to the parameter server without acquiring the lock.

        ### USE WITH CAUTION!
        This must be used to avoid deadlocks when called from within
        other methods that already hold the lock.
        """
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self._connected = True

            logger.info(f"Connected to parameter server at {self.host}:{self.port}")
        except Exception as e:
            await self._cleanup_connection()
            raise ConnectionError(f"Failed to connect to server: {e}")

    async def connect(self) -> None:
        """Connect to the parameter server."""
        async with self._lock:
            if self._connected:
                return

            # Clean up any existing connection
            await self._cleanup_connection()

            await self._unguarded_connect()

    async def disconnect(self) -> None:
        """Disconnect from the parameter server."""
        async with self._lock:
            await self._cleanup_connection()

    def is_connected(self) -> bool:
        """Check if client is connected to server."""
        return self._connected and self.writer is not None

    async def get(self, path: str) -> Any:
        """Get parameter value."""
        await self._ensure_connection()
        response = await self._send_message({"command": "get", "path": path})

        if response["status"] == "success":
            return response["value"]
        else:
            if "not found" in response["message"]:
                raise KeyError(response["message"])
            else:
                raise RuntimeError(response["message"])

    async def set(self, path: str, value: ALLOWED_TYPE_UNION) -> None:
        """Set parameter value."""
        if not isinstance(value, ALLOWED_TYPES):
            raise ValueError(f"Unsupported parameter type: {type(value)}")

        await self._ensure_connection()
        response = await self._send_message({"command": "set", "path": path, "value": value})

        if response["status"] != "success":
            raise RuntimeError(response["message"])

    async def delete(self, path: str) -> None:
        """Delete parameter."""
        await self._ensure_connection()
        response = await self._send_message({"command": "delete", "path": path})

        if response["status"] != "success":
            if "not found" in response["message"]:
                raise KeyError(response["message"])
            else:
                raise RuntimeError(response["message"])

    async def list_params(self, prefix: str = "") -> List[str]:
        """List all parameters with optional prefix filter."""
        await self._ensure_connection()
        response = await self._send_message({"command": "list", "prefix": prefix})

        if response["status"] == "success":
            return response["parameters"]
        else:
            raise RuntimeError(response["message"])

    async def ping(self) -> bool:
        """Ping the server to check connectivity."""
        try:
            await self._ensure_connection()
            response = await self._send_message({"command": "ping"})
            return response["status"] == "success"
        except Exception:
            return False

    async def _send_message(self, message: dict) -> dict:
        """Send message to server and receive response."""
        async with self._lock:
            try:
                # Send message
                message_data = json.dumps(message).encode("utf-8")
                message_length = len(message_data).to_bytes(4, byteorder="big")

                self.writer.write(message_length)
                self.writer.write(message_data)
                await self.writer.drain()

                # Receive response
                length_data = await self.reader.readexactly(4)
                response_length = int.from_bytes(length_data, byteorder="big")

                response_data = await self.reader.readexactly(response_length)
                response = json.loads(response_data.decode("utf-8"))

                return response

            except (asyncio.IncompleteReadError, json.JSONDecodeError) as e:
                self._connected = False
                raise ConnectionError(f"Communication error: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
