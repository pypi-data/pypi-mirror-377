import json
import os
from typing import Optional

from . import github
from .features import FeaturesFile


def from_github(version: Optional[str] = None) -> tuple[str, FeaturesFile]:
    """Load web features data from the GitHub repository

    :param version: Version name e.g. "v2.34.0" or None for the latest version.
    :returns: Tuple of loaded version number and FeaturesFile"""
    release = github.get_release(version)
    data = github.get_data(release)
    return release.name, FeaturesFile.model_validate(data)


def from_file(path: str | os.PathLike) -> FeaturesFile:
    """Load web features data from a local file.

    :param path: Filesystem path to load features data from."""

    with open(path) as f:
        return FeaturesFile.model_validate(json.load(f))


def download(out_path: str | os.PathLike, version: Optional[str] = None) -> str:
    """Download web features data to a file.

    :param out_path: Filesystem path to write web features data to.
    :param version: Optional version number e.g. "v2.14.6". None for the latest version.
    """
    release = github.get_release(version)
    data = github.get_data(release)
    with open(out_path, "w") as f:
        json.dump(data, f)
    return release.name
