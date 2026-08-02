"""Command line entry point for the USCIS case status checker."""

import argparse
import sys

from uscis_case_status import get_case_status


def main():
    """Parse the receipt number from argv and print its case status."""
    parser = argparse.ArgumentParser(
        prog="uscis-case-status",
        description="Check USCIS case status by receipt number",
    )
    parser.add_argument(
        "case_id",
        help="USCIS receipt number (e.g. SRC2690189834)",
    )
    args = parser.parse_args()

    try:
        result = get_case_status(args.case_id)
        print(f"Case:    {args.case_id}")
        print(f"Date:    {result['date']}")
        print(f"Status:  {result['status']}")
    # A CLI should report any failure — bad receipt number, missing Xvfb,
    # Selenium timeout — as a one-line message rather than a traceback.
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
