import sys
import os.path
import unittest
from tempfile import TemporaryDirectory
from io import StringIO
from unittest.mock import patch

from command import (
    main,
    parse_args,
    RETURN_CODES,
)

class TestArgumentParserDefaults(unittest.TestCase):
    """This TestCase tests the known defaults for command.parse_args.

    When changes are made to command.py that break these tests, the 
    change can be considered a breaking change. Update the test and
    document the breaking change in the release notes.
    """

    def test_default_destination_is_stdout(self):
        """Destination should default to stdout.
        """
        args = parse_args([])
        self.assertEqual(sys.stdout, args.destination)
    
    def test_default_source_is_stdin(self):
        """Source should default to stdin.
        """
        args = parse_args([])
        self.assertEqual(sys.stdin, args.source)

    def test_verbosity_default_is_stdin(self):
        """Source should default to stdin.
        """
        args = parse_args([])
        self.assertEqual(args.verbose, "CRITICAL")

class TestArgumentParser(unittest.TestCase):
    """This TestCase is meant to test that various arguments
    provided will be parsed as expected.
    """
    
    def test_verbosity_levels(self):
        """Each -v should increase the logging verbosity.

        Note CRITICAL is the default, which is tested in
        `TestArgumentParserDefaults`, so we will skip that one.
        """
        args = parse_args(["-v"])
        self.assertEqual(args.verbose, "FATAL")

        args = parse_args(["-vv"])
        self.assertEqual(args.verbose, "ERROR")

        args = parse_args(["-vvv"])
        self.assertEqual(args.verbose, "WARNING")

        args = parse_args(["-vvvv"])
        self.assertEqual(args.verbose, "INFO")

        args = parse_args(["-vvvvv"])
        self.assertEqual(args.verbose, "DEBUG")

        args = parse_args(["-vvvvvvvvvvv"])
        self.assertEqual(args.verbose, "DEBUG")

    def test_log_file(self):
        with TemporaryDirectory() as directory:
            logfile = os.path.join(directory, "out.log")

            # Patch stdin with a file-like object with 2 lines of text
            with patch("sys.stdin", StringIO("first line\nsecond line\n")):
                main(["-vvvvv", "--log-file", logfile])

            # Read in the log file
            with open(logfile, "r") as fin:
                log_content = fin.read()

            # Some assertions of expected log messages
            self.assertIn("first line", log_content)
            self.assertIn("second line", log_content)
            self.assertIn("Exiting successfully", log_content)
            self.assertIn("Found line: ", log_content)

class TestInputOutput(unittest.TestCase):

    def test_two_lines(self):
        with patch("sys.stdin", StringIO("first line\nsecond line\n")) as stdin, \
             patch("sys.stdout", new_callable=StringIO) as stdout:
            rc = main([])
            stdout.seek(0)
            results = stdout.read()
            self.assertEqual(results, "first line\nsecond line\n")


if __name__ == "__main__":
    unittest.main()
