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

import sys
import os

from ducktools.lazyimporter import LazyImporter, ModuleImport, FromImport

from . import list_python_installs, __version__
from .shared import purge_caches, version_str_to_tuple


TYPE_CHECKING = False
if TYPE_CHECKING:
    import argparse


_laz = LazyImporter(
    [
        ModuleImport("argparse"),
        ModuleImport("csv"),
        ModuleImport("re"),
        ModuleImport("subprocess"),
        ModuleImport("sysconfig"),
        ModuleImport("platform"),
        FromImport(".pythonorg_search", "PythonOrgSearch"),
        FromImport("packaging.specifiers", "SpecifierSet"),
        FromImport("urllib.error", "URLError"),
    ],
    globs=globals()
)


class UnsupportedPythonError(Exception):
    pass


def stop_autoclose() -> None:
    """
    Checks if it thinks windows will auto close the window after running

    The logic here is it checks if the PID of this task is running as py.exe

    By default py.exe is set as the runner for double-clicked .pyz files on
    windows.
    """
    autoclosing = False

    if sys.platform == "win32":
        exe_name = "py.exe"
        tasklist = _laz.subprocess.check_output(
            ["tasklist", "/v", "/fo", "csv", "/fi", f"PID eq {os.getppid()}"],
            text=True
        )
        data = _laz.csv.DictReader(tasklist.split("\n"))
        for entry in data:
            if entry["Image Name"] == exe_name:
                autoclosing = True
                break

    if autoclosing:
        _laz.subprocess.run("pause", shell=True)


def _get_parser_class() -> type[argparse.ArgumentParser]:
    # This class is deferred to avoid the argparse import
    # if there are no arguments to parse

    class FixedArgumentParser(_laz.argparse.ArgumentParser):  # type: ignore
        """
        The builtin argument parser uses shutil to figure out the terminal width
        to display help info. This one replaces the function that calls help info
        and plugs in a value for width.

        This prevents the unnecessary import.
        """

        def _get_formatter(self):
            # Calculate width
            try:
                columns = int(os.environ['COLUMNS'])
            except (KeyError, ValueError):
                try:
                    size = os.get_terminal_size()
                except (AttributeError, ValueError, OSError):
                    # get_terminal_size unsupported
                    columns = 80
                else:
                    columns = size.columns

            # noinspection PyArgumentList
            return self.formatter_class(prog=self.prog, width=columns - 2)

    return FixedArgumentParser


def get_parser() -> argparse.ArgumentParser:
    FixedArgumentParser = _get_parser_class()  # noqa

    parser = FixedArgumentParser(
        prog="ducktools-pythonfinder",
        description="Discover base Python installs",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=False)

    clear_cache = subparsers.add_parser(
        "clear-cache",
        help="Clear the cache of Python install details"
    )

    online = subparsers.add_parser(
        "online",
        help="Get links to binaries from python.org"
    )

    # Shared arguments
    for p in [parser, online]:
        p.add_argument("--min", help="Specify minimum Python version")
        p.add_argument("--max", help="Specify maximum Python version")
        p.add_argument("--compatible", help="Specify compatible Python version")

    online.add_argument(
        "--all-binaries",
        action="store_true",
        help="Provide *all* matching binaries and "
             "not just the latest minor versions"
    )
    online.add_argument(
        "--system",
        action="store",
        help="Get python installers for a different system (eg: Windows, Darwin, Linux)"
    )
    online.add_argument(
        "--machine",
        action="store",
        help="Get python installers for a different architecture (eg: AMD64, ARM64, x86)"
    )

    online.add_argument(
        "--prerelease",
        action="store_true",
        help="Include prerelease versions"
    )

    return parser


def display_local_installs(
    min_ver: str | None = None,
    max_ver: str | None = None,
    compatible: str | None = None,
) -> None:
    if min_ver:
        min_ver_tuple = version_str_to_tuple(min_ver)
    if max_ver:
        max_ver_tuple = version_str_to_tuple(max_ver)
    if compatible:
        compatible_spec = _laz.SpecifierSet(f"~={compatible}")

    installs = list_python_installs()

    headings = ["Version", "Executable Location"]

    install_collection: list[tuple[str, str]] = []
    max_version_len = len(headings[0])
    max_executable_len = len(headings[1])

    alternate_implementations = False

    # First collect the strings
    for install in installs:
        if min_ver and install.version < min_ver_tuple:
            continue
        elif max_ver and install.version > max_ver_tuple:
            continue
        elif compatible and not compatible_spec.contains(install.version_str):
            continue

        version_str = install.version_str

        if sys.platform == "win32":
            if install.metadata.get("InWindowsRegistry"):
                version_str = f"+{version_str}"
            if install.architecture == "32bit":
                version_str = f"^{version_str}"

        if install.executable == sys.executable:
            version_str = f"*{version_str}"
        elif (
            sys.prefix != sys.base_prefix
            and install.paths.get("stdlib") == _laz.sysconfig.get_path("stdlib")
        ):
            version_str = f"**{version_str}"

        if install.metadata.get("freethreaded"):
            version_str = f"{version_str}t"

        if install.shadowed:
            version_str = f"[{version_str}]"

        if (
            install.implementation != "cpython"
            and install.implementation_version != install.version
        ):
            alternate_implementations = True
            version_str = f"({install.implementation_version_str}) {version_str}"

        max_version_len = max(max_version_len, len(version_str))
        max_executable_len = max(max_executable_len, len(install.executable))

        install_collection.append((version_str, install.executable))

    print("Discoverable Python Installs")
    print()
    if alternate_implementations:
        print("Alternate implementation versions are listed in parentheses")

    if sys.platform == "win32":
        print("+ - Listed in the Windows Registry ")
        print("^ - This is a 32-bit Python install")
    if sys.platform != "win32":
        print("[] - This Python install is shadowed by another on Path")
    print("* - This is the active Python executable used to call this module")
    print("** - This is a parent Python executable of the venv used to call this module")
    print()

    headings_str = f"| {headings[0]:<{max_version_len}s} | {headings[1]:<{max_executable_len}s} |"
    print(headings_str)
    print(f"| {'-' * max_version_len} | {'-' * max_executable_len} |")

    for version_str, executable in install_collection:
        print(f"| {version_str:>{max_version_len}s} | {executable:<{max_executable_len}s} |")


def display_remote_binaries(
    min_ver: str,
    max_ver: str,
    compatible: str,
    all_binaries: bool,
    system: str,
    machine: str,
    prerelease: bool,
) -> None:
    specs = []
    if min_ver:
        specs.append(f">={min_ver}")
    if max_ver:
        specs.append(f"<{max_ver}")
    if compatible:
        specs.append(f"~={compatible}")

    spec = _laz.SpecifierSet(",".join(specs))

    searcher = _laz.PythonOrgSearch(system=system, machine=machine)
    if all_binaries:
        releases = searcher.all_matching_binaries(spec, prereleases=prerelease)
    else:
        releases = searcher.latest_minor_binaries(spec, prereleases=prerelease)

    headings = ["Python Version", "URL"]

    if releases:
        max_url_len = max(
            len(headings[1]), max(len(release.url) for release in releases)
        )
        headings_str = f"| {headings[0]} | {headings[1]:<{max_url_len}s} |"

        print(headings_str)
        print(f"| {'-' * len(headings[0])} | {'-' * max_url_len} |")

        for release in releases:
            print(f"| {release.version:>14s} | {release.url:<{max_url_len}s} |")
    else:
        print("No Python releases found matching specification")


def main() -> int:
    if sys.version_info < (3, 10):
        v = sys.version_info
        raise UnsupportedPythonError(
            f"Python {v.major}.{v.minor}.{v.micro} is not supported. "
            f"ducktools.pythonfinder requires Python 3.10 or later."
        )

    if sys.argv[1:]:
        parser = get_parser()
        vals = parser.parse_args(sys.argv[1:])

        if vals.command == "clear-cache":
            purge_caches()
        elif vals.command == "online":
            system = vals.system if vals.system else _laz.platform.system()
            machine = vals.machine if vals.machine else _laz.platform.machine()
            try:
                display_remote_binaries(
                    vals.min,
                    vals.max,
                    vals.compatible,
                    vals.all_binaries,
                    system,
                    machine,
                    vals.prerelease,
                )
            except _laz.URLError:
                print("Could not connect to python.org")
        else:
            display_local_installs(
                min_ver=vals.min,
                max_ver=vals.max,
                compatible=vals.compatible,
            )
    else:
        # No arguments to parse
        display_local_installs()

    stop_autoclose()

    return 0


if __name__ == "__main__":
    sys.exit(main())
