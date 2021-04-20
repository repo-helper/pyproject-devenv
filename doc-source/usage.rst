=======
Usage
=======

``pyproject-devenv`` creates a `virtualenv`_ using metadata defined in ``pyproject.toml``.

.. _virtualenv: https://virtualenv.pypa.io/en/latest/

Configuration
---------------

``pyproject-devenv`` is configured using the ``project`` table in ``pyproject.toml``, as defined in :pep:`621`.
At a minimum, a value must be provided for name_, and dependencies_ have a value or be marked as dynamic_. A value can also be provided for `optional-dependencies`_, but this cannot be dynamic.
Any requirements listed in dependencies_ or `optional-dependencies`_ are installed.

.. _name: https://www.python.org/dev/peps/pep-0621/#name
.. _dependencies: https://www.python.org/dev/peps/pep-0621/#dependencies-optional-dependencies
.. _optional-dependencies: https://www.python.org/dev/peps/pep-0621/#dependencies-optional-dependencies
.. _dynamic: https://www.python.org/dev/peps/pep-0621/#dynamic

``pyproject-devenv`` will also install anything listed in ``build-system.requires``,
which lists the project's build dependencies. Refer to :pep:`518` for more information on the ``[build-system]`` table.

If the file ``<pyproject_dir>/tests/requirements.txt`` exists, any requirements listed in that file are installed.

.. TODO::

	Config options for which extras to install and the test directory.

Command Line Usage
-------------------

.. click:: pyproject_devenv.__main__:main
	:prog: devenv
	:nested: none
