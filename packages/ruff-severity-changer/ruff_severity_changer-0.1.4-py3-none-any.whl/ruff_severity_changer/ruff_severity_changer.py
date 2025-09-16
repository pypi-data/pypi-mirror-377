import argparse
import json
import re
from enum import StrEnum
from pathlib import Path
from re import Pattern
from string import ascii_letters
from sys import stdin, stdout
from typing import TypedDict

import tomllib


class Severity(StrEnum):
    major = "major"
    minor = "minor"
    info = "info"
    unknown = "unknown"


class GitlabIssueLines(TypedDict):
    begin: int


class GitlabIssuePosition(TypedDict):
    line: int
    column: int


class GitlabIssuePositions(TypedDict):
    begin: GitlabIssuePosition
    end: GitlabIssuePosition


class GitlabIssueLocation(TypedDict):
    path: str
    lines: GitlabIssueLines | None
    positions: GitlabIssuePositions | None


class GitlabIssue(TypedDict):
    description: str
    check_name: str
    fingerprint: str
    severity: Severity
    location: GitlabIssueLocation


CQReport = list[GitlabIssue]


class SeverityMatcher:
    def __init__(self, configuration: dict[str, str]) -> None:
        sorted_config: list[tuple[str, Severity]] = [
            (k, Severity(v)) for (k, v) in configuration.items()
        ]
        sorted_config.sort(key=lambda t: len(t[0].lstrip(ascii_letters)), reverse=True)

        self._matchers: list[tuple[Pattern[str], Severity]] = [
            (re.compile(pattern=rf"^{code}\d*"), level) for (code, level) in sorted_config
        ]

    def get_severity(self, issue: GitlabIssue) -> Severity:
        for matcher, severity in self._matchers:
            if matcher.match(issue["check_name"]):
                return severity
        return Severity.major


def main() -> None:
    argument_parser = argparse.ArgumentParser("Ruff Severity Changer", description="")
    argument_parser.add_argument(
        "--config",
        nargs="?",
        default="pyproject.toml",
        type=Path,
        dest="toml_path",
    )
    cli_arguments = argument_parser.parse_args()
    ruff_report: CQReport = json.load(stdin)
    configuration: dict[str, str] = {}
    with open(cli_arguments.toml_path, "rb") as toml:
        configuration = tomllib.load(toml)["tool"]["ruff_severity_changer"]
    severity_matcher = SeverityMatcher(configuration)

    for issue in ruff_report:
        issue["severity"] = severity_matcher.get_severity(issue)

    json.dump(ruff_report, stdout, indent="\t")


if __name__ == "__main__":
    main()
