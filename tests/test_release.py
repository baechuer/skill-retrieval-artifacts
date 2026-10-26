import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify import verify


class ReleaseTests(unittest.TestCase):
    def fixture(self, root):
        digest = hashlib.sha256(b"retained vector bytes").hexdigest()
        relative = "embeddings/test/vectors-000.npz"
        path = root / relative
        path.parent.mkdir(parents=True)
        path.write_text("version https://git-lfs.github.com/spec/v1\n"
                        f"oid sha256:{digest}\nsize 21\n")
        (root / "release_manifest.json").write_text(json.dumps({"files": {
            relative: {"sha256": digest, "bytes": 21, "lfs": True}
        }}))
        return path

    def test_pointer_is_not_downloaded_embedding(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            result = verify(root)
            self.assertEqual(result["status"], "PASS")
            self.assertFalse(result["vector_bytes_verified"])
            self.assertEqual(verify(root, require_embeddings=True)["status"], "FAIL")

    def test_modified_pointer_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = self.fixture(root)
            path.write_text(path.read_text().replace("size 21", "size 22"))
            self.assertEqual(verify(root)["status"], "FAIL")

    def test_real_env_filename_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            (root / ".env").write_text("not a credential\n")
            self.assertEqual(verify(root)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
