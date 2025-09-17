=======
bitlist
=======

Pure-Python library for working with bit vectors.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/bitlist.svg#
   :target: https://badge.fury.io/py/bitlist
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/bitlist/badge/?version=latest
   :target: https://bitlist.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/lapets/bitlist/workflows/lint-test-cover-docs/badge.svg#
   :target: https://github.com/lapets/bitlist/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/lapets/bitlist/badge.svg?branch=main
   :target: https://coveralls.io/github/lapets/bitlist?branch=main
   :alt: Coveralls test coverage summary.

Purpose
-------
This library allows programmers to work with bit vectors using a pure-Python data structure. Its design prioritizes interoperability with built-in Python classes and operators.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/bitlist>`__:

.. code-block:: bash

    python -m pip install bitlist

The library can be imported in the usual manner:

.. code-block:: python

    import bitlist
    from bitlist import bitlist

Examples
^^^^^^^^

.. |bitlist| replace:: ``bitlist``
.. _bitlist: https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist

This library makes it possible to construct bit vectors from a variety of representations (including integers, bytes-like objects, strings of binary digits, lists of binary digits, and other bit vectors). Integer arguments are converted into a big-endian binary representation:

.. code-block:: python

    >>> bitlist(123)
    bitlist('1111011')
    >>> bitlist(bytes([255, 254]))
    bitlist('1111111111111110')
    >>> bitlist('101')
    bitlist('101')
    >>> bitlist([1, 0, 1, 1])
    bitlist('1011')
    >>> bitlist(bitlist('1010'))
    bitlist('1010')

The optional ``length`` parameter can be used to specify the length of the created bit vector (padding consisting of zero bits is applied automatically *on the left-hand size*, if necessary):

.. code-block:: python

    >>> bitlist(bytes([123]), length=16)
    bitlist('0000000001111011')
    >>> bitlist(16, 64)
    bitlist('0000000000000000000000000000000000000000000000000000000000010000')
    >>> bitlist(bitlist(123), 8)
    bitlist('01111011')

If the ``length`` parameter has a value that is less than the minimum number of bits that would be included according to the default constructor behaviors, the bit vector is truncated *on the left-hand side* to match the specified length:

.. code-block:: python

    >>> bitlist(bytes([123]), length=7)
    bitlist('1111011')
    >>> bitlist(bytes([123]), 4)
    bitlist('1011')
    >>> bitlist(bytes([123]), 2)
    bitlist('11')
    >>> bitlist(bytes([123]), 0)
    bitlist()

Bit vectors are iterable sequences of individual bits (where each bit is represented as an integer). Both slice notation and retrieval of individual bits by index are supported. Furthermore, methods are available for converting a bit vector into other common representations:

.. code-block:: python

    >>> b = bitlist('1111011')
    >>> b[1:-1]
    bitlist('11101')
    >>> b[0]
    1
    >>> [bit for bit in b]
    [1, 1, 1, 1, 0, 1, 1]
    >>> b.bin()
    '1111011'
    >>> b.hex()
    '7b'
    >>> list(b.to_bytes())
    [123]

`Concatenation <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__add__>`__, `partitioning <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__truediv__>`__, `subscription and slicing <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__getitem__>`__, `shift and rotation <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__lshift__>`__, `comparison <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__eq__>`__, and `logical <https://bitlist.readthedocs.io/en/2.0.0/_source/bitlist.html#bitlist.bitlist.bitlist.__and__>`__ operations are also supported by instances of the |bitlist|_ class. The larger example below -- a bitwise addition function -- illustrates the use of various operators supported by instances of the |bitlist|_ class:

.. code-block:: python

    >>> def add(x, y):
    ...     """Bitwise addition algorithm."""
    ...     r = bitlist(0)
    ...     carry = 0
    ...     # Use negative indices for big-endian interface.
    ...     for i in range(1, max(len(x), len(y)) + 1):
    ...         r[-i] = (x[-i] ^ y[-i]) ^ carry
    ...         carry = (x[-i] & y[-i]) | (x[-i] & carry) | (y[-i] & carry)
    ...     r[-(max(len(x), len(y)) + 1)] = carry
    ...     return r
    ...
    >>> int(add(bitlist(123), bitlist(456)))
    579

The `testing script <https://bitlist.readthedocs.io/en/2.0.0/_source/test_bitlist.html>`__ that accompanies this library contains additional examples of bitwise arithmetic operations implemented with the help of |bitlist|_ operators.

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install ".[docs,lint]"

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install ".[docs]"
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install ".[test]"
    python -m pytest

The subset of the unit tests included in the module itself and the *documentation examples* that appear in the testing script can be executed separately using `doctest <https://docs.python.org/3/library/doctest.html>`__:

.. code-block:: bash

    python src/bitlist/bitlist.py -v
    python test/test_bitlist.py -v

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install ".[lint]"
    python -m pylint src/bitlist test/test_bitlist.py

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/lapets/bitlist>`__ for this library.

Versioning
^^^^^^^^^^
Beginning with version 0.3.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/bitlist>`__ via the GitHub Actions workflow found in ``.github/workflows/build-publish-sign-release.yml`` that follows the `recommendations found in the Python Packaging User Guide <https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`__.

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions.

To publish the package, create and push a tag for the version being published (replacing ``?.?.?`` with the version number):

.. code-block:: bash

    git tag ?.?.?
    git push origin ?.?.?
