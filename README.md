DCSO Portal Python SDK
======================

Copyright (c) 2020, 2021, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

DCSO Portal Python Software Development Kit (SDK) helps you create
application which need to interact with the DCSO Portal.

Documentation: [https://dcso.github.io/dcso-portal-python-sdk/dcso/portal/](https://dcso.github.io/dcso-portal-python-sdk/dcso/portal/)

Requirements
------------

This library is, when installed, pure Python. We use only 3rd party tools
for installation and documentation generation.

* Python v3.7 or greater (Python v3.6 as best effort)
* See requirements in `requirements.txt`

Requirements can be installed using, for example, `pip`:

    $ pip install -r requirements.txt

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

License
-------

[MIT](LICENSE.txt)
