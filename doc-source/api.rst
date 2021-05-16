============
Public API
============

.. automodule:: pyproject_devenv

:mod:`pyproject_devenv.config`
---------------------------------

.. automodule:: pyproject_devenv.config
	:no-members:
	:autosummary-members:

.. autofunction:: pyproject_devenv.config.load_toml

.. class:: pyproject_devenv.config.ConfigTracebackHandler

	Bases: :class:`pyproject_parser.cli.ConfigTracebackHandler`

	.. raw:: latex

		\begin{flushleft}

	:class:`consolekit.tracebacks.TracebackHandler` which handles
	:exc:`dom_toml.parser.BadConfigError` and :exc:`~.BaseInstallError`.

	.. raw:: latex

		\end{flushleft}

.. autotypeddict:: pyproject_devenv.config.ConfigDict

.. clearpage::

.. autoclass:: pyproject_devenv.config.PEP621Parser
	:no-autosummary:
