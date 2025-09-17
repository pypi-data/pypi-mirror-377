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

import itertools

try:
    from _collections_abc import Iterator
except ImportError:
    from collections.abc import Iterator

from ..shared import PythonInstall, get_uv_pythons, DetailFinder
from .pyenv_search import get_pyenv_pythons
from .registry_search import get_registered_pythons


def get_python_installs(
    *,
    finder: DetailFinder | None = None
) -> Iterator[PythonInstall]:
    listed_installs = set()

    finder = DetailFinder() if finder is None else finder

    with finder:
        for py in itertools.chain(
            get_registered_pythons(),
            get_pyenv_pythons(finder=finder),
            get_uv_pythons(finder=finder),
        ):
            if py.executable not in listed_installs:
                yield py
                listed_installs.add(py.executable)
