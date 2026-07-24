import argparse
import sys

from uscis_case_status import get_case_status


def main():
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
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
