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
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, TypeVar, cast

# 3rd party
import pyproject_parser.cli
from consolekit.utils import abort
from dom_toml.parser import TOML_TYPES, BadConfigError
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from pyproject_parser.type_hints import ProjectDict
from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements
from typing_extensions import TypedDict

if TYPE_CHECKING:
	# this package
	from pyproject_devenv import BaseInstallError

__all__ = [
		"load_toml",
		"ConfigTracebackHandler",
		"ConfigDict",
		"PEP621Parser",
		]

_PP = TypeVar("_PP", bound=pyproject_parser.PyProject)


class PEP621Parser(pyproject_parser.parsers.PEP621Parser):
	"""
	Parser for a reduced subset of the :pep:`621` metadata from ``pyproject.toml``.
	"""

	#: The list of keys parsed from ``pyproject.toml``
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
			:attr:`self.defaults <dom_toml.parser.AbstractConfigParser.defaults>` and
			:attr:`self.factories <dom_toml.parser.AbstractConfigParser.factories>`
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


class _DevenvConfig(pyproject_parser.PyProject):
	"""
	Internal 'pyproject.toml' parser using the PEP621Parser class defined above.
	"""

	project_table_parser = PEP621Parser()


class ConfigDict(TypedDict):
	"""
	:class:`typing.TypedDict` representing the configuration returned by :func:`~.load_toml`.
	"""

	name: str
	dependencies: List[ComparableRequirement]
	optional_dependencies: Dict[str, List[ComparableRequirement]]
	build_dependencies: Optional[List[ComparableRequirement]]


def load_toml(filename: PathLike) -> ConfigDict:
	"""
	Load the ``pyproject-devenv`` configuration mapping from the given TOML file.

	:param filename:
	"""

	filename = PathPlus(filename)

	devenv_config = _DevenvConfig.load(filename, set_defaults=True)

	if devenv_config.project is None:
		raise BadConfigError(f"The '[project]' table was not found in {filename.as_posix()!r}")

	dynamic = set(devenv_config.project["dynamic"])
	project_dir = filename.parent

	if "dependencies" in dynamic:
		if (project_dir / "requirements.txt").is_file():
			dependencies = read_requirements(project_dir / "requirements.txt", include_invalid=True)[0]
			devenv_config.project["dependencies"] = sorted(combine_requirements(dependencies))
		else:
			raise BadConfigError(
					"'project.dependencies' was listed as a dynamic field "
					"but no 'requirements.txt' file was found."
					)

	if devenv_config.build_system is None:
		build_dependencies = None
	else:
		build_dependencies = devenv_config.build_system["requires"]

	return {
			"name": devenv_config.project["name"],
			"dependencies": devenv_config.project["dependencies"],
			"optional_dependencies": devenv_config.project["optional-dependencies"],
			"build_dependencies": build_dependencies,
			}


class ConfigTracebackHandler(pyproject_parser.cli.ConfigTracebackHandler):
	"""
	:class:`consolekit.tracebacks.TracebackHandler` which handles
	:exc:`dom_toml.parser.BadConfigError` and :exc:`~.BaseInstallError`.
	"""  # noqa: D400

	def handle_BaseInstallError(self, e: "BaseInstallError") -> bool:  # noqa: D102  # pragma: no cover
		raise abort(f"Error: {e}", colour=False)
