#!/usr/bin/env python3
import click
import os
import glob
import subprocess
import time
from hashlib import sha1
import json
import re

commands = {
    ".c": "gcc {filepath} -o {runame} -O2 -Wall -lm -static -std=gnu11 -Wfatal-errors",
    ".cpp": "g++ {filepath} -o {runame} -O2 -Wall -lm -static -std=gnu++2a -Wfatal-errors",
    ".java": "echo '#!/bin/sh' > {runame} && "
        "echo 'exec java {filepath} \"$@\"' >> {runame} && "
        "chmod u+x {runame}",
    ".py": 'echo "#!/usr/bin/env python3" > {runame};'
        "cat {filepath} >> {runame};chmod u+x {runame};"
        "python3 -c \"import py_compile; py_compile.compile('{runame}')\"",
    ".cs": 'dotnet new console --force -o .tmp/cs && '
        "cp {filepath} .tmp/cs/Program.cs && "
        "dotnet publish .tmp/cs --configuration Release --self-contained true --runtime linux-x64 /p:PublishSingleFile=true --framework net8.0 &&"
        "mv .tmp/cs/bin/Release/net8.0/linux-x64/publish/cs {runame}",
    ".rs": "rustc --edition 2018 -O -o {runame} {filepath}"
}


def preprocess(filepath, testcase_directory, no_subdirectory):
    if re.match("^$|\.", filepath):
        try:
            with open(".tmp/recent", "r") as f:
                filepath = json.load(f)["filepath"]
        except FileNotFoundError:
            click.echo("There is no recent run. Please specify filepath")

    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    name = re.sub("[-_].*", "", name)

    if not no_subdirectory:
        testcase_directory = os.path.join(testcase_directory, name)
    return filepath, testcase_directory, name


def compile(filepath):
    # Prepare
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)

    if not os.path.exists(".tmp"):
        os.mkdir(".tmp")
    if ext not in commands:
        raise click.ClickException(f"Cannot find compile command ({ext})")

    # TODO
    # To reduce compile, formatting source code before hashing would be good idea.

    # Hash
    with open(filepath, "rb") as f:
        data = f.read()
        h = sha1(data).hexdigest()
    runame = os.path.join(".tmp", name + "_" + h[:6])

    if os.path.exists(runame):
        click.echo(f"Skipping Compile (use {runame})")
        return runame

    # Compile
    command = commands[ext].format(filepath=filepath, runame=runame)
    click.echo(command)
    return_code = os.system(command)
    if return_code != 0:
        raise click.ClickException("Compile Failed.")
    return runame


@click.command()
@click.argument("filepath", type=click.Path(), default="")
@click.option(
    "--testcase-directory",
    "-tc",
    default="testcase",
    type=click.Path(),
    help="testcase directory",
)
@click.option(
    "--no-subdirectory",
    "-N",
    is_flag=True,
    help='directly find TCs in "testcase-directory/"'
    + '\ndefault is "testcase-directory/{filepath}"',
)
@click.option(
    "--runtime", "-r", is_flag=True, help="Ignore testcase, write data manually"
)
@click.option("--timelimit", "-t", default=3, help="time limit")
@click.option("--copytool", "-c", default="xclip", help="copy command after AC")
def run(filepath, testcase_directory, no_subdirectory, runtime, timelimit, copytool):
    """Simple Judge Tool"""
    # Preprocess args
    filepath, testcase_directory, pname = preprocess(
        filepath, testcase_directory, no_subdirectory
    )

    # Compile
    runame = compile(filepath)

    # Find testcases
    in_paths = sorted(glob.glob(os.path.join(testcase_directory, "*.in")))
    if not runtime and len(in_paths) == 0:
        click.secho("No input data!", fg="bright_red")
        runtime = True

    # Check runtime
    if runtime:
        click.secho(f"Runtime Mode ({runame})", fg="bright_cyan")
        os.system(runame)
        exit(0)

    # Judge!
    maxtime = 0
    align_length = max([len(s) for s in in_paths]) - len(testcase_directory) - 3
    wa_list = []
    AC_cnt = 0
    for in_path in in_paths:
        path, ext = os.path.splitext(in_path)
        tcname = os.path.basename(path)
        out_path = path + ".out"
        ans_path = path + ".ans"

        click.echo(tcname.rjust(align_length) + " ", nl=False)
        start_time = time.time_ns()
        with open(in_path, "r") as input_file, open(out_path, "w") as f:
            try:
                result = subprocess.run(
                    [runame], stdin=input_file, stdout=f, timeout=timelimit
                )
            except subprocess.TimeoutExpired:
                maxtime = timelimit * 1000
                click.secho("TLE", fg="bright_red")
                continue
        tc_time = (time.time_ns() - start_time) // 1000000
        maxtime = max(maxtime, tc_time)
        if result.returncode != 0:
            click.secho("RTE ", fg="bright_blue", nl=False)
        elif not os.path.isfile(ans_path):
            click.secho("? (no ans data)", fg="bright_black", nl=False)
        elif os.system(f"diff -wB {out_path} {ans_path} > /dev/null") != 0:
            click.secho("WA  ", fg="bright_red", nl=False)
            wa_list.append(tcname)
        else:
            click.secho("AC  ", fg="bright_green", nl=False)
            AC_cnt += 1
        click.echo(f"{tc_time}ms")
    click.secho(f"Maximum Time: {maxtime}ms", fg="bright_white")

    if AC_cnt == len(in_paths):
        com = f"{copytool} {filepath}"
        click.echo(com)
        os.system(com)

    # Write recent info
    recent = {
        "problem_name": pname,
        "filepath": filepath,
        "testcase_directory": os.path.abspath(testcase_directory),
        "wa_list": wa_list,
    }

    with open(".tmp/recent", "w") as f:
        json.dump(recent, f)


if __name__ == "__main__":
    run()
