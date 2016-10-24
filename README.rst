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

.. _AWS boto3: https://aws.amazon.com/pt/sdk-for-python/
.. _Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/
.. _click: http://click.pocoo.org/
.. _py.test: http://pytest.org/
.. _tox: https://testrun.org/tox/latest/
.. _flake8: https://gitlab.com/pycqa/flake8