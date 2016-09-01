
# AWS DBR parser #

> Author: Rafael M. Koike
>
> AWS ProServe

This script was created to support automatic parsing of Detailed Billing Records
(DBR) to JSON format and send these documents directly to ElasticSearch or save
it in a JSON file. It's based on [AWS boto3](https://aws.amazon.com/pt/sdk-for-python/),
[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/)
Python API and [click](http://click.pocoo.org/) CLI creation kit.


## Instalation Instructions

This project isn't on PyPI yet. For installation you will need to clone this
repository and use `setup.py` script to install it. For requirements see
the `requirements/base.txt` file. Clone this repository and install
using plain python and the `setup.py` script. For example:

```bash
$ git clone https://github.com/awslabs/aws-detailed-billing-parser.git
$ cd aws-detailed-billing-parser
$ python setup.py install
```

## Executing

Once installed run `dbrparser` CLI with `--help` option:

```bash
$ dbrparser --help
```

## Running Tests

Tests still need to be written. But we have already introduced
[py.test](http://pytest.org/), [tox](https://testrun.org/tox/latest/) for test
run automation and [flake8](https://gitlab.com/pycqa/flake8) to check quality
and style of the code. There are nice stubs for testing the CLI command line.
All you have to do is install **tox** and issue `tox` in the command line.


## TODO

* Unzip (Extract the DBR from zip file);
* S3 (Copy the source file from S3 bucket to local folder to process);
* To be compatible with **AWS Lambda** the parser must run in max 5 min and
depending on the size of the file this won't be possible, so we will probably
need to include a new option like, say `--max-rows` and every call to lambda
will process a maximum of `10000` rows for exemple. This may give us a
previsibility that lambda will work in the correct timeframe;
* Write more tests.


## Changes

### Version 0.4.1 - 2016-08-31

* Changed requirements to support newer versions of boto3. 
(Due to some other softwares that need version 1.3.1 or higher, dbrparser is conflicting with other softwares)

### Version 0.4.1 - 2016-05-11

* Bugfix of timeout when sending by bulk (Increased to 30 seconds)

### Version 0.4.0 - 2016-03-27

* Project was completely restructured in order to create a proper Python
package called `awsdbrparser` and the CLI name `dbrparser`;
* In the CLI side, `argparse` was dropped in favor of Armin Ronacher's `click`,
allowing a better and easier CLI implementation;
* Introduced option '--quiet' for those who intent to schedule DBR parsing via
cron jobs, for example;
* Introduced option '--fail-fast' which will stop parsing execution in case of
an expected parse error or other component error;
* Dropped own implementation of progress bar in favor of click's progress bar,
which includes a nice ETA (estimated time for acomplishment) calculation;
* When used as a library, parser execution can be parametrized through
`awsdbrparser.config.Config` class instance.
* Entire code was reviewed to match PEP8 compliance (with fewer exceptions)
through `flake8`.

### Version 0.3 - 2016-02-12

* Added incremental updates with `--check` parameter (Now you can update the
same file to the index without need to delete the index and reprocess the
entirely file again);
* Compatible with Elasticsearch 2.1 and above (Removed the `_timestamp` from
mapping that has been deprecated from 2.0 and above);
* Included elapsed time to evaluate the time to process the file.

### Version 0.2 - 2015-10-26

* Filter of control messages (Stop the error in the end of processing);
* Verbose output of the processing;
* Progress bar;
* Output options (to file or directly to Elasticsearch);
* Elasticsearch mapping.

### version 0.1 - 2015-10-17

* Initial version.
