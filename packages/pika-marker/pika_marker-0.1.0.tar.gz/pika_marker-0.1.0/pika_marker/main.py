import argparse
import sys
from .pika_marker import appendPikaMarker


def main():
    parser = argparse.ArgumentParser(
        description="Append a PIKA marker to a marker file."
    )
    parser.add_argument("file", help="Path to the marker file")
    parser.add_argument("name", help="Name of the marker")
    parser.add_argument("-a", "--additional", default="", help="Additional text")
    parser.add_argument("-i", "--icon", default="", help="Icon or emoji")
    parser.add_argument("-t", "--timestamp", type=float, default=None,
                        help="Unix timestamp (defaults to current time)")

    args = parser.parse_args()

    appendPikaMarker(
        fp_or_path=args.file,
        name=args.name,
        additional=args.additional,
        icon=args.icon,
        timestamp=args.timestamp
    )


if __name__ == "__main__":
    main()
