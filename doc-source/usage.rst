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

If the file ``<pyproject_dir>/tests/requirements.txt`` exists,
any requirements listed in that file are also installed.

.. TODO::

	Config options for which extras to install and the test directory.

Command Line Usage
-------------------

.. click:: pyproject_devenv.__main__:main
	:prog: devenv
	:nested: none

Example Configuration
----------------------

.. code-block:: toml

	[build-system]
	# Minimum requirements for the build system to execute.
	requires = ["setuptools", "wheel"]  # PEP 508 specifications.

	[project]
	name = "spam"
	version = "2020.0.0"
	description = "Lovely Spam! Wonderful Spam!"
	dependencies = [
	  "httpx",
	  "gidgethub[httpx]>4.0.0",
	  "django>2.1; os_name != 'nt'",
	  "django>2.0; os_name == 'nt'"
	]

	[project.optional-dependencies]
	test = [
	  "pytest[testing]<5.0.0",
	  "pytest-cov"
	]

Then run:

.. prompt:: bash

	pyproject-devenv

::

	Successfully created development virtualenv.

Output of ``pip list``::

	Package          Version
	---------------- ---------
	argcomplete      1.12.3
	asgiref          3.3.4
	atomicwrites     1.4.0
	attrs            20.3.0
	certifi          2020.12.5
	cffi             1.14.5
	chardet          4.0.0
	coverage         5.5
	cryptography     3.4.7
	Django           3.2
	gidgethub        5.0.1
	h11              0.12.0
	httpcore         0.12.3
	httpx            0.17.1
	hypothesis       6.10.0
	idna             2.10
	more-itertools   8.7.0
	nose             1.3.7
	packaging        20.9
	pip              21.0.1
	pluggy           0.13.1
	py               1.10.0
	pycparser        2.20
	PyJWT            2.0.1
	pyparsing        2.4.7
	pytest           4.6.11
	pytest-cov       2.11.1
	pytz             2021.1
	requests         2.25.1
	rfc3986          1.4.0
	setuptools       54.2.0
	six              1.15.0
	sniffio          1.2.0
	sortedcontainers 2.3.0
	sqlparse         0.4.1
	uritemplate      3.0.1
	urllib3          1.26.4
	wcwidth          0.2.5
	wheel            0.36.2
