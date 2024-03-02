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


def main():
    args = get_args()
    if args.command == "view":
        data = parse(args.file)
        print(data)


if __name__ == "__main__":
    main()
