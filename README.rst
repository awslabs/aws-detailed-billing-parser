.. image:: https://travis-ci.org/awslabs/aws-detailed-billing-parser.svg?branch=master
    :target: https://travis-ci.org/awslabs/aws-detailed-billing-parser


AWS DBR parser
==============

    Author: Rafael M. Koike

    AWS ProServe

This script was created to support automatic parsing of Detailed Billing
Records (DBR) to JSON format and send these documents directly to
ElasticSearch or save it in a JSON file. It’s based on `AWS boto3`_,
`Elasticsearch`_ Python API and `click`_ CLI creation kit.

Instalation Instructions
------------------------

This project isn’t on PyPI yet. For installation you will need to clone
this repository and use ``setup.py`` script to install it. For
requirements see the ``requirements/base.txt`` file. Clone this
repository and install using plain python and the ``setup.py`` script.
For example:

-  This option just install the dbrparser but maybe you can use the
   job.sh from the repository to schedule the process in your cronjob

::

    $ pip install git+https://github.com/awslabs/aws-detailed-billing-parser.git

-  This option clone the repository from git to your instance and
   install

.. code:: bash

    $ git clone https://github.com/awslabs/aws-detailed-billing-parser.git
    $ cd aws-detailed-billing-parser
    $ python setup.py install

Executing
---------

Once installed run ``dbrparser`` CLI with ``--help`` option:

.. code:: bash

    $ dbrparser --help

Running Tests
-------------

Tests still need to be written. But we have already introduced
`py.test`_, `tox`_ for test run automation and `flake8`_ to check
quality and style of the code. There are nice stubs for testing the CLI
command line. All you have to do is install **tox** and issue ``tox`` in
the command line.

TODO (Features to incorporate in the dbrparser)
-----------------------------------------------

-  Unzip (Extract the DBR from zip file);
-  S3 (Copy the source file from S3 bucket to local folder to process);
-  To be compatible with **AWS Lambda** the parser must run in max 5 min
   and depending on the size of the file this won’t be possible, so we
   will probably need to include a new option like, say ``--max-rows``
   and every call to lambda will process a maximum of ``10000`` rows for
   exemple. This may give us a previsibility that lambda will work in
   the correct timeframe;
-  Write more tests.

Changes
-------
Version 0.5.4 - 2017-08-29
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Bugfix: RI and Spot coverage was returning incorrect results with Python 2.7 due to the default integer result from /

Version 0.5.3 - 2017-08-28
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Refactoring: analytics() function has been refactored to reduce the memory usage and avoid problems with huge DBR files

Version 0.5.2 - 2017-08-24
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  BugFix: Python 3 has deprecated the parameter encoding in the json library and some functions
still have them. Removed the encoding paramter solved the incompatibility


Version 0.5.1 - 2017-01-05
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  BugFix: Some running instances don't have the UsageType in the format: <Usage>:<InstanceType>
Than we need to check if the UsageType has ':' and return InstanceType or N/A


Version 0.5.0 - 2016-10-11
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Included Dynamic Template to new document fields be Not Analyzed
-  Included support to AWS Signed V4 requests. If you are running the
   program from an EC2 instance or from a computer that has installed
   aws cli and configured with the correct credentials you just need to
   include\ ``--awsauth`` parameter
-  Changed the split\_keys function to pre\_process and include extra
   information based on the UsageType field Now you have:

   -  UsageItem with the options:

      -  On-Demand
      -  Reserved Instance
      -  Spot Instance

   -  InstanceType with only the instance name extracted from the
      UsageType

Version 0.4.1 - 2016-08-31
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Changed requirements to support newer versions of boto3. (Due to some
   other softwares that need version 1.3.1 or higher, dbrparser is
   conflicting with other softwares)

Version 0.4.1 - 2016-05-11
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Bugfix of timeout when sending by bulk (Increased to 30 seconds)

Version 0.4.0 - 2016-03-27
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Project was completely restructured in order to create a proper
   Python package called ``awsdbrparser`` and the CLI name
   ``dbrparser``;
-  In the CLI side, ``argparse`` was dropped in favor of Armin
   Ronacher’s ``click``, allowing a better and easier CLI
   implementation;
-  Introduced option ‘–quiet’ for those who intent to schedule DBR
   parsing via cron jobs, for example;
-  Introduced option ‘–fail-fast’ which will stop parsing execution in
   case of an expected parse error or other component error;
-  Dropped own implementation of progress bar in favor of click’s
   progress bar, which includes a nice ETA (estimated time for
   acomplishment) calculation;
-  When used as a library, parser execution can be parametrized through
   ``awsdbrparser.config.Config`` class instance.
-  Entire code was reviewed to match PEP8 compliance (with fewer
   exceptions) through ``flake8``.

Version 0.3 - 2016-02-12
~~~~~~~~~~~~~~~~~~~~~~~~

-  Added incremental updates with ``--check`` parameter (Now you can
   update the same file to the index without need to delete the index
   and reprocess the entirely file again);
-  Compatible with Elasticsearch 2.1 and above (Removed the
   ``_timestamp`` from mapping that has been deprecated from 2.0 and
   above);
-  Included elapsed time to evaluate the time to process the file.

Version 0.2 - 2015-10-26
~~~~~~~~~~~~~~~~~~~~~~~~

-  Filter of control messages (Stop the error in the end of processing);
-  Verbose output of the processing;
-  Progress bar;
-  Output options (to file or directly to Elasticsearch);
-  Elasticsearch mapping.

version 0.1 - 2015-10-17
~~~~~~~~~~~~~~~~~~~~~~~~

-  Initial version.

.. _AWS boto3: https://aws.amazon.com/pt/sdk-for-python/
.. _Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/
.. _click: http://click.pocoo.org/
.. _py.test: http://pytest.org/
.. _tox: https://testrun.org/tox/latest/
.. _flake8: https://gitlab.com/pycqa/flake8
