#!/usr/bin/env python3
#
#  __init__.py
"""
Create virtual environments using ``pyproject.toml`` metadata.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import os
import pathlib
import shutil
from typing import Dict, List, Optional, Union

# 3rd party
import click
import virtualenv  # type: ignore
from domdf_python_tools.paths import PathPlus, traverse_to_file
from domdf_python_tools.typing import PathLike
from domdf_python_tools.words import word_join
from packaging.requirements import Requirement
from shippinglabel import read_pyvenv
from virtualenv.run import session_via_cli  # type: ignore
from virtualenv.run.session import Session  # type: ignore
from virtualenv.seed.wheels import pip_wheel_env_run  # type: ignore

# this package
from pyproject_devenv.config import ConfigDict, load_toml

__all__ = ["mkdevenv", "BaseInstallError", "InstallFromFileError", "InstallError"]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.2"
__email__: str = "dominic@davis-foster.co.uk"

virtualenv_version = tuple(map(int, virtualenv.__version__.split('.')))

if virtualenv_version >= (20, 4):
	_pip_wheel_env_run = pip_wheel_env_run

	def pip_wheel_env_run(search_dirs, app_data):
		return _pip_wheel_env_run(search_dirs, app_data, os.environ)


class BaseInstallError(RuntimeError):
	"""
	Base :exc:`Exception` to indicate an error occurred when installing packages.
	"""


class InstallFromFileError(BaseInstallError):
	"""
	:exc:`Exception` to indicate an error occurred when installing packages from a requirements file.

	:param filename: The file listing the packages to install.
	"""

	def __init__(self, filename: PathLike):
		if not isinstance(filename, pathlib.Path):
			filename = PathPlus(filename)

		self.filename: str = filename.as_posix()
		"""
		The file listing the packages to install.

		.. latex:clearpage::
		"""

		super().__init__(f"Could not install from {self.filename!r}")


class InstallError(BaseInstallError):
	r"""
	:exc:`Exception` to indicate an error occurred when installing packages.

	:param \*requirements: The requirements being installed.
	"""

	def __init__(self, *requirements: Union[str, Requirement]):
		#: The requirements being installed.
		self.requirements: List[str] = list(map(str, requirements))

		requirements_string = word_join(self.requirements, use_repr=True)
		super().__init__(f"Could not install the given requirements: {requirements_string}")


class _Devenv:
	"""
	Create a "devenv".

	.. TODO:: Maybe make this public at some point?

	:param project_dir: The root of the project to create the devenv for.
	:param venv_dir: The directory to create the devenv in, relative to ``repo_dir``.
	:param verbosity: The verbosity of the function. ``0`` = quiet, ``2`` = very verbose.
	:param upgrade: Whether to upgrade all specified packages to the newest available version.
	"""

	def __init__(
			self,
			project_dir: PathLike,
			venv_dir: PathLike = "venv",
			*,
			verbosity: int = 1,
			upgrade: bool = False,
			):
		self.project_dir: PathPlus = self.determine_project_dir(project_dir)
		self.config: ConfigDict = self.load_config()
		self.venv_dir = self.project_dir / venv_dir
		self.verbosity: int = int(verbosity)
		self.upgrade: bool = upgrade

		# TODO: config option
		self.extras_to_install = sorted(self.config["optional_dependencies"])

	@staticmethod
	def determine_project_dir(project_dir: PathLike) -> PathPlus:
		"""
		Determine the project base directory.

		Subclasses may override this method to customise the behaviour.

		:param project_dir:
		"""

		return traverse_to_file(PathPlus(project_dir), "pyproject.toml")

	def load_config(self) -> ConfigDict:
		"""
		Load the configuration.

		Subclasses may override this method to customise the behaviour.
		"""

		return load_toml(self.project_dir / "pyproject.toml")

	def create(self) -> int:

		args = [
				str(self.venv_dir),
				"--prompt",
				f"{self.config['name']}",
				"--seeder",
				"pip",
				"--download",
				]

		if self.verbosity:
			args.append("--verbose")
		if self.verbosity >= 2:
			args.append("--verbose")

		of_session = session_via_cli(args)

		if not of_session.seeder.enabled:  # pragma: no cover
			return 1

		with of_session:
			of_session.run()

		self.install_project_requirements(of_session)

		self.install_extra_requirements(of_session)

		# TODO: config option for tests dir
		if (self.project_dir / "tests" / "requirements.txt").is_file():
			self.install_test_requirements(of_session)

		self.install_build_requirements(of_session)

		if self.verbosity:
			click.echo()

		self.update_pyvenv()

		return 0

	def install_project_requirements(self, of_session):
		"""
		Install the project's requirements/dependencies.

		:param of_session:
		"""

		if self.config["dependencies"]:
			self.report_installing("project requirements")

			self.install_requirements(
					of_session,
					*self.config["dependencies"],
					)

	def install_extra_requirements(self, of_session):
		"""
		Install the project's extra-requirements/optional-dependencies.

		:param of_session:
		"""

		for extra in self.extras_to_install:
			self.report_installing(f"extra {extra!r}")

			self.install_requirements(
					of_session,
					*self.config["optional_dependencies"][extra],
					)

	def install_test_requirements(self, of_session):
		"""
		Install the project's test requirements.

		:param of_session:
		"""

		self.report_installing("test requirements")

		self.install_requirements(
				of_session,
				requirements_file=self.project_dir / "tests" / "requirements.txt",
				)

	def install_build_requirements(self, of_session):
		"""
		Install the project's build requirements.

		:param of_session:
		"""

		if self.config["build_dependencies"] is not None:
			self.report_installing("build requirements")

			self.install_requirements(
					of_session,
					*self.config["build_dependencies"],
					)

	def report_installing(self, what: str):
		"""
		Report that a category of requirements is being installed.

		:param what: The type/category of requirements to report the installation of,
			e.g. "library requirements".
		"""

		if self.verbosity:
			click.echo()
			click.echo(f" Installing {what.strip()} ".center(shutil.get_terminal_size().columns, '='))

	# @overload
	# def install_requirements(
	# 		self,
	# 		session: Session,
	# 		*requirements: Union[str, Requirement],
	# 		requirements_file: None = ...
	# 		): ...
	#
	# @overload
	# def install_requirements(
	# 		self,
	# 		session: Session,
	# 		requirements_file: PathLike,
	# 		): ...

	def install_requirements(
			self,
			session: Session,
			*requirements: Union[str, Requirement],
			requirements_file: Optional[PathLike] = None,
			):
		r"""
		Install requirements into a virtualenv.

		:param session:
		:param \*requirements: The requirements to install.
		:param requirements_file: The file to install the requirements from, with ``pip install -r <filename>``.

		``*requirements`` and ``requirements_file`` are mutually exclusive.
		"""

		if requirements and requirements_file:
			raise TypeError("'*requirements' and 'requirements_file' are mutually exclusive.")

		cmd = [
				session.creator.exe,
				"-m",
				"pip",
				"install",
				"--disable-pip-version-check",
				]

		if requirements_file:
			cmd.append("-r")
			cmd.append(str(requirements_file))
		else:
			cmd.extend(map(str, requirements))

		if self.verbosity < 1:
			cmd.append("--quiet")
		elif self.verbosity > 1:
			cmd.append("--verbose")

		if self.upgrade:
			cmd.append("--upgrade")

		try:
			session.seeder._execute(
					[str(x) for x in cmd],
					pip_wheel_env_run(session.seeder.extra_search_dir, session.seeder.app_data),
					)
		except RuntimeError:  # pragma: no cover
			if requirements_file:
				raise InstallFromFileError(requirements_file)
			else:
				raise InstallError(*requirements)

	def update_pyvenv(self) -> None:
		"""
		Read and update the ``pyvenv.cfg`` file of the virtualenv.
		"""

		pyvenv_config: Dict[str, str] = read_pyvenv(self.venv_dir)
		pyvenv_config["pyproject-devenv"] = __version__

		with (self.venv_dir / "pyvenv.cfg").open('w') as fp:
			for key, value in pyvenv_config.items():
				value = f" = " + str(value).replace('\n', '\n\t')
				fp.write(f"{key}{value}\n")


def mkdevenv(
		project_dir: PathLike,
		venv_dir: PathLike = "venv",
		*,
		verbosity: int = 1,
		upgrade: bool = False,
		) -> int:
	"""
	Create a "devenv".

	:param project_dir: The root of the project to create the devenv for.
	:param venv_dir: The directory to create the devenv in, relative to ``repo_dir``.
	:param verbosity: The verbosity of the function. ``0`` = quiet, ``2`` = very verbose.
	:param upgrade: Whether to upgrade all specified packages to the newest available version.
	"""

	return _Devenv(project_dir, venv_dir, verbosity=verbosity, upgrade=upgrade).create()
