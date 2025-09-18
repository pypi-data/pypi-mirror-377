from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from django_pre_commit_hooks.compile_messages import main

from .utils import get_resource_path


@pytest.fixture
def execute_from_command_line(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "django_pre_commit_hooks.compile_messages.execute_from_command_line"
    )


def test_no_files(execute_from_command_line):
    ret = main([])
    assert ret == 0
    execute_from_command_line.assert_not_called()


def test_failing_file(execute_from_command_line):
    execute_from_command_line.side_effect = SystemExit(1)
    with pytest.raises(SystemExit):
        main([get_resource_path("locales/fr_CA/LC_MESSAGES/test.po")])
    execute_from_command_line.assert_called_once_with(
        [
            "django-admin",
            "compilemessages",
            "--locale",
            "fr_CA",
            "--ignore",
            ".venv",
            "--ignore",
            ".tox",
        ],
    )


def test_passing_file(execute_from_command_line):
    ret = main([get_resource_path("locales/fr_FR/LC_MESSAGES/test.po")])
    assert ret == 0
    execute_from_command_line.assert_called_once_with(
        [
            "django-admin",
            "compilemessages",
            "--locale",
            "fr_FR",
            "--ignore",
            ".venv",
            "--ignore",
            ".tox",
        ],
    )
