"""
Utility functions for IO of compressed files and parsing of the data.
"""

import zlib
import ast
from pathlib import Path

__all__ = ["decompress", "compress", "encode", "decode"]


def decompress_raw(file: Path) -> str:
    """Read and parse the compressed file and return the decompressed data as a string."""
    data = file.read_bytes()
    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)  # For raw deflate data
    decompressed_data = decompressor.decompress(data)
    return decompressed_data.decode("utf-8")


def compress_raw(data: str, file: Path) -> None:
    """Compress the data and write it to a file."""
    compressor = zlib.compressobj(1, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed_data = compressor.compress(data.encode("utf-8"))
    compressed_data += compressor.flush()
    file.write_bytes(compressed_data)


def parse_obj(data: str) -> dict:
    """Parse the decompressed data and return the content in an object."""
    obj_str = (
        data[7:]
        .replace("[", "")
        .replace("]", "")
        .replace("=", ":")
        .replace(":true", ":True")
        .replace(":false", ":False")
    )
    return ast.literal_eval(obj_str)


def convert_obj(obj: dict) -> str:
    """Convert the object to lua-like string"""
    result = ""
    for key, value in obj.items():
        if isinstance(value, dict):
            value = convert_obj(value)
        elif isinstance(value, str):
            value = f'"{value}"'
        elif isinstance(value, bool):
            value = str(value).lower()
        if isinstance(key, str):
            key = f'"{key}"'
        result += f"[{key}]={value},"
    return "{" + result + "}"


def decompress(file: Path) -> dict:
    """Read and parse the compressed file and return the decompressed data as an object."""
    return parse_obj(decompress_raw(file))


def compress(obj: dict, file: Path) -> None:
    """Compress the object and write it to a file."""
    compress_raw("return " + convert_obj(obj), file)


def encode(obj: dict) -> dict:
    """Encode the object to a type-safe dictionary"""

    result = {}
    for key, value in obj.items():
        if isinstance(key, int):
            key = "\t\f" + str(key)
        if isinstance(value, dict):
            value = encode(value)
        result[key] = value
    return result


def decode(obj: dict) -> dict:
    """Decode the object to a type-safe dictionary"""
    result = {}
    for key, value in obj.items():
        if key.startswith("\t\f"):
            key = int(key[2:])
        if isinstance(value, dict):
            value = decode(value)
        result[key] = value
    return result
