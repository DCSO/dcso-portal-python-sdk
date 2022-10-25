DCSO Portal Python SDK
======================

***This project is now deprecated. It is not maintained anymore.***

Copyright (c) 2020, 2021, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

DCSO Portal Python Software Development Kit (SDK) helps you create
application which need to interact with the DCSO Portal.

Documentation: [https://dcso.github.io/dcso-portal-python-sdk/dcso/portal/](https://dcso.github.io/dcso-portal-python-sdk/dcso/portal/)

Requirements
------------

This library is, when installed, pure Python. We use only 3rd party tools
for installation and documentation generation.

* Python v3.7 or greater (Python v3.6 as best effort)
* Requirements:
  - for distribution, see `requirements_dist.txt`

Requirements can be installed using, for example, `pip`:

    $ pip install -r requirements_dist.txt

We strongly advise to use a Virtual Environment for testing or for
development. This makes sure your local Python environment stays clean.

    $ python3 -m venv venvdir
    $ source ./venvdir/bin/activate
    (venvdir)$ pip install -r requirements.txt 

Installation
------------

This section explains how to install the DCSO Portal Python SDK. You can get
a copy and source on [GitHub](https://github.com/dcso/dcso-portal-python-sdk).

### From Python Package Index (PyPI)

    $ pip install -U dcso-portal-python-sdk


### Using Source

Installation is done using `setup.py`:

    $ pip install .
    or
    $ python3 setup.py install


It is advised, when developing or testing, to use a Virtual Environment (see
Prerequisites in this document).

Documentation
-------------

Documentation is available as HTML in the `docs/dcso/portal` folder.

It is possible to generate it using:

    $ ./gendocs.py

Alternatively, it is also possible to have the documentation service
by the pdoc3 web server. This is mostly useful for working on the
documentation since it will rebuild automatically:

    $ PYTHONPATH="./lib" pdoc --http : --html \
        --template-dir support/doc_templates dcso.portal
    
    open http://localhost:8080/dcso.portal/

See `pdoc --help` for more information.


Examples
--------

The folder `examples` contains code which can be used to learn how to
use this SDK.

When running the examples, within the root of the repository, use
the `PYTHONPATH` variable:

    $ PYTHONPATH="lib" python3 examples/basic.py

### example/portal_cli.py

The `portal_cli.py`, Portal Command-Line Intereface, show how to create an
interactive client.
It will prompt for username, password, and if needed, also the one-time password.  
The result is showing all permissions the user has, and whether the user
has TDH Coordinator access.

### example/exec_graphql.py

The `exec_graphql.py` shows how to connect using a Machine Token (also known as
API Tokene), and execute some GraphQL.


Development
-----------

The SDK itself and its tests stays as pure Python as possibly can be.  
An exception is the Setuptools requirement for installation or any tools
for packaging.

### DCSO Namespace

We use the `dcso` package namespace, which can be recognized lacking the
`__init__.py`. This helps having other Python project which can then
install in the same location.


### Running Tests

Directly using the `unittest` package from command line:

    $ PYTHONPATH="lib" python3 -m unittest discover -s ./lib/dcso/ -vv

Or using the wrapper script, to run all tests:

    $ python3 test.py


IDE Tips
--------

### PyCharm

Right click on the `lib/` folder in the root of the repository and 
select 'Mark Directory as > Sources Root'. This will make sure PyCharm
add the code to its `PYTHONPATH`.


Distribution
------------

DCSO Portal Python SDK is make available for downloading from GitHub as source
distributions are made available with each release.

We also upload to the Python Package Index (PyPI) using `twine`, and an API token.

### Preparing a Release

It is a good idea to start with a fresh Virtual Environment when creating a new
release.

1. Install requirements: `pip install -r requirements_dist.txt`
2. Create a supporting branch which contains the version number to be releases,
   for example, `release/1.0.0-beta3`
3. Update `lib/dcso/portal/_version.py` and update the `__version__` variable
4. Generate documentation: `./gendocs.py`
5. Create source distribution: `python setup.py sdist --formats=zip` (will be created
   in sub folder `dist`)

### Upload to PyPI

With the source distribution created as ZIP-archive, we can now upload to PyPI using
the Twine module.

```
python3 -m twine upload dist/dcso_portal_python_sdk-1.0.0b3.zip
```

The `twine` module is installed using `pip install -r requirements_dist.txt`.

Twine will ask you for credentials:

1. Use `__token__` as username
2. As Password, enter the PyPI API Token for the `dcso-portal-python-sdk` project (note
   that this includes the `pypi-` prefix)


License
-------

[MIT](LICENSE.txt)
