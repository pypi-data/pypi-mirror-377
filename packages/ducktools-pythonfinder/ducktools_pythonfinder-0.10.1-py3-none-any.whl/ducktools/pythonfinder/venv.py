# ducktools-pythonfinder
# MIT License
#
# Copyright (c) 2023-2025 David C Ellis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

try:
    from _collections_abc import Iterable
except ImportError:
    from collections.abc import Iterable

import os
import sys

from ducktools.classbuilder.prefab import Prefab, attribute
from ducktools.lazyimporter import LazyImporter, FromImport, ModuleImport

from .shared import (
    PythonInstall,
    DetailFinder,
    version_str_to_tuple,
    version_tuple_to_str,
)


_laz = LazyImporter(
    [
        ModuleImport("re"),
        ModuleImport("json"),
        ModuleImport("subprocess"),
        FromImport("pathlib", "Path"),
        FromImport("subprocess", "run"),
        FromImport(".", "package_list_script"),
    ],
    globs=globals()
)

VENV_CONFIG_NAME = "pyvenv.cfg"


# VIRTUALENV can make some invalid regexes that are just the tuple with dots.
VIRTUALENV_PY_VER_RE = (
    r"(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<micro>\d*)\.(?P<releaselevel>.+)\.(?P<serial>\d*)?"
)


class InvalidVEnvError(Exception):
    pass


class PythonPackage(Prefab):
    name: str
    version: str


class PythonVEnv(Prefab):
    folder: str
    executable: str
    version: tuple[int, int, int, str, int]
    parent_path: str
    _parent_executable: str | None = attribute(default=None, repr=False)

    @property
    def version_str(self) -> str:
        return version_tuple_to_str(self.version)

    @property
    def parent_executable(self) -> str | None:
        if self._parent_executable is None:
            # Guess the parent executable file
            parent_exe = None
            if sys.platform == "win32":
                parent_exe = os.path.join(self.parent_path, "python.exe")
            else:
                # try with additional numbers in order eg: python3.13, python313, python3, python
                suffixes = [
                    f"{self.version[0]}.{self.version[1]}",
                    f"{self.version[0]}{self.version[1]}",
                    f"{self.version[0]}",
                    ""
                ]

                for suffix in suffixes:
                    parent_exe = os.path.join(self.parent_path, f"python{suffix}")
                    if os.path.exists(parent_exe):
                        break

            if not (parent_exe and os.path.exists(parent_exe)):
                try:
                    pyout = _laz.run(
                        [
                            self.executable,
                            "-c",
                            "import sys; sys.stdout.write(getattr(sys, '_base_executable', ''))",
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except (_laz.subprocess.CalledProcessError, FileNotFoundError):
                    pass
                else:
                    if out_exe := pyout.stdout:
                        parent_exe = os.path.join(self.parent_path, os.path.basename(out_exe))

            self._parent_executable = parent_exe

        return self._parent_executable

    @property
    def parent_exists(self) -> bool:
        if self.parent_executable and os.path.exists(self.parent_executable):
            return True
        return False

    def get_parent_install(
        self,
        cache: list[PythonInstall] | None = None,
        finder: DetailFinder | None = None,
    ) -> PythonInstall | None:
        install = None
        cache = [] if cache is None else cache

        finder = DetailFinder() if finder is None else finder

        if self.parent_exists:
            # parent_exists forces this check
            assert self.parent_executable is not None

            exe = self.parent_executable

            # Python installs may be cached, can skip querying exe.
            for inst in cache:
                if os.path.samefile(inst.executable, exe):
                    install = inst
                    break

            if install is None:
                with finder:
                    install = finder.get_install_details(exe)

        return install

    def list_packages(self) -> list[PythonPackage]:
        if not self.parent_exists:
            raise FileNotFoundError(
                f"Parent Python at \"{self.parent_executable}\" does not exist."
            )

        package_list_script = _laz.package_list_script.__file__

        data = _laz.run(
            [self.executable, package_list_script],
            capture_output=True,
            text=True,
            check=True,
        )

        raw_packages = data.stdout.split("\n")

        packages = [
            PythonPackage(*p.split("=="))
            for p in raw_packages
            if p
        ]

        return packages

    @classmethod
    def from_cfg(cls, cfg_path: str | os.PathLike) -> PythonVEnv:
        """
        Get a PythonVEnv instance from the path to a config file

        :param cfg_path: Path to a virtualenv config file
        :return: PythonVEnv with details relative to that config file
        """
        venv_base = os.path.dirname(cfg_path)

        with open(cfg_path, 'r') as f:
            conf = {}
            for line in f:
                key, _, value = [item.strip() for item in line.partition("=")]
                conf[key] = value

        parent_path = conf.get("home")
        version_str = conf.get("version", conf.get("version_info"))
        parent_exe = conf.get("executable", conf.get("base-executable"))

        if parent_path is None or version_str is None:
            # Not a valid venv
            raise InvalidVEnvError(f"Path or version not defined in {cfg_path}")

        if sys.platform == "win32":
            venv_exe = os.path.join(venv_base, "Scripts", "python.exe")
        else:
            venv_exe = os.path.join(venv_base, "bin", "python")

        try:
            version_tuple = version_str_to_tuple(version_str)
        except ValueError:  # pragma: no cover
            # Might be virtualenv putting in incorrect versions
            parsed_version = _laz.re.fullmatch(VIRTUALENV_PY_VER_RE, version_str)
            if parsed_version:
                major, minor, micro, releaselevel, serial = parsed_version.groups()
                version_tuple = (
                    int(major),
                    int(minor),
                    int(micro) if micro else 0,
                    releaselevel,
                    int(serial if serial != "" else 0),
                )
            else:
                raise InvalidVEnvError(
                    f"Could not determine version from venv version string {version_str}"
                )

        return cls(
            folder=venv_base,
            executable=venv_exe,
            version=version_tuple,
            parent_path=parent_path,
            _parent_executable=parent_exe,
        )


def get_python_venvs(
    base_dir: str | os.PathLike | None = None,
    recursive: bool = False,
    search_parent_folders: bool = False
) -> Iterable[PythonVEnv]:
    """
    Yield discoverable python virtual environment information

    If recursive=True and search_parent_folders=True *only* the current working
    directory will be searched recursively. Parent folders will not be searched recursively

    If you're in a project directory and are looking for a potential venv
    search_parent_folders=True will search parents and yield installs discovered.

    If you're in a folder of source trees and want to find venvs inside any subfolders
    then use recursive=True.

    :param base_dir: Base directory to search venvs
    :param recursive: Also check subfolders of the base directory
    :param search_parent_folders: Also search parent folders
    :yield: PythonVEnv details.
    """
    # This converts base_dir to a Path, but mypy doesn't know that
    base_dir = _laz.Path.cwd() if base_dir is None else _laz.Path(base_dir)

    cwd_pattern = pattern = f"*/{VENV_CONFIG_NAME}"

    if recursive:
        # Only search cwd recursively, parents are searched non-recursively
        cwd_pattern = "*" + pattern

    for conf in base_dir.glob(cwd_pattern):  # type: ignore
        try:
            env = PythonVEnv.from_cfg(conf)
        except InvalidVEnvError:
            continue
        yield env

    if search_parent_folders:
        # Search parent folders
        for fld in base_dir.parents:  # type: ignore
            try:
                for conf in fld.glob(pattern):
                    try:
                        env = PythonVEnv.from_cfg(conf)
                    except InvalidVEnvError:
                        continue
                    yield env
            except OSError as e:
                # MacOS can error on searching up folders with an invalid argument
                # On Python 3.11 or earlier.
                if e.errno != 22:
                    raise


def list_python_venvs(
    base_dir: str | os.PathLike | None = None,
    recursive: bool = False,
    search_parent_folders: bool = False,
) -> list[PythonVEnv]:
    """
    Get a list of discoverable python virtual environment information

    If recursive=True then search_parent_folders is ignored.

    :param base_dir: Base directory to search venvs
    :param recursive: Also check subfolders of the base directory
    :param search_parent_folders: Also search parent folders
    :returns: List of Python VEnv details.
    """
    return list(
        get_python_venvs(
            base_dir=base_dir,
            recursive=recursive,
            search_parent_folders=search_parent_folders,
        )
    )
