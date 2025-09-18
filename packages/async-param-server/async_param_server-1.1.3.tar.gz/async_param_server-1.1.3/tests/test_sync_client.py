"""Tests for sync parameter client functionality (mirrors async client tests)."""

import pytest
from param_server.client import ParameterClient

class TestParameterClient:
    """Test cases for ParameterClient (sync)."""

    def test_sync_connection(self, sync_test_server):
        """Test sync client connection and disconnection."""
        server = sync_test_server
        client = ParameterClient(host="localhost", port=server.port)

        assert not client.is_connected()

        client.connect()
        assert client.is_connected()

        client.disconnect()
        assert not client.is_connected()

    def test_sync_context_manager(self, sync_test_server):
        """Test sync client as context manager."""
        server = sync_test_server
        with ParameterClient(host="localhost", port=server.port) as client:
            assert client.is_connected()
            assert client.ping()
        assert not client.is_connected()

    def test_sync_basic_operations(self, sync_test_server):
        """Test basic sync get/set operations."""
        server = sync_test_server
        with ParameterClient(host="localhost", port=server.port) as client:
            # Set parameters
            client.set("/test/string", "hello")
            client.set("/test/int", 42)
            client.set("/test/float", 3.14)
            client.set("/test/bool", True)
            # Get parameters
            assert client.get("/test/string") == "hello"
            assert client.get("/test/int") == 42
            assert client.get("/test/float") == 3.14
            assert client.get("/test/bool") is True

    def test_parameter_listing(self, sync_test_server):
        """Test sync parameter listing functionality."""
        server = sync_test_server
        with ParameterClient(host="localhost", port=server.port) as client:
            # Set up test parameters
            client.set("/camera/exposure", 0.033)
            client.set("/camera/gain", 1.5)
            client.set("/robot/joint1", 0.0)
            client.set("/system/debug", True)
            # Test listing all parameters
            all_params = client.list_params()
            assert len(all_params) >= 4
            # Test listing with prefix
            camera_params = client.list_params("/camera")
            assert len(camera_params) == 2

    def test_error_handling(self, sync_test_server):
        """Test sync error handling for various scenarios."""
        server = sync_test_server
        with ParameterClient(host="localhost", port=server.port) as client:
            # Test getting non-existent parameter
            with pytest.raises(KeyError):
                client.get("/nonexistent/param")
            # Test deleting non-existent parameter
            with pytest.raises(KeyError):
                client.delete("/nonexistent/param")
            # Test setting invalid type
            with pytest.raises(ValueError):
                client.set("/test/invalid", {})  # dict is not a supported type

    def test_ping(self, sync_test_server):
        """Test sync ping functionality."""
        server = sync_test_server
        with ParameterClient(host="localhost", port=server.port) as client:
            assert client.ping() is True

    def test_multiple_clients(self, sync_test_server):
        """Test multiple sync clients accessing server simultaneously."""
        server = sync_test_server
        def client_worker(client_id, result_list, idx):
            with ParameterClient(host="localhost", port=server.port) as client:
                # Each client sets and gets its own parameters
                for i in range(10):
                    param_name = f"/sync_client_{client_id}/param_{i}"
                    client.set(param_name, i * client_id)
                # Verify all parameters were set correctly
                for i in range(10):
                    param_name = f"/sync_client_{client_id}/param_{i}"
                    value = client.get(param_name)
                    assert value == i * client_id
            result_list[idx] = "success"
        # Start multiple sync clients in threads
        import threading
        results = [None, None, None]
        threads = []
        for idx in range(3):
            t = threading.Thread(target=client_worker, args=(idx+1, results, idx))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        assert all(result == "success" for result in results)
