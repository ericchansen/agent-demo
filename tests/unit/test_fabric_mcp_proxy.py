"""Offline regressions for the SDK-independent Fabric stdio/HTTP proxy."""

from __future__ import annotations

import io
import json
import subprocess
import urllib.error
from unittest.mock import Mock

from src.cli import fabric_mcp_proxy as proxy


def test_token_acquisition_preserves_scope_and_cache(monkeypatch):
    run = Mock(return_value=subprocess.CompletedProcess([], 0, stdout="test-access-token\n"))
    monkeypatch.setattr(proxy.subprocess, "run", run)
    monkeypatch.setattr(proxy, "_token_cache", {"token": None, "expires": 0.0})
    monkeypatch.setattr(proxy, "SUBSCRIPTION", "sample-subscription")
    monkeypatch.setattr(proxy, "TENANT", "sample-tenant")
    monkeypatch.setattr(proxy, "RESOURCE", "https://api.fabric.microsoft.com")

    assert proxy.get_token() == "test-access-token"
    assert proxy.get_token() == "test-access-token"
    run.assert_called_once_with(
        [
            proxy._AZ_CMD,
            "account",
            "get-access-token",
            "--resource",
            "https://api.fabric.microsoft.com",
            "--subscription",
            "sample-subscription",
            "--query",
            "accessToken",
            "-o",
            "tsv",
            "--tenant",
            "sample-tenant",
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def test_forwarding_preserves_bearer_auth_and_jsonrpc(monkeypatch):
    request = {"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}}
    result = {"jsonrpc": "2.0", "id": 7, "result": {"tools": []}}
    token = Mock(return_value="test-access-token")
    monkeypatch.setattr(proxy, "get_token", token)
    monkeypatch.setattr(proxy, "MCP_URL", "https://example.invalid/fabric-mcp")

    def open_request(outgoing, *, timeout):
        assert outgoing.full_url == "https://example.invalid/fabric-mcp"
        assert outgoing.method == "POST"
        assert outgoing.get_header("Authorization") == "Bearer test-access-token"
        assert outgoing.get_header("Content-type") == "application/json"
        assert json.loads(outgoing.data) == request
        assert timeout == 120
        return io.BytesIO(json.dumps(result).encode())

    monkeypatch.setattr(proxy.urllib.request, "urlopen", open_request)
    assert proxy.forward_request(request) == result
    token.assert_called_once_with()


def test_http_error_body_remains_a_protocol_error(monkeypatch):
    error = {"jsonrpc": "2.0", "id": 8, "error": {"code": -32602, "message": "Invalid params"}}
    monkeypatch.setattr(proxy, "get_token", Mock(return_value="test-access-token"))
    failure = urllib.error.HTTPError(
        "https://example.invalid/fabric-mcp", 400, "Bad Request", {}, io.BytesIO(json.dumps(error).encode())
    )
    monkeypatch.setattr(proxy.urllib.request, "urlopen", Mock(side_effect=failure))
    assert proxy.forward_request({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {}}) == error


def test_notification_does_not_receive_a_response(monkeypatch):
    request = {"jsonrpc": "2.0", "id": 9, "method": "ping"}
    notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    result = {"jsonrpc": "2.0", "id": 9, "result": {}}
    forward = Mock(return_value=result)
    stdout = io.StringIO()
    monkeypatch.setattr(proxy, "forward_request", forward)
    monkeypatch.setattr(proxy.sys, "stdin", io.StringIO(json.dumps(notification) + "\n" + json.dumps(request) + "\n"))
    monkeypatch.setattr(proxy.sys, "stdout", stdout)
    proxy.main()
    forward.assert_called_once_with(request)
    assert [json.loads(line) for line in stdout.getvalue().splitlines()] == [result]
