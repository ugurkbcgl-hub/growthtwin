"""Ensure distributable Python archives contain the Django demo templates."""

import tarfile
import tomllib
import zipfile
from pathlib import Path

DIST_DIRECTORY = Path(__file__).resolve().parents[1] / "dist"
PROJECT = tomllib.loads(
    (DIST_DIRECTORY.parent / "pyproject.toml").read_text(encoding="utf-8")
)["project"]
NORMALIZED_PROJECT_NAME = PROJECT["name"].replace("-", "_")
PROJECT_VERSION = PROJECT["version"]
REQUIRED_FILES = {
    "growthtwin/demo/templates/demo/profile_edit.html",
    "growthtwin/demo/templates/registration/login.html",
}


def require_files(distribution_name: str, files: set[str]) -> None:
    missing = REQUIRED_FILES - files
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise SystemExit(
            f"{distribution_name} is missing required package files: {missing_list}"
        )


def main() -> None:
    wheels = sorted(
        DIST_DIRECTORY.glob(f"{NORMALIZED_PROJECT_NAME}-{PROJECT_VERSION}-*.whl")
    )
    source_distributions = sorted(
        DIST_DIRECTORY.glob(f"{NORMALIZED_PROJECT_NAME}-{PROJECT_VERSION}.tar.gz")
    )
    if len(wheels) != 1 or len(source_distributions) != 1:
        raise SystemExit(
            "Expected exactly one wheel and one source distribution in "
            f"{DIST_DIRECTORY}"
        )

    with zipfile.ZipFile(wheels[0]) as wheel:
        require_files("Wheel", set(wheel.namelist()))

    with tarfile.open(source_distributions[0], mode="r:gz") as source:
        source_files = {
            member.name.split("/", maxsplit=1)[1]
            for member in source.getmembers()
            if member.isfile() and "/" in member.name
        }
        require_files("Source distribution", source_files)

    print("Both distributions contain the login and profile templates.")


if __name__ == "__main__":
    main()
