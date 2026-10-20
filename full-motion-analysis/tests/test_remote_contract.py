import asyncio
import os
import unittest
from unittest.mock import patch

from remote_mcp_server import (
    BearerTokenMiddleware,
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_BYTES,
    MAX_VIDEO_DURATION_SECONDS,
    TICKET_TTL_SECONDS,
    UPLOAD_TTL_SECONDS,
    safe_extension,
)


class RemoteMCPContractTests(unittest.TestCase):
    def test_upload_limits_are_bounded(self):
        self.assertLessEqual(MAX_UPLOAD_BYTES, 25 * 1024 * 1024)
        self.assertLessEqual(MAX_VIDEO_DURATION_SECONDS, 120)
        self.assertLessEqual(TICKET_TTL_SECONDS, 900)
        self.assertLessEqual(UPLOAD_TTL_SECONDS, 3600)

    def test_video_extension_allowlist_and_path_stripping(self):
        for name in ("clip.mp4", "scene.MKV", r"..\\outside\\clip.webm"):
            self.assertIn(safe_extension(name), ALLOWED_EXTENSIONS)
        for name in ("report.pdf", "archive.zip", "unknown"):
            self.assertIsNone(safe_extension(name))

    def test_extension_result_is_not_a_user_path(self):
        result = safe_extension("../../tmp/pwned.mp4")
        self.assertEqual(result, ".mp4")
        self.assertFalse("/" in result or "\\" in result)


class _PassThroughASGI:
    async def __call__(self, scope, receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})


class RemoteBearerAuthTests(unittest.IsolatedAsyncioTestCase):
    async def _status(self, path, *, method="POST", token=None, configured="T" * 48):
        headers = []
        if token is not None:
            headers.append((b"authorization", f"Bearer {token}".encode("ascii")))
        scope = {
            "type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1", "method": method, "scheme": "https",
            "path": path, "raw_path": path.encode(), "query_string": b"",
            "root_path": "", "headers": headers, "client": ("127.0.0.1", 12345),
            "server": ("example.test", 443),
        }
        messages = []
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        async def send(message):
            messages.append(message)
        environ = {} if configured is None else {"MOTION_API_TOKEN": configured}
        with patch.dict(os.environ, environ, clear=True):
            await BearerTokenMiddleware(_PassThroughASGI())(scope, receive, send)
        return messages[0]["status"]

    async def test_mcp_rejects_missing_or_wrong_bearer(self):
        self.assertEqual(await self._status("/mcp", token=None), 401)
        self.assertEqual(await self._status("/mcp", token="wrong"), 401)

    async def test_mcp_accepts_exact_bearer_token(self):
        token = "K" * 48
        self.assertEqual(await self._status("/mcp", token=token, configured=token), 204)

    async def test_server_fails_closed_when_token_is_not_configured(self):
        self.assertEqual(await self._status("/mcp", token=None, configured=None), 503)

    async def test_health_remains_minimally_public(self):
        self.assertEqual(await self._status("/health", method="GET", token=None, configured=None), 204)


if __name__ == "__main__":
    unittest.main()
