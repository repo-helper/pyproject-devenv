============
Public API
============

Create virtual environments using ``pyproject.toml`` metadata.

.. autosummary-widths:: 6/16
	:html: 4/10

.. automodulesumm:: pyproject_devenv
	:autosummary-sections: Exceptions

.. latex:vspace:: -10px
.. autosummary-widths:: 1/2
	:html: 5/10

.. automodulesumm:: pyproject_devenv
	:autosummary-sections: Functions

.. automodule:: pyproject_devenv
	:no-autosummary:
	:no-docstring:
	:member-order: bysource

.. latex:vspace:: -10px


:mod:`pyproject_devenv.config`
---------------------------------

.. autosummary-widths:: 11/32
	:html: 3/10

.. py:currentmodule:: pyproject_devenv.config
.. automodule:: pyproject_devenv.config
	:no-members:
	:autosummary-members:

.. autofunction:: pyproject_devenv.config.load_toml

.. class:: ConfigTracebackHandler

	Bases: :class:`pyproject_parser.cli.ConfigTracebackHandler`

	.. raw:: latex

		\begin{flushleft}

	:class:`consolekit.tracebacks.TracebackHandler` which handles
	:exc:`dom_toml.parser.BadConfigError` and :exc:`~.BaseInstallError`.

	.. raw:: latex

		\end{flushleft}

.. autotypeddict:: pyproject_devenv.config.ConfigDict

.. autoclass:: pyproject_devenv.config.PEP621Parser
	:no-autosummary:
