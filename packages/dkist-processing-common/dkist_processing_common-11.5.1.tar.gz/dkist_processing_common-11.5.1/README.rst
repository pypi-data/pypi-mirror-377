dkist-processing-common
=======================

|codecov|

This repository works in concert with `dkist-processing-core <https://pypi.org/project/dkist-processing-core/>`_ and `dkist-processing-*instrument*` to
form the DKIST calibration processing stack.

Usage
-----

The classes in this repository should be used as the base of any DKIST processing pipeline tasks. Science tasks should subclass `ScienceTaskL0ToL1Base`.

Each class is built on an abstract base class with the `run` method left for a developer to fill out with the required steps that the task should take.
This class is then used as the callable object for the workflow and scheduling engine.

Example
-------

.. code-block:: python

    from dkist_processing_common.tasks.base import ScienceTaskL0ToL1Base


    class RemoveArtifacts(ScienceTaskL0ToL1Base):
        def run(self):
            # task code here
            total = 2 + 5

Deployment
----------

dkist-processing-common is deployed to `PyPI <https://pypi.org/project/dkist-processing-common/>`_

Development
-----------

There are two prerequisites for test execution on a local machine:


* Redis.  A running instance of redis on the local machine is required. The tests will use the default host ip of localhost and port of 6379 to connect to the database.

* RabbitMQ.  A running instance of rabbitmq on the local machine is required.  The tests will use the default host of localhost and a port of 5672 to connect to the interservice bus.


To run the tests locally, clone the repository and install the package in editable mode with the test extras.


.. code-block:: bash

    git clone git@bitbucket.org:dkistdc/dkist-processing-common.git
    cd dkist-processing-common
    pre-commit install
    pip install -e .[test]
    # Redis must be running
    pytest -v --cov dkist_processing_common

Changelog
#########

When you make **any** change to this repository it **MUST** be accompanied by a changelog file.
The changelog for this repository uses the `towncrier <https://github.com/twisted/towncrier>`__ package.
Entries in the changelog for the next release are added as individual files (one per change) to the ``changelog/`` directory.

Writing a Changelog Entry
^^^^^^^^^^^^^^^^^^^^^^^^^

A changelog entry accompanying a change should be added to the ``changelog/`` directory.
The name of a file in this directory follows a specific template::

  <PULL REQUEST NUMBER>.<TYPE>[.<COUNTER>].rst

The fields have the following meanings:

* ``<PULL REQUEST NUMBER>``: This is the number of the pull request, so people can jump from the changelog entry to the diff on BitBucket.
* ``<TYPE>``: This is the type of the change and must be one of the values described below.
* ``<COUNTER>``: This is an optional field, if you make more than one change of the same type you can append a counter to the subsequent changes, i.e. ``100.bugfix.rst`` and ``100.bugfix.1.rst`` for two bugfix changes in the same PR.

The list of possible types is defined the the towncrier section of ``pyproject.toml``, the types are:

* ``feature``: This change is a new code feature.
* ``bugfix``: This is a change which fixes a bug.
* ``doc``: A documentation change.
* ``removal``: A deprecation or removal of public API.
* ``misc``: Any small change which doesn't fit anywhere else, such as a change to the package infrastructure.


Rendering the Changelog at Release Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you are about to tag a release first you must run ``towncrier`` to render the changelog.
The steps for this are as follows:

* Run `towncrier build --version vx.y.z` using the version number you want to tag.
* Agree to have towncrier remove the fragments.
* Add and commit your changes.
* Tag the release.

**NOTE:** If you forget to add a Changelog entry to a tagged release (either manually or automatically with ``towncrier``)
then the Bitbucket pipeline will fail. To be able to use the same tag you must delete it locally and on the remote branch:

.. code-block:: bash

    # First, actually update the CHANGELOG and commit the update
    git commit

    # Delete tags
    git tag -d vWHATEVER.THE.VERSION
    git push --delete origin vWHATEVER.THE.VERSION

    # Re-tag with the same version
    git tag vWHATEVER.THE.VERSION
    git push --tags origin main

.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist-processing-common/graph/badge.svg?token=3QSLGSEF3O
 :target: https://codecov.io/bb/dkistdc/dkist-processing-common
