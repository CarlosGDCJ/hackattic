#! /usr/bin/env python3
import requests
import dotenv
import os
import sys
import base64
import json
from struct import unpack

dotenv.load_dotenv()

problem_url = f'https://hackattic.com/challenges/help_me_unpack/problem?access_token={os.getenv("access_token")}'
res = requests.get(problem_url)

if res.status_code != 200:
    sys.exit("Couldn't get problem")

encoded_bytes = res.json()["bytes"]
decoded_bytes = base64.b64decode(encoded_bytes)
print(f"Decoded bytes: {decoded_bytes!r}")

hex_data = decoded_bytes.hex(" ", 1).split()
print(f"Decoded hex: {hex_data}")

mapping_dict = {
    "int": 4,
    "uint": 4,
    "short": 4,
    "float": 4,
    "double": 8,
    "big_endian_double": 8,
}
bytes_processed_so_far = 0

hex_dict = {}
for key, bytes_number in mapping_dict.items():
    processed_bytes = hex_data[
        bytes_processed_so_far : bytes_processed_so_far + bytes_number
    ]

    bytes_processed_so_far += bytes_number
    hex_dict[key] = processed_bytes

print(f"Hex dict: {hex_dict}")

# signed int
def twos_complement(value, bit_width):
    if value >= 2**bit_width:
        # This catches when someone tries to give a value that is out of range
        raise ValueError(
            "Value: {} out of range of {}-bit value.".format(value, bit_width)
        )
    else:
        return value - int((value << 1) & 2**bit_width)


signed_int = twos_complement(int("".join(hex_dict["int"][::-1]), 16), 32)
print(f"Signed int: {signed_int}")

# unsigned int
unsigned_int = int("".join(hex_dict["uint"][::-1]), 16)
print(f"Unsigned int: {unsigned_int}")

# short
short = twos_complement(int("".join(hex_dict["short"][1::-1]), 16), 16)
print(f"Short: {short}")

# float
float_hex = "".join(hex_dict["float"][::-1])
float_res = unpack(">f", bytes.fromhex(float_hex))[0]
print(f"Float: {float_res}")

# double
double_hex = "".join(hex_dict["double"][::-1])
double_res = unpack(">d", bytes.fromhex(double_hex))[0]
print(f"Double: {double_res}")

solution = {
    "int": signed_int,
    "uint": unsigned_int,
    "short": short,
    "float": float_res,
    "double": double_res,
    "big_endian_double": double_res,
}

submit_url = f"https://hackattic.com/challenges/help_me_unpack/solve?access_token={os.getenv('access_token')}"
submit_res = requests.post(
    submit_url,
    json=solution,
)

if submit_res.status_code != 200:
    sys.exit("Couldn't submit solution")

print(submit_res.json())
