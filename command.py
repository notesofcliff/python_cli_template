"""This script is meant to serve as an example and a
template for writing programs with a Command Line
Interface.

Features Include:
    * -vvv style logging verbosity arguments
    * Option to output logs to a file in addition to stderr
    * Sensible Return Codes
    * Intuitive code organization
    * Input file that defaults to stdin
    * Output file that defaults to stdout 

This code is released under the GPL v3.

Feel free to copy this file `command.py` for the scaffolding
of the script and the file `test_command.py` for the tests.
"""
import sys
import pathlib
import logging
import argparse

LOG_LEVELS = [
    'CRITICAL',
    'FATAL',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
]

RETURN_CODES = {
    "SUCCESS": 0,
    "UNHANDLED_EXCEPTION": 1,
}

def parse_args(argv):
    """This function is responsible for parsing the command line
    arguments as well as any required post-processing.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=argparse.FileType("r"),
        default="-",
        nargs="?",
        help="The input file. Defaults to stdin",
    )
    parser.add_argument(
        "destination",
        type=argparse.FileType("w"),
        default="-",
        nargs="?",
        help="The output file. Defaults to stdout.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="If specified, increases logging verbosity. "
             "Can be specified multiple times (ie. -vvv)",
    )
    parser.add_argument(
        "-l", "--log-file",
        type=pathlib.Path,
        help="If provided, it must be the path to a file. The "
             "given file will be used for logging. NOTE: This file"
             "will be overwritten."
    )
    args = parser.parse_args(argv)
    args.verbose = LOG_LEVELS[min(args.verbose, len(LOG_LEVELS)-1)]
    return args

def configure_logging(level, filename=None):
    """This function configures the Python logging system
    based on the level and filename provided.
    """
    handlers = [
        logging.StreamHandler(
            stream=sys.stderr,
        ),
    ]
    if filename is not None:
        handlers.append(
            logging.FileHandler(
                filename,
                mode="w",
            )
        )

    logging.basicConfig(
        level=level,
        handlers=handlers,
    )

def _main(args):
    """This function is responsible for executing the application logic.
    """
    log = logging.getLogger(__name__)
    for line in args.source:
        log.debug(f"Found line: {line}")
        bytes_written = args.destination.write(line)
        log.debug(f"Wrote {bytes_written} bytes to {args.destination}")
    log.info(f"Exiting successfully")
    return RETURN_CODES["SUCCESS"]


def main(argv):
    """This method is executed when this script is called
    from the command line.

    This function is responsible for the following:

    * parse command line arguments
    * Configure logging based on arguments
    * Call the function `_main` which should hold the application logic
    * return the return code as determined by function `_main`
    """
    log = logging.getLogger(__name__)
    try:
        args = parse_args(argv)
    except Exception as exception:
        log.critical(f"An unhandled exception has occurred: {exception}")
        return RETURN_CODES["UNHANDLED_EXCEPTION"]
    configure_logging(args.verbose, args.log_file)
    log = logging.getLogger(__name__)
    log.debug(f"Received args: {args}")
    try:
        return_value = _main(args)
    except Exception as exception:
        log.critical(f"An unhandled exception has occurred: {exception}")
        return_value = RETURN_CODES["UNHANDLED_EXCEPTION"]
    return return_value

if __name__ == "__main__":
    try:
        rc = main(sys.argv[1:])
    except:
        rc = RETURN_CODES["UNHANDLED_EXCEPTION"]
    finally:
        logging.shutdown()
    sys.exit(rc)
