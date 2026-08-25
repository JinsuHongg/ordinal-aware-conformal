from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ordinal_aware_conformal.checkpoint_reuse import load_manifest_metadata


class CheckpointReuseTests(unittest.TestCase):
    def test_manifest_metadata_hash_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.jsonl"
            manifest.write_text('{"sample_id":"one"}\n')
            from ordinal_aware_conformal.checkpoint_reuse import sha256_file

            (root / "manifest_metadata.json").write_text(
                json.dumps({"manifest_sha256": sha256_file(manifest)})
            )
            self.assertEqual(load_manifest_metadata(root)["manifest_sha256"], sha256_file(manifest))

    def test_manifest_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifest.jsonl").write_text('{"sample_id":"one"}\n')
            (root / "manifest_metadata.json").write_text(json.dumps({"manifest_sha256": "wrong"}))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_manifest_metadata(root)


if __name__ == "__main__":
    unittest.main()
