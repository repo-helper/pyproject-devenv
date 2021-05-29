#!/usr/bin/env python3
#
#  __main__.py
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
import sys

# 3rd party
import click
from consolekit import click_command
from consolekit.options import DescribedArgument, colour_option, flag_option, verbose_option, version_option
from consolekit.terminal_colours import ColourTrilean, Fore, resolve_color_default
from consolekit.tracebacks import handle_tracebacks, traceback_option
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike

__all__ = ["main", "version_callback"]


def version_callback(ctx: click.Context, param: click.Option, value: int):  # noqa: D103
	if not value or ctx.resilient_parsing:
		return

	# 3rd party
	import virtualenv  # type: ignore
	from domdf_python_tools.stringlist import DelimitedList

	# this package
	import pyproject_devenv

	parts = DelimitedList([f"pyproject-devenv version {pyproject_devenv.__version__}"])

	if value > 1:
		parts.append(f"virualenv {virtualenv.__version__}")

	click.echo(f"{parts:, }", color=ctx.color)
	ctx.exit()


@version_option(callback=version_callback)
@traceback_option()
@colour_option()
@verbose_option()
@flag_option(
		"-U",
		"--upgrade",
		help="Upgrade all specified packages to the newest available version.",
		)
@click.argument(
		"dest",
		type=click.STRING,
		default="venv",
		cls=DescribedArgument,
		description="The directory to create the virtual environment in."
		)
@click_command()
def main(
		dest: PathLike = "venv",
		verbose: int = 0,
		colour: ColourTrilean = None,
		show_traceback: bool = False,
		upgrade: bool = False,
		):
	"""
	Create virtual environments using pyproject.toml metadata.
	"""

	# this package
	from pyproject_devenv import mkdevenv
	from pyproject_devenv.config import ConfigTracebackHandler

	with handle_tracebacks(show_traceback, ConfigTracebackHandler):
		ret = mkdevenv(PathPlus.cwd(), dest, verbosity=verbose, upgrade=upgrade)

		if ret:
			sys.exit(ret)  # pragma: no cover
		else:
			click.echo(
					Fore.GREEN("Successfully created development virtualenv."),
					color=resolve_color_default(colour),
					)


if __name__ == "__main__":
	sys.exit(main())
