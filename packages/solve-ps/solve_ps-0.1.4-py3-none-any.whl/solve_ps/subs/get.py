#!/usr/bin/env python3
import click
import requests
import re
import os
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
}

sources = {
    "boj": {
        "url": "https://acmicpc.net/problem/%s",
        "input": lambda soup: soup.find_all(
            attrs={"id": re.compile("sample-input-\d*")}
        ),
        "ans": lambda soup: soup.find_all(
            attrs={"id": re.compile("sample-output-\d*")}
        ),
    },
    "cf-contest": {
        "url": "https://codeforces.com/contest/%s/problem/%s",
        "input": lambda soup: list(
            map(lambda div: div.find("pre"), soup.find_all(attrs={"class": "input"}))
        ),
        "ans": lambda soup: list(
            map(lambda div: div.find("pre"), soup.find_all(attrs={"class": "output"}))
        ),
    },
}


def guess_src(src):
    for key, val in sources.items():
        if key.startswith(src):
            return key, val
    raise click.ClickException("Invalid source " + src)


@click.command()
@click.argument("source", nargs=1)
@click.argument("problem", nargs=-1)
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
def get(source, problem, testcase_directory, no_subdirectory):
    """Fetch testcase"""
    key, src = guess_src(source)
    webpage = requests.get(src["url"] % problem, headers=headers)
    soup = BeautifulSoup(webpage.content, "html.parser")
    INS = src["input"](soup)
    ANS = src["ans"](soup)

    if len(INS) == 0:
        raise click.ClickException("Cannot find testcases from " + src["url"] % problem)

    if not no_subdirectory:
        testcase_directory = os.path.join(testcase_directory, "".join(problem))
    testcase_directory.rstrip("/")
    testcase_directory += "/"
    if not os.path.exists(testcase_directory):
        os.makedirs(testcase_directory)

    for i, IN, AN in zip(map(str, range(1, len(INS) + 1)), INS, ANS):
        with open(testcase_directory + str(i) + ".in", "w") as f:
            f.write(IN.text.strip().replace("\r", ""))
        with open(testcase_directory + str(i) + ".ans", "w") as f:
            f.write(AN.text.strip().replace("\r", ""))
    click.echo(f"Successfully crawled {len(INS)} testcases ", nl=False)
    click.secho(f"from {key}", fg="bright_black")


if __name__ == "__main__":
    get()
