#!/usr/bin/env python3
import click
import os
import json


@click.command()
@click.option("--tool", "-t", default="diff", help="your diff command")
@click.option("-y", is_flag=True, help="do not ask")
def diff(tool, y):
    """Diff Recent WAs"""
    with open(".tmp/recent", "r") as f:
        recent = json.load(f)

    problem_name = recent["problem_name"]
    testcase_directory = recent["testcase_directory"]
    wa_list = recent["wa_list"]

    # Echo
    click.secho(f"diff. problem '{problem_name}', ", fg="bright_cyan", nl=False)
    if len(wa_list) == 0:
        click.secho("There is no WA!", fg="bright_cyan")
        exit(0)
    click.secho(
        f'There is {len(wa_list)} WA(s)({", ".join(wa_list)})',
        fg="bright_cyan",
        nl=False,
    )
    click.secho(f" {tool}", fg="blue")

    for i, wa in enumerate(wa_list):
        click.echo(f"{wa} ({i+1}/{len(wa_list)})")

        while True:
            ch = "y" if y else input("Show? (y/n/q/yq) >")
            if ch and ch.strip()[0].lower() in "ynq":
                if ch[0] == "y":
                    out = os.path.join(testcase_directory, wa + ".out")
                    ans = os.path.join(testcase_directory, wa + ".ans")
                    os.system(f"{tool} {out} {ans}")
                    if ch == "yq":
                        exit(0)
                    break
                elif ch == "q":
                    exit(0)
                elif ch == "n":
                    break
                else:
                    continue


if __name__ == "__main__":
    diff()
