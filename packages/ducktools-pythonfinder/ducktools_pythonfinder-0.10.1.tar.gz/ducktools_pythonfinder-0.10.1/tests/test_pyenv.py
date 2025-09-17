# ducktools-pythonfinder
# MIT License
#
# Copyright (c) 2023-2024 David C Ellis
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

import sys
import os
import os.path
import textwrap
import types
from pathlib import Path

import pytest
from unittest.mock import patch, Mock

from ducktools.pythonfinder.shared import PythonInstall, DetailFinder
from ducktools.pythonfinder import details_script

if sys.platform == "win32":
    from ducktools.pythonfinder.win32.pyenv_search import (
        get_pyenv_pythons,
        get_pyenv_root,
    )
else:
    from ducktools.pythonfinder.linux.pyenv_search import (
        get_pyenv_pythons,
        get_pyenv_root,
    )


details_text = Path(details_script.__file__).read_text()


def test_get_pyenv_root_env():
    fake_path = "path/to/pyenv"
    with patch.dict(os.environ, {"PYENV_ROOT": fake_path}):
        assert get_pyenv_root() == fake_path


@pytest.mark.skipif(sys.platform == "win32", reason="Test for non-Windows only")
def test_get_pyenv_root_backup():
    with patch.dict(os.environ) as patched:
        if "PYENV_ROOT" in patched:
            del patched["PYENV_ROOT"]

        from ducktools.pythonfinder.linux.pyenv_search import _laz
        with patch.object(_laz, "run") as run_mock:
            run_mock.return_value = types.SimpleNamespace(stdout="path/to/pyenv\n")
            pyenv_root = get_pyenv_root()
            run_mock.assert_called_with(["pyenv", "root"], text=True, capture_output=True)

    assert pyenv_root == "path/to/pyenv"


def test_no_versions_folder(temp_finder):
    with patch("os.path.exists") as exists_mock:
        exists_mock.return_value = False
        assert list(get_pyenv_pythons(finder=temp_finder)) == []


def test_mock_versions_folder(temp_finder):
    mock_dir_entry = Mock(os.DirEntry)

    out_ver = "3.12.1"
    if sys.platform == "win32":
        versions_folder = os.path.join("c:", "fake", "versions")
        out_executable = os.path.join(versions_folder, out_ver, "python.exe")
    else:
        versions_folder = "~/fake/versions"
        out_executable = os.path.join(versions_folder, out_ver, "bin/python")

    mock_dir_entry.name = out_ver
    mock_dir_entry.path = os.path.join(versions_folder, out_ver)

    with patch("os.path.exists") as exists_mock, \
            patch("os.scandir") as scandir_mock, \
            patch.object(DetailFinder, "get_install_details") as details_mock:

        assert os.path.exists is exists_mock

        return_val = PythonInstall.from_str(version=out_ver, executable=out_executable, managed_by="pyenv")
        details_mock.return_value = return_val

        def false_on_venv_check(pth):
            # Need to return False on the venv check, but True on all other exists checks
            return False if pth.endswith("pyvenv.cfg") else True

        exists_mock.side_effect = false_on_venv_check
        scandir_mock.return_value = iter([mock_dir_entry])

        python_versions = list(get_pyenv_pythons(versions_folder=versions_folder, finder=temp_finder))

        details_mock.assert_called_once_with(out_executable, managed_by="pyenv")

    assert python_versions == [return_val]


def test_mock_folder_skip_venv(temp_finder):
    # If the venv check returns true, make sure the folder is skipped
    mock_dir_entry = Mock(os.DirEntry)

    out_ver = "3.12.1"
    if sys.platform == "win32":
        versions_folder = os.path.join("c:", "fake", "versions")
        out_executable = os.path.join(versions_folder, out_ver, "python.exe")
    else:
        versions_folder = "~/fake/versions"
        out_executable = os.path.join(versions_folder, out_ver, "bin/python")

    mock_dir_entry.name = out_ver
    mock_dir_entry.path = os.path.join(versions_folder, out_ver)

    with patch("os.path.exists") as exists_mock, \
            patch("os.scandir") as scandir_mock, \
            patch.object(DetailFinder, "get_install_details") as details_mock:

        assert os.path.exists is exists_mock

        return_val = PythonInstall.from_str(version=out_ver, executable=out_executable, managed_by="pyenv")
        details_mock.return_value = return_val

        exists_mock.return_value = True
        scandir_mock.return_value = iter([mock_dir_entry])

        python_versions = list(get_pyenv_pythons(versions_folder=versions_folder, finder=temp_finder))

        details_mock.assert_not_called()

    assert python_versions == []


@pytest.mark.skipif(sys.platform != "win32", reason="Test for Windows only")
def test_fs_versions_win(fs, temp_finder):
    # Test with folders in fake file system

    tmpdir = "c:\\fake_folder"

    py_folder = os.path.join(tmpdir, "3.12.1")
    py_exe = os.path.join(py_folder, "python.exe")

    fs.create_dir(py_folder)
    fs.create_file(py_exe)

    with patch.object(DetailFinder, "get_install_details") as details_mock:
        return_val = PythonInstall.from_str(version="3.12.1", executable=py_exe, managed_by="pyenv")
        details_mock.return_value = return_val
        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))

        details_mock.assert_called_once_with(py_exe, managed_by="pyenv")

        assert versions == [return_val]

        # Check presence of a 'pyvenv.cfg' ignores the folder
        details_mock.reset_mock()
        fs.create_file(os.path.join(py_folder, "pyvenv.cfg"))

        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))
        details_mock.assert_not_called()
        assert versions == []


@pytest.mark.skipif(sys.platform == "win32", reason="Test for non-Windows only")
def test_fs_versions_nix(fs, temp_finder):
    # Test folders in fake file system

    tmpdir = "~/.pyenv/versions"

    py_folder = os.path.join(tmpdir, "3.12.1")
    py_exe = os.path.join(py_folder, "bin/python")

    fs.create_dir(py_folder)
    fs.create_dir(os.path.join(py_folder, "bin"))
    fs.create_file(py_exe)

    with patch.object(DetailFinder, "get_install_details") as details_mock:
        return_val = PythonInstall.from_str(version="3.12.1", executable=py_exe, managed_by="pyenv")
        details_mock.return_value = return_val

        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))
        details_mock.assert_called_once_with(py_exe, managed_by="pyenv")

        assert versions == [return_val]

        details_mock.reset_mock()

        # Test the same folder is ignored if a 'pyvenv.cfg' file is discovered
        fs.create_file(os.path.join(py_folder, "pyvenv.cfg"))
        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))
        details_mock.assert_not_called()
        assert versions == []


@pytest.mark.skipif(sys.platform == "win32", reason="Test for non-Windows only")
def test_invalid_ver_nix(fs, uses_details_script, temp_finder):
    # Test folders in fake file system

    tmpdir = "~/.pyenv/versions"

    py_folder = os.path.join(tmpdir, "external-python3.12.1")
    py_exe = os.path.join(py_folder, "bin/python")

    fs.create_dir(py_folder)
    fs.create_dir(os.path.join(py_folder, "bin"))
    fs.create_file(py_exe)

    py2_folder = os.path.join(tmpdir, "ext3.13.0")
    py2_exe = os.path.join(py2_folder, "bin/python")

    fs.create_dir(py2_folder)
    fs.create_dir(os.path.join(py2_folder, "bin"))
    fs.create_file(py2_exe)

    py3_folder = os.path.join(tmpdir, "invalid-version-3.12.1")
    py3_exe = os.path.join(py3_folder, "bin/python")

    fs.create_dir(py3_folder)
    fs.create_dir(os.path.join(py3_folder, "bin"))
    fs.create_file(py3_exe)

    with patch("subprocess.run") as run_mock:
        run_mock.side_effect = OSError("Failure")
        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))
        assert run_mock.call_count == 3

    assert versions == []


@pytest.mark.skipif(sys.platform == "win32", reason="Test for non-Windows only")
def test_pypy_version(fs, temp_finder):
    # Test pypy version retrieval

    ver_folder = "pypy3.10-7.3.15"
    tmpdir = os.path.expanduser("~/.pyenv/versions")

    mock_output = textwrap.dedent(
        """
        {"version": [3, 10, 13, "final", 0],
        "executable": "~/.pyenv/versions/pypy3.10-7.3.15/bin/pypy",
        "architecture": "64bit",
        "implementation": "pypy",
        "metadata": {"pypy_version": [7, 3, 15, "final", 0]}}
        """
    ).strip()

    py_folder = os.path.join(tmpdir, ver_folder)
    py_exe = os.path.join(py_folder, "bin/python")

    fs.add_real_file(details_script.__file__)
    fs.create_dir(py_folder)
    fs.create_dir(os.path.join(py_folder, "bin"))
    fs.create_file(py_exe)

    with patch("subprocess.run") as run_cmd:
        run_cmd.return_value.stdout = mock_output
        versions = list(get_pyenv_pythons(tmpdir, finder=temp_finder))

        run_cmd.assert_called_once_with(
            [os.path.abspath(py_exe), "-"],
            input=details_text,
            capture_output=True,
            text=True,
            check=True,
        )

        out_version = PythonInstall(
            version=(3, 10, 13, "final", 0),
            executable="~/.pyenv/versions/pypy3.10-7.3.15/bin/pypy",
            architecture="64bit",
            implementation="pypy",
            metadata={"pypy_version": (7, 3, 15, "final", 0)},
            managed_by="pyenv",
        )

        assert versions == [out_version]
