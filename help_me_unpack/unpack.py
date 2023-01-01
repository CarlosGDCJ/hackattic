#! /usr/bin/env python3
import requests
import dotenv
import os
import sys
import base64
from struct import unpack

dotenv.load_dotenv()

problem_url = f'https://hackattic.com/challenges/help_me_unpack/problem?access_token={os.getenv("access_token")}'
res = requests.get(problem_url)

if res.status_code != 200:
    sys.exit("Couldn't get problem")

encoded_bytes = res.json()["bytes"]
decoded_bytes = base64.b64decode(encoded_bytes)
print(f"Decoded bytes: {decoded_bytes!r}")

int_val, uint_val, short_val, float_val, double_val = unpack(
    "<iIhxxfd", decoded_bytes[:-8]
)

big_endian_double_val = unpack(">d", decoded_bytes[-8:])

solution = {
    "int": int_val,
    "uint": uint_val,
    "short": short_val,
    "float": float_val,
    "double": double_val,
    "big_endian_double": big_endian_double_val,
}

submit_url = f"https://hackattic.com/challenges/help_me_unpack/solve?access_token={os.getenv('access_token')}"
submit_res = requests.post(
    submit_url,
    json=solution,
)

if submit_res.status_code != 200:
    sys.exit("Couldn't submit solution")

print(submit_res.json())
