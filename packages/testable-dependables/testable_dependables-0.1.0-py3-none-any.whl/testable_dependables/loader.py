import tomllib
from pathlib import Path
from typing import Any

import typer


def get_cwd(path: Path | None = None) -> Path:
    path = path or Path(".").resolve()

    if not path.exists():
        raise FileNotFoundError("No such directory")

    if not path.is_dir():
        raise AssertionError("Path is not a directory")

    return path


def get_pyproject_data(cwd: Path, is_verbose: bool = False) -> dict[str, Any]:  # noqa: FBT001, FBT002
    pyproject_path = cwd / "pyproject.toml"

    if is_verbose:
        typer.secho(f"Loading data from '{pyproject_path.parent}'", fg=typer.colors.BLUE)

    return tomllib.loads(pyproject_path.read_text())
