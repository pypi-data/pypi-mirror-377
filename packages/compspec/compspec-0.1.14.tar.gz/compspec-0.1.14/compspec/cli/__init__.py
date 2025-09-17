#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MIT"

import argparse
import os
import sys

import compspec
import compspec.plugin.parser as parsers
from compspec.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="Compspec",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description="actions",
        dest="command",
    )
    # print version and exit
    subparsers.add_parser("version", description="show software version")

    # List installed modules
    extract = subparsers.add_parser(
        "extract",
        formatter_class=argparse.RawTextHelpFormatter,
        description="extraction and creation plugins for compspec",
    )
    extract.add_argument("--outfile", help="output json file to write artifact")
    extract.add_argument(
        "--name", help="name for experiment", default="compat-experiment"
    )
    extractors = extract.add_subparsers(
        title="extract",
        description="Use compspec to extract specific application or environment metadata",
        dest="extract",
    )

    # Add plugin parsers
    parsers.add_plugin_parsers(extractors)
    return parser


def run_compspec():
    """
    run_compspec is the entrypoint for compspec!
    """
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """

        version = compspec.__version__

        print("\nCompspec v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(compspec.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # Here we can assume instantiated to get args
    if args.command == "extract":
        from .extract import main

    if args.command == "create":
        from .create import main

    main(args, extra)


if __name__ == "__main__":
    run_compspec()
