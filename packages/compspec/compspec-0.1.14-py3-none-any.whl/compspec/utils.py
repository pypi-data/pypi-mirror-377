__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MIT"

import json
import os
import re
import shlex
import subprocess

import yaml


def read_json(filename):
    with open(filename, "r") as fd:
        data = json.loads(fd.read())
    return data


def read_file(filename):
    with open(filename, "r") as fd:
        data = fd.read()
    return data


def write_json(data, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(data, indent=4))


def normalize_key(key):
    """
    A key needs to be all lowercase, ideally with no spaces, etc.
    """
    return key.lower().replace(" ", "_")


def read_yaml(filepath):
    with open(filepath, "r") as fd:
        data = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    return data


def row(cols):
    return "|" + "|".join(cols) + "|\n"


def recursive_find(base, pattern="*.py"):
    """recursive find will yield python files in all directory levels
    below a base path.

    Arguments:
      - base (str) : the base directory to search
      - pattern: a pattern to match, defaults to *.py
    """
    for root, _, filenames in os.walk(base):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if not re.search(pattern, filepath):
                continue
            yield filepath


def run_command(cmd, stream=False):
    """
    use subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send
    """
    if not isinstance(cmd, list):
        cmd = shlex.split(cmd)

    stdout = subprocess.PIPE if not stream else None
    output = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=stdout)

    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")

    return output
