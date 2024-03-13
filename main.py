import argparse
import json
from typing import Any

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
    export_subparser = subparsers.add_parser(
        "export", help="Export a save file to JSON", aliases=["e"]
    )
    export_subparser.add_argument("file", type=str, help="The .jkr file to export")
    export_subparser.add_argument(
        "--output",
        "-o",
        type=str,
        help="The file to save the exported data to",
        default="exported.json",
    )
    import_subparser = subparsers.add_parser(
        "import", help="Import a save file from JSON", aliases=["i"]
    )
    import_subparser.add_argument("file", type=str, help="The .json file to import")
    import_subparser.add_argument(
        "--output",
        "-o",
        type=str,
        help="The file to save the imported data to",
        default="imported.jkr",
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


def export(file_name: str, output: str) -> None:
    """Export the save file to a Python file."""
    data = parse(file_name)
    with open(output, "w", encoding="UTF-8") as f:
        f.write(json.dumps(data, indent=4))


def import_(file_name: str, output: str) -> None:
    """Import the save file from a Python file."""
    with open(file_name, "r", encoding="UTF-8") as f:
        data = f.read()
    data = json.loads(data)

    def parse_int_keys(obj: dict[str, Any]) -> dict:
        """Parse the integer keys in the object."""
        result = {}
        for key, value in obj.items():
            if key.isdigit():
                key = int(key)
            if isinstance(value, dict):
                value = parse_int_keys(value)
            result[key] = value
        return result

    # Fix the integer keys that were converted to strings by json
    data = parse_int_keys(data)

    save(output, data)


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
    elif args.command in {"export", "e"}:
        export(args.file, args.output)
        print(f"Exported data saved to {args.output}")
    elif args.command in {"import", "i"}:
        import_(args.file, args.output)
        print(f"Imported data saved to {args.output}")


if __name__ == "__main__":
    main()
