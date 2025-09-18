"""Requirements generation."""
import argparse
import logging
import sys

from . import VERSION
from .requirements import NoAppropriateVersionFoundError
from .requirements import Requirements


_logger = logging.getLogger(__name__)


def add_standard_arguments(parser: argparse.ArgumentParser):
    """Add normally expected command-line arguments to the given ``parser``."""
    # The "version" option
    parser.add_argument("--version", action="version", version=VERSION)

    # Logging options
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        dest="loglevel",
        help="Log copious debugging messages suitable for developers",
    )
    group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="loglevel",
        help="Don't log anything except warnings and critically-important messages",
    )


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description="Create a requirement report")
    add_standard_arguments(parser)
    parser.add_argument(
        "--organization", dest="organization", help="github organization owning the repo (e.g. NASA-PDS)"
    )
    parser.add_argument("--repository", dest="repository", help="github repository name")
    parser.add_argument(
        "--dev",
        dest="dev",
        nargs="?",
        const=True,
        default=False,
        help="Generate requirements with impacts related to latest dev/snapshot version",
    )
    parser.add_argument("--output", dest="output", help="directory where version/REQUIREMENTS.md file is created")
    parser.add_argument("--format", dest="format", default="md", help="markdown (md) or html")
    parser.add_argument("--token", dest="token", help="github personal access token")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format="%(levelname)s %(message)s")

    try:
        requirements = Requirements(args.organization, args.repository, token=args.token, dev=args.dev)
        requirement_file = requirements.write_requirements(root_dir=args.output, format=args.format)
        print(requirement_file)
    except NoAppropriateVersionFoundError as e:
        print("")  # Write just a newline to stdout I guess
        _logger.error(e)
        sys.exit(0)  # we don't want the github action to fail after that


if __name__ == "__main__":
    main()
