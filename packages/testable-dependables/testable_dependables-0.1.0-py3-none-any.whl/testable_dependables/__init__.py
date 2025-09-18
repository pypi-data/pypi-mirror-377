from json import dumps
from pathlib import Path
from typing import Annotated

import typer

from testable_dependables.loader import get_cwd, get_pyproject_data
from testable_dependables.version_retriever import get_versions

app = typer.Typer()


@app.command()
def output(
    path: Annotated[Path, typer.Argument(help="The path of the pyproject.toml.")] = Path("."),
    json: Annotated[bool, typer.Option(help="Output in JSON.")] = False,  # noqa: FBT002
    verbose: Annotated[bool, typer.Option(help="Verbosity.")] = False,  # noqa: FBT002
) -> None:
    """Suggest new classifiers for a library."""

    cwd = get_cwd(path)
    data = get_pyproject_data(cwd, is_verbose=verbose)

    requires_python = data["project"]["requires-python"]
    python_specifier = f"Python{requires_python}"

    versions = get_versions(python_specifier, is_verbose=verbose)

    if verbose:
        typer.secho()
        typer.secho("Versions that fit requirements:")

    if json:
        typer.secho(dumps(versions))
    else:
        for version in versions:
            typer.secho(version)


if __name__ == "__main__":
    app()
