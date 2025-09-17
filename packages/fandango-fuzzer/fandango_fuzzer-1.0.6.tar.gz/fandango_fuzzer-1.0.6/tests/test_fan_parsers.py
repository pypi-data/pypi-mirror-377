#!/usr/bin/env pytest

import glob
import unittest

import pytest

from .utils import RESOURCES_ROOT, DOCS_ROOT, run_command


files = glob.glob(str(RESOURCES_ROOT / "*.fan")) + glob.glob(str(DOCS_ROOT / "*.fan"))


@pytest.mark.parametrize("fan_file", files)
def test_file(fan_file):
    """Test the C++ and python .fan parsers for `fan_file`."""

    command = ["fandango", "-v", "--parser=python", "convert", fan_file]
    python_out, err, return_code = run_command(command)
    assert return_code == 0, err
    assert err == ""

    command = ["fandango", "--parser=cpp", "convert", fan_file]
    cpp_out, err, return_code = run_command(command)
    assert return_code == 0, err
    assert err == ""

    assert (
        python_out == cpp_out
    ), f"{fan_file} produced different outputs for Python and C++ parsers:\n\nPython output:\n{python_out}\n\nC++ output:\n{cpp_out}"


if __name__ == "__main__":
    unittest.main()
