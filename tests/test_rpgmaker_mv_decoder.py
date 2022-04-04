#!/usr/bin/env python

"""Tests for `rpgmaker_mv_decoder` package."""


import shutil
import unittest
from pathlib import Path, PurePath
from typing import List

from click.testing import CliRunner

from decode import main
from rpgmaker_mv_decoder.exceptions import NoValidFilesFound
from rpgmaker_mv_decoder.utils import decode_files, guess_at_key


class TestDecode(unittest.TestCase):
    """Tests for `rpgmaker_mv_decoder` package."""

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.key = "acbd18db4cc2f85cedef654fccc4a4d8"
        base_path: PurePath = PurePath("tests/assets/decode_project/www/")
        self.valid_src_dir: List[PurePath] = [
            base_path,
            base_path.parent,
            base_path.parent.parent,
        ]
        self.dst_dir: PurePath = PurePath("tests/output")
        self.invalid_src_dir: PurePath = PurePath("tests/assets/invalid_project/")
        self.dst_checksums = {}
        self.src_checksums = {}

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def check_source_files(self):
        """Check md5sums"""

    def test_key_finding_invalid(self):
        """Test invalid source directory."""
        with self.assertRaises(
            NoValidFilesFound,
            msg=f"Invalid directory '{self.invalid_src_dir}' should "
            "raise 'NoValidFilesFound' exception",
        ):
            guess_at_key(self.invalid_src_dir)

    def test_decode_files_no_filetype_detection(self):
        """Test finding a key."""
        cnt: int = 0
        for path in self.valid_src_dir:
            output_dir = self.dst_dir.joinpath(str(cnt))
            decode_files(path, output_dir, self.key, False)
            cnt += 1
        shutil.rmtree(Path(self.dst_dir).resolve())

    def test_key_finding_valid(self):
        """Test finding a key."""
        for path in self.valid_src_dir:
            self.assertEqual(self.key, guess_at_key(path), f"Decoded key doesn't match for '{path}")


class TestCLI(unittest.TestCase):
    """Tests for `rpgmaker_mv_decoder` package."""

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_command_line_interface(self):
        """Test the CLI."""
        if self is None:
            return
        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 2
        assert "Usage: main" in result.output
        help_result = runner.invoke(main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help         Show this message and exit." in help_result.output
