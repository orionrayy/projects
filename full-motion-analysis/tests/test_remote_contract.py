import unittest

from remote_mcp_server import (
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


if __name__ == "__main__":
    unittest.main()
