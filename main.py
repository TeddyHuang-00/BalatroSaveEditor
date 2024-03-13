import argparse
import json
from pathlib import Path

from rich import print

from utils import compress, compress_raw, decompress, decompress_raw, encode, decode


def get_args():
    parser = argparse.ArgumentParser(description="Balatro save manager")
    subparsers = parser.add_subparsers(help="Subcommands", dest="command")
    view_subparser = subparsers.add_parser(
        "view", help="View a save file", aliases=["v"]
    )
    view_subparser.add_argument("file", type=str, help="The file to view")
    view_subparser.add_argument(
        "--format",
        "-f",
        type=str,
        help="The format to output (json or lua)",
        choices=["json", "lua"],
    )
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


def parse(file: Path) -> dict:
    """Try to parse the file and return the result."""
    if not file.suffix == ".jkr":
        raise ValueError(f"{file} is not a valid file")
    if file.parts[-1] == "version.jkr":
        raise ValueError("version.jkr is not a save file")
    return decompress(file)


def save(file: Path, data: dict) -> None:
    """Try to save the data to the file."""
    compress(data, file)


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


def export(file_name: Path, output: Path) -> None:
    """Export the save file to a Python file."""
    output_file = Path(output)
    if output_file.suffix == ".json":
        data = parse(file_name)
        output_file.write_text(json.dumps(data, indent=4).replace(r"\"", r"\\\""), encoding="UTF-8")
    elif output_file.suffix == ".lua":
        data = decompress_raw(file_name)
        output_file.write_text(data, encoding="UTF-8")
    else:
        raise ValueError(f"{output_file.parts[-1]} is not a valid file (should be .json or.lua)")


def import_(input: Path, output: Path) -> None:
    """Import the save file from a Python file."""
    data = input.read_text(encoding="UTF-8")
    if input.suffix == ".json":
        save(output, decode(json.loads(data)))
    elif input.suffix == ".lua":
        compress_raw(data, output)
    else:
        raise ValueError(f"{output.parts[-1]} is not a valid file (should be .json or.lua)")


def main():
    args = get_args()
    if args.command in {"view", "v"}:
        file = Path(args.file)
        if args.format == "json":
            data = parse(file)
            print(data)
        elif args.format == "lua":
            print(decompress_raw(file))
    elif args.command in {"merge", "m"}:
        left = parse(Path(args.left))
        right = parse(Path(args.right))
        result = merge(left, right, args.prefer)
        save(Path(args.output), result)
        print(f"Merged data saved to {args.output}")
    elif args.command in {"export", "e"}:
        export(Path(args.file), Path(args.output))
        print(f"Exported data saved to {args.output}")
    elif args.command in {"import", "i"}:
        import_(Path(args.file), Path(args.output))
        print(f"Imported data saved to {args.output}")


if __name__ == "__main__":
    main()
