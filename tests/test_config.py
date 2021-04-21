# stdlib
from typing import Dict

# 3rd party
import dom_toml
import pytest
from consolekit.testing import CliRunner, Result
from dom_toml.parser import BadConfigError
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from pyproject_devenv.__main__ import main
from pyproject_devenv.config import PEP621Parser, load_toml


def test_dynamic_name():
	with pytest.raises(BadConfigError, match="The 'project.name' field may not be dynamic."):
		PEP621Parser().parse({"dynamic": ["name"]})


def test_name_not_provided():
	with pytest.raises(BadConfigError, match="The 'project.name' field must be provided."):
		PEP621Parser().parse({})


def test_dependencies_not_provided():
	with pytest.raises(
			BadConfigError, match="The 'project.dependencies' field must be provided or marked as 'dynamic'."
			):
		PEP621Parser().parse({"name": "foo"})


def test_dynamic_optional_dependencies():
	with pytest.raises(BadConfigError, match=r"The '\[project.optional-dependencies\]' table may not be dynamic."):
		PEP621Parser().parse({"name": "foo", "dynamic": ["dependencies", "optional-dependencies"]})


def test_no_requirements_txt(tmp_pathplus: PathPlus):
	dom_toml.dump({"project": {"name": "foo", "dynamic": ["dependencies"]}}, tmp_pathplus / "pyproject.toml")

	with pytest.raises(
			BadConfigError,
			match="'project.dependencies' was listed as a dynamic field but no 'requirements.txt' file was found."
			):
		load_toml(tmp_pathplus / "pyproject.toml")


@pytest.mark.parametrize(
		"config, match",
		[
				pytest.param(
						{"dynamic": ["name"]},
						"The 'project.name' field may not be dynamic.",
						id="dynamic_name",
						),
				pytest.param({}, "The 'project.name' field must be provided.", id="no_name"),
				pytest.param(
						{"name": "foo", "dynamic": ["dependencies", "optional-dependencies"]},
						"The '[project.optional-dependencies]' table may not be dynamic.",
						id="dynamic_optional_dependencies",
						),
				pytest.param(
						{"name": "foo", "dynamic": ["dependencies"]},
						"'project.dependencies' was listed as a dynamic field "
						"but no 'requirements.txt' file was found.",
						id="no_requirements_txt",
						),
				]
		)
def test_bad_config_cli(tmp_pathplus: PathPlus, config: Dict, match: str):
	dom_toml.dump({"project": config}, tmp_pathplus / "pyproject.toml")

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main)
		assert result.exit_code == 1
		assert match in result.stdout


@pytest.mark.parametrize(
		"config, match",
		[
				pytest.param(
						{"dynamic": ["name"]},
						"The 'project.name' field may not be dynamic.",
						id="dynamic_name",
						),
				pytest.param({}, "The 'project.name' field must be provided.", id="no_name"),
				pytest.param(
						{"name": "foo", "dynamic": ["dependencies", "optional-dependencies"]},
						r"The '\[project.optional-dependencies\]' table may not be dynamic.",
						id="dynamic_optional_dependencies",
						),
				pytest.param(
						{"name": "foo", "dynamic": ["dependencies"]},
						"'project.dependencies' was listed as a dynamic field "
						"but no 'requirements.txt' file was found.",
						id="no_requirements_txt",
						),
				]
		)
def test_bad_config_cli_traceback(tmp_pathplus: PathPlus, config: Dict, match: str):
	dom_toml.dump({"project": config}, tmp_pathplus / "pyproject.toml")

	with in_directory(tmp_pathplus):
		runner = CliRunner()

		with pytest.raises(BadConfigError, match=match):
			runner.invoke(main, args=["-T"])
