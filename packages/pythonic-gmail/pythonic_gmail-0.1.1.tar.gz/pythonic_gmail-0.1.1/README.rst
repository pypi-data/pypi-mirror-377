
.. image:: https://readthedocs.org/projects/pythonic-gmail/badge/?version=latest
    :target: https://pythonic-gmail.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pythonic_gmail-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pythonic_gmail-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/pythonic_gmail-project

.. image:: https://img.shields.io/pypi/v/pythonic-gmail.svg
    :target: https://pypi.python.org/pypi/pythonic-gmail

.. image:: https://img.shields.io/pypi/l/pythonic-gmail.svg
    :target: https://pypi.python.org/pypi/pythonic-gmail

.. image:: https://img.shields.io/pypi/pyversions/pythonic-gmail.svg
    :target: https://pypi.python.org/pypi/pythonic-gmail

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://pythonic-gmail.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/pythonic_gmail-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/pythonic-gmail#files


Welcome to ``pythonic_gmail`` Documentation
==============================================================================
.. image:: https://pythonic-gmail.readthedocs.io/en/latest/_static/pythonic_gmail-logo.png
    :target: https://pythonic-gmail.readthedocs.io/en/latest/

**A Pythonic object-oriented wrapper for the Gmail API**

``pythonic_gmail`` transforms the traditional Google Gmail API client into an intuitive, object-oriented interface that follows Python best practices. While the native Gmail API returns raw JSON dictionaries, this library provides structured data models with property-based access, automatic pagination handling, and efficient batch operations.

**Key Features:**

**Object-Oriented Data Models**: All Gmail API responses are wrapped in frozen dataclasses with property-based access. Instead of accessing ``response["messages"][0]["id"]``, you simply use ``message.id``. Each model maintains the original raw data while providing a clean, type-safe interface with intelligent property caching.

**Intelligent Pagination**: Gmail's pagination mechanism with ``pageToken`` and ``nextPageToken`` is completely abstracted away. The library provides iterator proxies that handle token management automatically, allowing you to focus on processing data rather than managing API pagination state.

**Efficient Batch Operations**: Built-in batch processing utilities automatically group individual API calls into efficient batch requests. This significantly reduces HTTP overhead when retrieving multiple messages or threads, improving performance for bulk operations.

**Stable Interface Design**: The library implements a core data extraction pattern where each model exposes essential information through a standardized ``core_data`` property. This provides resilience against API schema changes while maintaining a consistent developer experience.

**Flexible Iterator Architecture**: Advanced iterator proxies support both response-level iteration (for processing API responses in batches) and item-level iteration (for processing individual messages or threads). This dual-mode approach provides flexibility for different use cases and performance requirements.


.. _install:

Install
------------------------------------------------------------------------------

``pythonic_gmail`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install pythonic-gmail

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pythonic-gmail
