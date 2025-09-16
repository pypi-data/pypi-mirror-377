# ruff: noqa: SLF001
from unittest.mock import Mock

import pytest

from src.ruff_severity_changer import ruff_severity_changer
from src.ruff_severity_changer.ruff_severity_changer import Severity


def create_gitlab_issue(check_name: str) -> ruff_severity_changer.GitlabIssue:
    return ruff_severity_changer.GitlabIssue(
        description="Meaningless description",
        check_name=check_name,
        fingerprint="sometotallymeaninglessfingerprint2137",
        severity=Severity.major,
        location=ruff_severity_changer.GitlabIssueLocation(
            path="NonExistentFile",
            lines=ruff_severity_changer.GitlabIssueLines(begin=0),
            positions=None,
        ),
    )


class TestSeverityMatcher:
    class TestInitialization:
        def test_empty_configuration(self):
            sut = ruff_severity_changer.SeverityMatcher({})

            assert not sut._matchers

        def test_simple_config_with_all_levels(self):
            config = {"F": "major", "E": "minor", "W": "info", "D": "unknown"}

            sut = ruff_severity_changer.SeverityMatcher(config)

            assert len(sut._matchers) == len(config)
            expected_levels = {Severity(severity) for severity in config.values()}
            actual_levels = {severity for _, severity in sut._matchers}
            assert actual_levels == expected_levels

        def test_matchers_are_reverse_sorted(self):
            config = {
                "W304": "minor",
                "F": "major",
                "E": "minor",
                "W": "info",
                "W5": "unknown",
            }
            expected = ["minor", "unknown", "major", "minor", "info"]

            sut = ruff_severity_changer.SeverityMatcher(config)

            for expected_severity, actual_severity in zip(
                expected,
                (severity for _, severity in sut._matchers),
            ):
                assert expected_severity == actual_severity

    class TestGetSeverity:
        @pytest.fixture(autouse=True)
        def _severity_matcher_with_loaded_config(self):
            self.config = {
                "E505": "info",
                "F": "major",
                "E": "minor",
                "W": "info",
                "D": "unknown",
            }
            self.sut = ruff_severity_changer.SeverityMatcher(self.config)

        def test_matches(self):
            issues_with_expected_result = [
                (
                    create_gitlab_issue("F001"),
                    Severity.major,
                ),
                (
                    create_gitlab_issue("E001"),
                    Severity.minor,
                ),
                (
                    create_gitlab_issue("W001"),
                    Severity.info,
                ),
                (
                    create_gitlab_issue("D001"),
                    Severity.unknown,
                ),
            ]

            for issue, expected in issues_with_expected_result:
                assert expected == self.sut.get_severity(issue)

        def test_not_matches(self):
            expected = Severity.major
            issue = create_gitlab_issue("U001")

            assert expected == self.sut.get_severity(issue)

        def test_matches_more_specific(self):
            issues_with_expected_result = [
                (
                    # Minor issue
                    create_gitlab_issue("E001"),
                    Severity.minor,
                ),
                # Level not in config
                (create_gitlab_issue("U001"), Severity.major),
                # More specific info issue
                (create_gitlab_issue("E505"), Severity.info),
                # Other minor issue
                (create_gitlab_issue("E002"), Severity.minor),
            ]

            for issue, expected in issues_with_expected_result:
                assert expected == self.sut.get_severity(issue)


class TestMain:
    @pytest.fixture()
    def _mock_stdin(self, monkeypatch):
        input_file = open("tests/ruff_output.json", "r")  # noqa: SIM115
        monkeypatch.setattr(
            "src.ruff_severity_changer.ruff_severity_changer.stdin", input_file
        )
        yield
        input_file.close()

    @pytest.fixture()
    def _mock_argparse(self, monkeypatch):
        mock_argparser = Mock()
        mock_argparser_class = Mock(return_value=mock_argparser)
        mock_namespace = Mock()
        mock_namespace.toml_path = "tests/test_pyproject.toml"
        mock_argparser.parse_args.return_value = mock_namespace
        monkeypatch.setattr(
            "src.ruff_severity_changer.ruff_severity_changer.argparse.ArgumentParser",
            mock_argparser_class,
        )

    @pytest.mark.usefixtures("_mock_stdin", "_mock_argparse")
    def test_run(self, monkeypatch):
        mock_dump = Mock()
        monkeypatch.setattr(
            "src.ruff_severity_changer.ruff_severity_changer.json.dump", mock_dump
        )

        ruff_severity_changer.main()

        ruff_report: ruff_severity_changer.CQReport = mock_dump.call_args.args[0]

        for issue, severity in (
            (issue["check_name"], issue["severity"]) for issue in ruff_report
        ):
            if issue.startswith("N") or issue == "E741":
                assert severity == Severity.info
            elif issue.startswith("E"):
                assert severity == Severity.minor
            else:
                assert severity == Severity.major
