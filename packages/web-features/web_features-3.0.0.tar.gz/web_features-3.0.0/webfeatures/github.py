import re
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Sequence, Mapping

import httpx
from pydantic import BaseModel

Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None


@dataclass
class Links:
    prev: Optional[str] = None
    next: Optional[str] = None
    first: Optional[str] = None
    last: Optional[str] = None


@dataclass(frozen=True, order=True)
class VersionNumber:
    major: int
    minor: int
    patch: int


def parse_version_number(name: str) -> VersionNumber:
    parser = re.compile(r"v?(\d+)\.(\d+)(?:\.(\d+))?")
    m = parser.match(name)
    if m is None:
        raise ValueError(f"Failed to parse {name} as version string")
    major, minor, patch = m.groups()
    return VersionNumber(
        major=int(major), minor=int(minor), patch=int(patch) if patch is not None else 0
    )


class Asset(BaseModel):
    name: str
    browser_download_url: str


class Release(BaseModel):
    id: int
    name: str
    created_at: datetime
    published_at: datetime
    assets: list[Asset]

    @property
    def parsed_version(self):
        return parse_version_number(self.name)


def parse_link_header(header: str) -> Links:
    parser = re.compile('<([^>]+)>; rel="([^"]+)"')
    args = {
        key: url
        for url, key in parser.findall(header)
        if key in {"prev", "next", "first", "last"}
    }
    return Links(**args)


def get_json(
    url: str, headers: Optional[Mapping[str, str]] = None
) -> tuple[Json, Optional[str]]:
    resp = httpx.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()
    next_url = None
    if "link" in resp.headers:
        next_url = parse_link_header(resp.headers["link"]).next
    return resp.json(), next_url


def get_data(release: Release) -> Mapping[str, Json]:
    for asset in release.assets:
        if asset.name == "data.extended.json":
            data, _ = get_json(asset.browser_download_url)
            assert isinstance(data, dict)
            return data
    raise ValueError(f"Didn't find data.extended.json in release {release.name}")


def get_releases() -> Sequence[Release]:
    """Get a list of all released versions of web features"""
    next_url: Optional[str] = (
        "https://api.github.com/repos/web-platform-dx/web-features/releases"
    )
    releases = []
    while next_url is not None:
        data, next_url = get_json(
            next_url,
            {"Accept": "application/vnd.github+json"},
        )
        assert isinstance(data, list)
        for release_data in data:
            assert isinstance(release_data, dict)
            if release_data.get("draft", False) or release_data.get(
                "prerelease", False
            ):
                continue
            release = Release.model_validate(release_data)
            releases.append(release)
    return releases


def latest_release() -> Release:
    """Get the latest released version of web features"""
    releases = get_releases()
    if not releases:
        raise ValueError("No releases found")
    return sorted(releases, key=lambda release: release.parsed_version, reverse=True)[0]


def get_release_version(name: str) -> Release:
    """Get a named release of web features

    :param name: The version number of the release e.g. "v2.20.1"
    """
    name_re = re.compile(r"v\d+\.\d+\.\d+")
    if not name_re.match(name):
        raise ValueError(f"Invalid version {name}")

    url = f"https://api.github.com/repos/web-platform-dx/web-features/releases/tags/{name}"
    data, _ = get_json(url)
    return Release.model_validate(data)


def get_release(name: Optional[str]) -> Release:
    """Get the metadata for a specific release

    :param name: The name. of the release e.g. "v2.34.2" or None for the latest release."""
    if name:
        return get_release_version(name)
    return latest_release()
