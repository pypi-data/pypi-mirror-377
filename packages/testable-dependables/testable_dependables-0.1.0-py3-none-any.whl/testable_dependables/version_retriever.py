import typer
from packaging.requirements import Requirement
from packaging.version import Version
from packaging.version import parse as version_parse
from py_eol import supported_versions

# TODO: Use https://endoflife.date/api/python.json directly instead of `py-eol` package


def get_versions(requirement_specifier: str, is_verbose: bool = False) -> list[str]:  # noqa: FBT001, FBT002
    current_supported_versions = set(supported_versions())

    requirement = Requirement(requirement_specifier)

    versions = set()
    minor_versions = set()

    """
    Add versions for the floor and ceilings of major.minor versions of the specifier.

    Examples:
        - if the specifier is "Python>=3.9.7", include 3.9.7 in the `versions`
        - if the specifier is "Python<=3.9.7", include 3.9.7 in the `versions`
        - if the specifier is "Python<3.9.7", include 3.9.6 in the `versions`
        - if the specifier is "Python>3.9.7", include 3.9.8 in the `versions`
    """
    for specifier in requirement.specifier:
        version = version_parse(specifier.version)
        minor_versions.add(version.minor)

        if f"{version.major}.{version.minor}" not in current_supported_versions:
            if is_verbose:
                typer.secho(f"WARNING: {version} is EOL.", fg=typer.colors.RED)

            continue

        if specifier.operator in ("<=", ">=", "=="):
            versions.add(version)
        elif specifier.operator == "<":
            if version.micro > 0:
                version = Version(f"{version.major}.{version.minor}.{version.micro - 1}")
                versions.add(version)
        elif specifier.operator == ">":
            # TODO: Check that micro version is valid before adding it
            # Could use https://endoflife.date/api/python.json, maybe
            version = Version(f"{version.major}.{version.minor}.{version.micro + 1}")
            versions.add(version)
        elif specifier.operator == "!=":
            raise AssertionError("Not supported")

    # Add versions of Python that are currently supported and fit within the specifiers
    for supported_version in current_supported_versions:
        version = version_parse(supported_version)

        if requirement.specifier.contains(version):
            if version.minor not in minor_versions:
                versions.add(version)

    sorted_versions = sorted([str(version) for version in versions])

    return sorted_versions
