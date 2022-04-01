#!/usr/bin/env python

"""Tests for `rpgmaker_mv_decoder` package."""


import unittest
from pathlib import PurePath

import pytest
from click.testing import CliRunner
from decode import main
from rpgmaker_mv_decoder.exceptions import NoValidFilesFound
from rpgmaker_mv_decoder.utils import guess_at_key


class TestDecode(unittest.TestCase):
    """Tests for `rpgmaker_mv_decoder` package."""

    def __init__(self, methodName: str = ...) -> None:
        self.key = "acbd18db4cc2f85cedef654fccc4a4d8"
        self.valid_src_dir_1: PurePath = PurePath(
            "tests/assets/decode_project/www/")
        self.valid_src_dir_2: PurePath = self.valid_src_dir_1.parent
        self.valid_src_dir_3: PurePath = self.valid_src_dir_2.parent
        self.dst_dir: PurePath = PurePath("tests/output/")
        self.invalid_src_dir: PurePath = PurePath(
            "tests/assets/invalid_project/")
        self.dst_dir = ""
        self.dst_checksums = {}
        self.src_checksums = {}
        super().__init__(methodName)

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_key_finding_invalid(self):
        """Test invalid source directory."""
        with pytest.raises(NoValidFilesFound):
            guess_at_key(self.invalid_src_dir)

    def test_key_finding_valid(self):
        """Test finding a key."""
        assert self.key == guess_at_key(self.valid_src_dir_1)

    def test_command_line_interface(self):
        """Test the CLI."""
        if self is None:
            return
        runner = CliRunner()
        result = runner.invoke(main)
        assert result.exit_code == 2
        assert 'Usage: main' in result.output
        help_result = runner.invoke(main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help         Show this message and exit.' in help_result.output
