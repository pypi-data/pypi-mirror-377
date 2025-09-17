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
import os.path
import sys
import sysconfig
import tempfile

from pathlib import Path

import pytest

from ducktools.pythonfinder import details_script
from ducktools.pythonfinder.shared import DetailFinder


@pytest.fixture(scope="session")
def sources_folder():
    return Path(__file__).parent / "sources"


@pytest.fixture
def uses_details_script(fs):
    fs.add_real_file(details_script.__file__)


@pytest.fixture(scope="function")
def temp_finder():
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_cache_path = os.path.join(tmpdir, "cache.json")
        finder = DetailFinder(cache_path=temp_cache_path)
        yield finder


@pytest.fixture(scope="function")
def this_python(temp_finder):
    config_exe = sysconfig.get_config_var("EXENAME")

    if config_exe:
        exename = os.path.basename(sysconfig.get_config_var("EXENAME"))
    elif sys.platform == "win32":
        exename = "python.exe"
    else:
        ver = ".".join(str(v) for v in sys.version_info[:2])
        exename = f"python{ver}"

    if sys.platform == "win32":
        py_exe = Path(sys.base_prefix) / exename
    else:
        py_exe = Path(sys.base_prefix) / "bin" / exename

    return temp_finder.query_install(str(py_exe))


@pytest.fixture(scope="function")
def this_venv(temp_finder):
    exe = sys.executable
    venv = temp_finder.query_install(exe)
    return venv


def pytest_addoption(parser):
    parser.addoption(
        "--run-uv-python",
        action="store_true",
        default=False,
        help="Run tests that involve installing UV pythons",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "uv_python: only run test if --run-uv-python is specified"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-uv-python"):
        skipper = pytest.mark.skip(reason="Only run when --run-uv-python is given")
        for item in items:
            if "uv_python" in item.keywords:
                item.add_marker(skipper)
