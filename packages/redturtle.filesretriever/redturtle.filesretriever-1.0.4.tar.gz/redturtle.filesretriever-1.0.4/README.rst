.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://travis-ci.org/collective/redturtle.filesretriever.svg?branch=master
    :target: https://travis-ci.org/collective/redturtle.filesretriever

.. image:: https://coveralls.io/repos/github/collective/redturtle.filesretriever/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/redturtle.filesretriever?branch=master
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/redturtle.filesretriever.svg
    :target: https://pypi.python.org/pypi/redturtle.filesretriever/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/redturtle.filesretriever.svg
    :target: https://pypi.python.org/pypi/redturtle.filesretriever
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/redturtle.filesretriever.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/redturtle.filesretriever.svg
    :target: https://pypi.python.org/pypi/redturtle.filesretriever/
    :alt: License


=========================
RedTurtle Files Retriever
=========================

Utility view to retrieve massive files from a remote page.

View
----

There is an helper view (**/files-retriever**) that you can call on every Plone folderish context.

Files will be saved in that context.

Restapi endpoints
-----------------

There are two endpoints:

- @files-list (POST): accept an url and some CSS selectors, and returns a list of found links in the page.
- @save-files (POST): accept a list of urls/titles and will download resources and save them in the current context.

Translations
------------

This product has been translated into

- English
- Italian


Installation
------------

Install redturtle.filesretriever by adding it to your buildout::

    [buildout]

    ...

    eggs =
        redturtle.filesretriever


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/RedTurtle/redturtle.filesretriever/issues
- Source Code: https://github.com/RedTurtle/redturtle.filesretriever


License
-------

The project is licensed under the GPLv2.
