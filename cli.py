import argparse
import logging
import sys
from datetime import datetime

import sync
import validate


def parse_date(text):
    return datetime.strptime(text, "%Y-%m-%d").date()


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "full-load", "incremental"):
        sub.add_parser(name)
    v = sub.add_parser("validate")
    v.add_argument("--from", dest="start", type=parse_date)
    v.add_argument("--to", dest="end", type=parse_date)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        if args.command == "init":
            sync.run_init()
        elif args.command == "full-load":
            sync.run_sync(full=True)
        elif args.command == "incremental":
            sync.run_sync(full=False)
        else:
            errors = validate.run_validate(args.start, args.end)
            if errors:
                for e in errors:
                    print("ERROR:", e)
                print("validate FAILED")
                return 1
        print(f"{args.command} succeeded")
        return 0
    except Exception as e:
        print(f"{args.command} FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
