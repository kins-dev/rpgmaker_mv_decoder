#!/usr/bin/env python

"""Tests for `rpgmaker_mv_decoder` package."""


import unittest
from click.testing import CliRunner

from decode import main


class TestDecode(unittest.TestCase):
    """Tests for `rpgmaker_mv_decoder` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

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
