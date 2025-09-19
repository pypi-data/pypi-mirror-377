#!/usr/bin/env python3
import click
import os
import json
import glob


@click.command()
@click.argument("testcases", nargs=-1)
@click.option("--problem", "-p", default=".", help="problem name of testcase")
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
    + '\ndefault is "testcase-directory/{filename}"',
)
@click.option("--tool", "-t", default="vim", help="your editor command")
@click.option("-y", is_flag=True, help="do not ask")
def tc(testcases, problem, testcase_directory, no_subdirectory, tool, y):
    """Open testcases with editor"""
    # Preprocess Args
    problem, ext = os.path.splitext(problem)
    problem = (problem + " ")[: problem.find("_")]
    if problem == ".":
        with open(".tmp/recent", "r") as f:
            problem = json.load(f)["problem_name"]
    if not no_subdirectory:
        testcase_directory = os.path.join(testcase_directory, problem)

    testcases = set(testcases)
    if len(testcases) == 0 or "." in testcases:
        tc = glob.glob(f"{testcase_directory}/*.in")
        tc = set(map(lambda x: os.path.splitext(os.path.basename(x))[0], tc))
        testcases -= {"."}
        testcases |= tc

    # Check directory existence
    os.makedirs(testcase_directory, exist_ok=True)

    # Echo
    click.secho(f"tc. problem '{problem}', ", fg="bright_cyan", nl=False)
    if len(testcases) == 0:
        click.secho("There is no TC!", fg="bright_cyan")
        exit(0)
    click.secho(
        f'There is {len(testcases)} TC(s)({", ".join(testcases)})',
        fg="bright_cyan",
        nl=False,
    )
    click.secho(f" {tool}", fg="blue")

    # Open
    for i, tc in enumerate(sorted(testcases)):
        click.echo(f"{tc} ({i+1}/{len(testcases)})")
        while True:
            ch = "y" if y else input("Open? (y/n/q/yq) >")
            if ch and ch.strip()[0].lower() in "ynq":
                if ch[0] == "y":
                    inn = os.path.join(testcase_directory, tc + ".in")
                    ans = os.path.join(testcase_directory, tc + ".ans")
                    command = f"{tool} {inn} {ans}"
                    click.echo(command)
                    os.system(command)
                    if ch == "yq":
                        exit(0)
                elif ch == "q":
                    exit(0)
                break


if __name__ == "__main__":
    tc()
