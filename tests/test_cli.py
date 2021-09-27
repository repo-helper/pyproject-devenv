# stdlib
import re
import sys
from typing import Dict

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.compat import PYPY
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.utils import strtobool
from shippinglabel import read_pyvenv

# this package
from pyproject_devenv import __version__
from pyproject_devenv.__main__ import main


def test_mkdevenv(tmp_pathplus: PathPlus):
	lib_requirements = [
			"click",
			"flask",
			"werkzeug",
			"consolekit",
			"requests",
			"apeye",
			]

	test_requirements = [
			"pytest",
			"hypothesis",
			]

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = ["setuptools", "wheel"]',
			'',
			"[project]",
			"name = 'pyproject-devenv-demo'",
			"dynamic = ['dependencies']",
			])
	(tmp_pathplus / "requirements.txt").write_lines(lib_requirements)

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main)
		assert result.exit_code == 0
		assert result.stdout == 'Successfully created development virtualenv.\n'

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY:
		version_dirs = [venv_dir]
	elif sys.platform == "win32":
		version_dirs = [(venv_dir / "Lib")]
	else:
		version_dirs = list((venv_dir / "lib").glob("py*"))

	for version_dir in version_dirs:

		for package in lib_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

		for package in test_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

	assert len(version_dirs) == 1

	pyvenv_config: Dict[str, str] = read_pyvenv(venv_dir)

	assert "prompt" in pyvenv_config
	assert pyvenv_config["prompt"] == "(pyproject-devenv-demo) "

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


@pytest.mark.parametrize(
		"extra_args",
		[
				pytest.param(("--verbose", ), id="verbose"),
				pytest.param(("--verbose", "--verbose"), id="very verbose"),
				pytest.param(("-v", ), id="verbose short"),
				pytest.param(("-v", "--verbose"), id="very verbose short"),
				pytest.param(("-vv", ), id="very verbose short short"),
				pytest.param(("--verbose", "--upgrade"), id="verbose upgrade"),
				pytest.param(("-vU", ), id="verbose short upgrade short"),
				]
		)
def test_mkdevenv_verbose(tmp_pathplus: PathPlus, extra_args):
	lib_requirements = [
			"click",
			"flask",
			"werkzeug",
			"consolekit",
			"requests",
			"apeye",
			]

	test_requirements = [
			"pytest",
			"hypothesis",
			]

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = ["setuptools", "wheel"]',
			'',
			"[project]",
			"name = 'pyproject-devenv-demo'",
			"dynamic = ['dependencies']",
			])
	(tmp_pathplus / "requirements.txt").write_lines(lib_requirements)

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main, extra_args)
		assert result.exit_code == 0

	assert " Installing project requirements " in result.stdout
	assert " Installing test requirements " in result.stdout
	assert " Installing build requirements " in result.stdout
	assert "Successfully created development virtualenv." in result.stdout

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY:
		version_dirs = [venv_dir]
	elif sys.platform == "win32":
		version_dirs = [(venv_dir / "Lib")]
	else:
		version_dirs = list((venv_dir / "lib").glob("py*"))

	for version_dir in version_dirs:

		for package in lib_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

		for package in test_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

	assert len(version_dirs) == 1

	pyvenv_config: Dict[str, str] = read_pyvenv(venv_dir)

	assert "prompt" in pyvenv_config
	assert pyvenv_config["prompt"] == "(pyproject-devenv-demo) "

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_version(tmp_pathplus):

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main, args=["--version"])
		assert result.exit_code == 0

	assert result.stdout == f"pyproject-devenv version {__version__}\n"


def test_version_version(tmp_pathplus):

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main, args=["--version", "--version"])
		assert result.exit_code == 0

	assert re.match(
			rf"pyproject-devenv version {re.escape(__version__)}, virualenv \d+\.\d+\.\d+\n",
			result.stdout,
			)
