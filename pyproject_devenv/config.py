#!/usr/bin/env python3
#
#  config.py
"""
Read the ``pyproject-devenv`` config from ``pyproject.toml``.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, TypeVar, cast

# 3rd party
import pyproject_parser.cli
from consolekit.utils import abort
from dom_toml.parser import TOML_TYPES, BadConfigError
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from pyproject_parser.type_hints import ProjectDict
from shippinglabel.requirements import combine_requirements, read_requirements

if TYPE_CHECKING:
	# this package
	from pyproject_devenv import BaseInstallError

__all__ = [
		"DevenvConfig",
		"PEP621Parser",
		"load_toml",
		"ConfigTracebackHandler",
		]


class PEP621Parser(pyproject_parser.parsers.PEP621Parser):
	keys: List[str] = [
			"name",
			"dependencies",
			"optional-dependencies",
			]

	defaults: ClassVar[Dict[str, Any]] = {}
	factories: ClassVar[Dict[str, Callable[..., Any]]] = {
			"dependencies": list,
			"optional-dependencies": dict,
			}

	def parse(  # type: ignore[override]
		self,
		config: Dict[str, TOML_TYPES],
		set_defaults: bool = False,
		) -> ProjectDict:
		"""
		Parse the TOML configuration.

		:param config:
		:param set_defaults: If :py:obj:`True`, the values in
			:attr:`dom_toml.parser.AbstractConfigParser.defaults` and
			:attr:`dom_toml.parser.AbstractConfigParser.factories`
			will be set as defaults for the returned mapping.
		"""

		dynamic_fields = config.get("dynamic", [])

		if "name" in dynamic_fields:
			raise BadConfigError("The 'project.name' field may not be dynamic.")
		elif "name" not in config:
			raise BadConfigError("The 'project.name' field must be provided.")

		if "dependencies" not in config and "dependencies" not in dynamic_fields:
			raise BadConfigError("The 'project.dependencies' field must be provided or marked as 'dynamic'.")

		if "optional-dependencies" not in config and "optional-dependencies" in dynamic_fields:
			raise BadConfigError("The '[project.optional-dependencies]' table may not be dynamic.")

		parsed_config = {"dynamic": dynamic_fields}
		parsed_config.update(super().parse(config, set_defaults))
		return cast(ProjectDict, parsed_config)


_PP = TypeVar("_PP", bound=pyproject_parser.PyProject)


class DevenvConfig(pyproject_parser.PyProject):
	project_table_parser = PEP621Parser()

	def read_dynamic_dependencies(self, project_dir: PathLike):
		if self.project is None:
			raise BadConfigError(f"The '[project]' table was not found in 'pyproject.toml'")

		project_dir = PathPlus(project_dir)

		dynamic = list(self.project["dynamic"])

		if "dependencies" in dynamic:
			if (project_dir / "requirements.txt").is_file():
				dependencies = read_requirements(project_dir / "requirements.txt", include_invalid=True)[0]
				self.project["dependencies"] = sorted(combine_requirements(dependencies))
			else:
				raise BadConfigError(
						"'project.dependencies' was listed as a dynamic field "
						"but no 'requirements.txt' file was found."
						)


def load_toml(filename: PathLike) -> DevenvConfig:  # TODO: TypedDict
	"""
	Load the ``mkrecipe`` configuration mapping from the given TOML file.

	:param filename:
	"""

	filename = PathPlus(filename)

	devenv_config = DevenvConfig.load(filename, set_defaults=True)

	if devenv_config.project is None:
		raise BadConfigError(f"The '[project]' table was not found in {str(filename)!r}")

	devenv_config.read_dynamic_dependencies(filename.parent)

	return devenv_config


class ConfigTracebackHandler(pyproject_parser.cli.ConfigTracebackHandler):
	"""
	:class:`consolekit.tracebacks.TracebackHandler` which handles
	:exc:`dom_toml.parser.BadConfigError` and :exc:`~.BaseInstallError`.
	"""

	def handle_BaseInstallError(self, e: "BaseInstallError") -> bool:  # noqa: D102
		raise abort(f"Error: {e}", colour=False)
