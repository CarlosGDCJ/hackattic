#! /usr/bin/env python3
import requests
import dotenv
import os
import base64
import sys
import magic
import gzip
import shutil
import psycopg2
import subprocess

dotenv.load_dotenv()
problem_url = f'https://hackattic.com/challenges/backup_restore/problem?access_token={os.getenv("access_token")}'

res = requests.get(problem_url)
if res.status_code != 200:
    sys.exit("Couldn't get problem")

decoded_bytes = base64.b64decode(res.json()["dump"])

with open("what_is_this", "wb") as f:
    f.write(decoded_bytes)

print(magic.from_file("what_is_this"))  # we find out that we received a gzipped file

with gzip.open("what_is_this", "rb") as f_in:
    with open("what_is_this_v2", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print(
    magic.from_file("what_is_this_v2")
)  # we find out that we received some ascii text (sql code)

# creating database
db_name = "hackattic"
db_user = "ha"
user_passwd = "passwd"
subprocess.run(
    [
        "psql",
        "-c",
        f"CREATE DATABASE {db_name}",
    ]
)
subprocess.run(
    [
        "psql",
        "-c",
        f"CREATE USER {db_user} WITH PASSWORD '{user_passwd}'",
    ]
)
subprocess.run(
    [
        "psql",
        "-c",
        f"GRANT CONNECT ON DATABASE {db_name} TO {db_user}",
    ]
)
subprocess.run(
    [
        "psql",
        "-d",
        f"{db_name}",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-c",
        "DROP TABLE IF EXISTS criminal_records",
        f"{db_user}",
    ]
)
subprocess.run(
    [
        "psql",
        "-d",
        f"{db_name}",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-f",
        "what_is_this_v2",
        f"{db_user}",
    ]
)


conn = psycopg2.connect(
    dbname=db_name, user=db_user, password=user_passwd, host="localhost", port=5432
)
cur = conn.cursor()
cur.execute("SELECT ssn FROM criminal_records WHERE status = 'alive'")
results = cur.fetchall()
cur.close()

print(*results, sep="\n")

solution = {"alive_ssns": [ssn[0] for ssn in results]}

submit_url = f'https://hackattic.com/challenges/backup_restore/solve?access_token={os.getenv("access_token")}'
res = requests.post(submit_url, json=solution)

print(solution)
if res.status_code != 200:
    sys.exit("Could not send solution")

print(res.json())
