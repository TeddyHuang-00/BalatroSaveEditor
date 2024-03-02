import argparse

from rich import print

from utils import compress, decompress


def get_args():
    parser = argparse.ArgumentParser(description="Balatro save manager")
    subparsers = parser.add_subparsers(help="Subcommands", dest="command")
    view_subparser = subparsers.add_parser(
        "view", help="View a save file", aliases=["v"]
    )
    view_subparser.add_argument("file", type=str, help="The file to view")
    merge_subparser = subparsers.add_parser(
        "merge", help="Merge two save files", aliases=["m"]
    )
    merge_subparser.add_argument("left", type=str, help="The first file to merge")
    merge_subparser.add_argument("right", type=str, help="The second file to merge")
    merge_subparser.add_argument(
        "--output",
        "-o",
        type=str,
        help="The file to save the merged data to",
        default="merged.jkr",
    )
    merge_subparser.add_argument(
        "--prefer",
        "-p",
        type=str,
        help="The file to prefer when merging. Left or right means not to overwrite the data with the other file. Latest means to prefer the data from the file with the most progress.",
        choices=["left", "right", "latest"],
        default="latest",
    )

    return parser.parse_args()


def parse(file_name: str) -> dict:
    """Try to parse the file and return the result."""
    if not file_name.endswith(".jkr"):
        raise ValueError(f"{file_name} is not a valid file")
    if file_name == "version.jkr":
        raise ValueError("version.jkr is not a save file")
    return decompress(file_name)


def save(file_name: str, data: dict) -> None:
    """Try to save the data to the file."""
    compress(data, file_name)


def merge(left: dict, right: dict, prefer: str) -> dict:
    """Merge the two dictionaries and return the result."""
    result = {}
    all_keys = set(left.keys()) | set(right.keys())
    for key in all_keys:
        if key not in left:
            result[key] = right[key]
        elif key not in right:
            result[key] = left[key]
        else:
            lv, rv = left[key], right[key]
            if isinstance(lv, dict) and isinstance(rv, dict):
                result[key] = merge(lv, rv, prefer)
            else:
                if prefer == "left":
                    result[key] = left[key]
                elif prefer == "right":
                    result[key] = right[key]
                elif prefer == "latest":
                    if left[key] > right[key]:
                        result[key] = left[key]
                    else:
                        result[key] = right[key]
    return result


def main():
    args = get_args()
    if args.command in {"view", "v"}:
        data = parse(args.file)
        print(data)
    elif args.command in {"merge", "m"}:
        left = parse(args.left)
        right = parse(args.right)
        result = merge(left, right, args.prefer)
        save(args.output, result)
        print(f"Merged data saved to {args.output}")


if __name__ == "__main__":
    main()
