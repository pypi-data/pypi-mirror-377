# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: Apache-2.0

"""Wrapper for (some) Android build-tools."""


import re
import os
import pathlib
from typing import Optional


def _highest_ver_dir(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Find subfolder where the name corresponds to the hights version number.

    This function assumes that the passed path is a folder which contains
    subfolders, which have names that are valid semver version designations.
    e.g. ['11.0.1', '23.0.3', '30.0.0-rc1', '30.0.0'] etc.
    With this set of subdirectories this function will return path / '30.0.0'

    If path is not a directory or if there are no sub directoryies with valid
    version names, this function will return None.
    """
    if path.is_dir():
        ver_dirs = [(Ver(str(b.name)), b) for b in path.iterdir()]
        if len(ver_dirs) > 0:
            return sorted(ver_dirs)[-1][1]
    return None


def lookup_android_home() -> Optional[pathlib.Path]:
    """Find android sdk installation location.

    This lookup will try env $ANDROID_HOME first. Then it will try well knows
    default installation paths. If it can't find an any matching directories it
    will return None.
    """
    android_home = pathlib.Path(
        os.environ.get("ANDROID_HOME", r'<>:"/\|?*-invalid-dir')
    )
    if android_home.is_dir():
        return android_home
    default_windows = pathlib.Path.home() / "AppData" / "Local" / "Android" / "Sdk"
    if default_windows.is_dir():
        return default_windows
    default_osx = pathlib.Path.home() / "Library" / "Android" / "sdk"
    if default_osx.is_dir():
        return default_osx
    default_linux = pathlib.Path.home() / "Android" / "Sdk"
    if default_linux.is_dir():
        return default_linux
    default_sdkmanager = pathlib.Path("/opt/android-sdk")
    if default_sdkmanager.is_dir():
        return default_sdkmanager
    if default_linux.is_dir():
        return default_linux
    return None


def lookup_buildtools_bin(bin_name, android_home=None) -> Optional[pathlib.Path]:
    """Find install location of a specific build-tools binary."""
    if not android_home:
        android_home = lookup_android_home()
    if android_home:
        return _highest_ver_dir(pathlib.Path(android_home) / "build-tools") / bin_name
    return None


class Ver:
    """Helper class for parsinging and sorting Android build tools versions."""

    def __init__(self, version_string):
        """Create a new instance from version string."""
        self.version_string = version_string
        self.major, self.minor, self.patch, self.label = self.parse_version(
            version_string
        )

    def parse_version(self, version_string):
        """Parse version string and set object data based on that."""
        pattern = r"^(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?(?:-(?P<label>.+))?$"
        match = re.match(pattern, version_string)

        if match:
            major = int(match.group("major"))
            minor = int(match.group("minor")) if match.group("minor") else 0
            patch = int(match.group("patch")) if match.group("patch") else 0
            label = match.group("label") if match.group("label") else None
            return major, minor, patch, label
        else:
            raise ValueError(f"Invalid version string: {version_string}")

    def __str__(self):
        """Convert this back into a string."""
        return f"{self.major}.{self.minor}.{self.patch}" + (
            f"-{self.label}" if self.label else ""
        )

    def __lt__(self, other):
        """Compare if his is less that supplied other."""
        if not isinstance(other, Ver):
            return NotImplemented
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        ):
            if self.label is None and other.label is None:
                return False
            elif self.label is None:
                return False
            elif other.label is None:
                return True
            else:
                return self.label < other.label
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __gt__(self, other):
        """Compare if his is greater that supplied other."""
        return other.__lt__(self)
