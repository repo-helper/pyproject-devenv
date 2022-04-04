# stdlib
import sys
from typing import Dict

# 3rd party
import pytest
from domdf_python_tools.compat import PYPY, PYPY38
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.utils import strtobool
from shippinglabel import read_pyvenv

# this package
from pyproject_devenv import __version__, mkdevenv


@pytest.mark.parametrize("verbosity", [0, 1, 2])
def test_mkdevenv(tmp_pathplus: PathPlus, capsys, verbosity: int):
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

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=verbosity, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
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
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_mkdevenv_extras(tmp_pathplus: PathPlus, capsys):
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
			'',
			"[project.optional-dependencies]",
			"doc = ['sphinx']",
			'',
			])
	(tmp_pathplus / "requirements.txt").write_lines(lib_requirements)

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=2, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err
	assert "Installing extra 'doc'" in capout.out

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
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

		assert (version_dir / "site-packages" / "sphinx").is_dir()

	assert len(version_dirs) == 1

	pyvenv_config: Dict[str, str] = read_pyvenv(venv_dir)

	assert "prompt" in pyvenv_config
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_mkdevenv_no_build_deps(tmp_pathplus: PathPlus, capsys):
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
			"[project]",
			"name = 'pyproject-devenv-demo'",
			"dynamic = ['dependencies']",
			'',
			"[project.optional-dependencies]",
			"doc = ['sphinx']",
			'',
			])
	(tmp_pathplus / "requirements.txt").write_lines(lib_requirements)

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=2, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err
	assert "Installing build requirements" not in capout.out

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
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
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_mkdevenv_no_lib_deps(tmp_pathplus: PathPlus, capsys):

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
			f"dependencies = []",
			])

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=1, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err
	assert "Installing library requirements" not in capout.out

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
		version_dirs = [venv_dir]
	elif sys.platform == "win32":
		version_dirs = [(venv_dir / "Lib")]
	else:
		version_dirs = list((venv_dir / "lib").glob("py*"))

	for version_dir in version_dirs:
		for package in test_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

	assert len(version_dirs) == 1

	pyvenv_config: Dict[str, str] = read_pyvenv(venv_dir)

	assert "prompt" in pyvenv_config
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_mkdevenv_no_lib_deps_dynamic(tmp_pathplus: PathPlus, capsys):
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
	(tmp_pathplus / "requirements.txt").touch()

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=1, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err
	assert "Installing library requirements" not in capout.out

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
		version_dirs = [venv_dir]
	elif sys.platform == "win32":
		version_dirs = [(venv_dir / "Lib")]
	else:
		version_dirs = list((venv_dir / "lib").glob("py*"))

	for version_dir in version_dirs:
		for package in test_requirements:
			assert (version_dir / "site-packages" / package).is_dir()

	assert len(version_dirs) == 1

	pyvenv_config: Dict[str, str] = read_pyvenv(venv_dir)

	assert "prompt" in pyvenv_config
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])


def test_mkdevenv_no_dynamic(tmp_pathplus: PathPlus, capsys):
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
			f"dependencies = {lib_requirements!r}",
			'',
			])

	(tmp_pathplus / "tests").mkdir()
	(tmp_pathplus / "tests/requirements.txt").write_lines(test_requirements)

	assert mkdevenv(tmp_pathplus, tmp_pathplus / "venv", verbosity=2, upgrade=False) == 0

	capout = capsys.readouterr()
	assert not capout.err

	# Check list of packages in virtualenv
	venv_dir = tmp_pathplus / "venv"

	if PYPY and not sys.version_info >= (3, 8):
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
	assert pyvenv_config["prompt"] == "pyproject-devenv-demo"

	assert "pyproject-devenv" in pyvenv_config
	assert pyvenv_config["pyproject-devenv"] == __version__

	assert "virtualenv" in pyvenv_config

	assert "include-system-site-packages" in pyvenv_config
	assert not strtobool(pyvenv_config["include-system-site-packages"])
