# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from packaging.requirements import Requirement
from shippinglabel.requirements import ComparableRequirement

# this package
from pyproject_devenv import InstallError, InstallFromFileError


def test_InstallFromFileError():
	with pytest.raises(InstallFromFileError, match="Could not install from 'requirements.txt'"):
		raise InstallFromFileError("requirements.txt")

	with pytest.raises(InstallFromFileError, match="Could not install from 'requirements.txt'"):
		raise InstallFromFileError(PathPlus("requirements.txt"))

	with pytest.raises(InstallFromFileError, match="Could not install from 'tests/requirements.txt'"):
		raise InstallFromFileError(PathPlus("tests") / "requirements.txt")


def test_InstallError():
	with pytest.raises(
			InstallError,
			match="Could not install the given requirements: 'pytest', 'flake8', 'black' and 'pip'",
			):
		raise InstallError("pytest", "flake8", "black", "pip")

	with pytest.raises(
			InstallError,
			match="Could not install the given requirements: 'pytest', 'flake8', 'black' and 'pip'",
			):
		raise InstallError(
				ComparableRequirement("pytest"),
				ComparableRequirement("flake8"),
				ComparableRequirement("black"),
				ComparableRequirement("pip")
				)

	with pytest.raises(
			InstallError,
			match="Could not install the given requirements: 'pytest', 'flake8', 'black' and 'pip'",
			):
		raise InstallError(Requirement("pytest"), Requirement("flake8"), Requirement("black"), Requirement("pip"))

	with pytest.raises(
			InstallError,
			match="Could not install the given requirements: 'pytest', 'flake8', 'black' and 'pip'",
			):
		raise InstallError(ComparableRequirement("pytest"), Requirement("flake8"), "black", Requirement("pip"))
