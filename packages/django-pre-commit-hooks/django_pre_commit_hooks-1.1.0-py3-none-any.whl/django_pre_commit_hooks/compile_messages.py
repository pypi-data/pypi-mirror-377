from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from django.core.management import execute_from_command_line


def main(argv: Sequence[str] | None = None) -> int:
    """Run django-admin compilemessages for each .po file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    retval = 0
    for filename in args.filenames:
        path = Path(filename)
        # Assume the path is <locale>/LC_MESSAGES/django.po
        locale = path.parent.parent
        execute_from_command_line(
            [
                "django-admin",
                "compilemessages",
                "--locale",
                locale.name,
                "--ignore",
                ".venv",
                "--ignore",
                ".tox",
            ]
        )
    return retval


if __name__ == "__main__":
    raise SystemExit(main())
