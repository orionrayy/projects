import tempfile
import unittest
from pathlib import Path

from motionlab.security import resolve_allowed_video_path


class LocalPathPolicyTests(unittest.TestCase):
    def test_allowed_file_is_resolved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = root / "clip.mp4"
            source.write_bytes(b"placeholder")
            self.assertEqual(resolve_allowed_video_path(str(source), [root]), source)

    def test_file_outside_allowed_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as root_temp, tempfile.TemporaryDirectory() as outside_temp:
            root = Path(root_temp).resolve()
            outside = Path(outside_temp) / "clip.mp4"
            outside.write_bytes(b"placeholder")
            with self.assertRaisesRegex(PermissionError, "outside_MOTION_ALLOWED_ROOTS"):
                resolve_allowed_video_path(str(outside), [root])

    def test_non_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as root_temp:
            root = Path(root_temp).resolve()
            with self.assertRaisesRegex(ValueError, "video_path_must_be_a_file"):
                resolve_allowed_video_path(str(root), [root])


if __name__ == "__main__":
    unittest.main()
