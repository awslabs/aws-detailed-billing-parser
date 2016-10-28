# -*- coding: utf-8 -*-
#
# awsdbrparser/cli.py
#
# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime
import os
import sys
import time

import click

from . import parser
from .config import BULK_SIZE
from .config import Config
from .config import ES_TIMEOUT
from .config import OUTPUT_OPTIONS
from .config import OUTPUT_TO_FILE
from .config import PROCESS_BY_LINE
from .config import PROCESS_OPTIONS
from .utils import ClickEchoWrapper
from .utils import display_banner
from .utils import hints_for
from .utils import values_of

configure = click.make_pass_decorator(Config, ensure=True)


@click.command()
@click.option('-i', '--input', metavar='FILE', help='Input file (expected to be a CSV file).')
@click.option('-o', '--output', metavar='FILE', help='Output file (will generate a JSON file).')
@click.option('-e', '--es-host', metavar='HOST', help='Elasticsearch host name or IP address.')
@click.option('-p', '--es-port', type=int, metavar='PORT', help='Elasticsearch port number.')
@click.option('-to', '--es-timeout', type=int, default=ES_TIMEOUT, metavar='TIMEOUT',
              help='Elasticsearch connection Timeout.')
@click.option('-ei', '--es-index', metavar='INDEX', help='Elasticsearch index prefix.')
@click.option('-bi', '--analytics', is_flag=True, default=False,
              help='Execute analytics on file to generate extra-information')
@click.option('-a', '--account-id', help='AWS Account-ID.')
@click.option('-y', '--year', type=int, help='Year for the index (defaults to current year).')
@click.option('-m', '--month', type=int, help='Month for the index (defaults to current month).')
@click.option('-t', '--output-type', default=OUTPUT_TO_FILE,
              type=click.Choice(values_of(OUTPUT_OPTIONS)),
              help='Output type ({}, default is {}).'.format(hints_for(OUTPUT_OPTIONS), OUTPUT_TO_FILE))
@click.option('-d', '--csv-delimiter', help='CSV delimiter (default is comma).')
@click.option('--delete-index', is_flag=True, default=False,
              help='Delete current index before processing (default is keep).')
@click.option('-bm', '--process-mode', default=PROCESS_BY_LINE,
              type=click.Choice(values_of(PROCESS_OPTIONS)),
              help='Send DBR line-by-line or in bulk ({}, bulk mode implies sending '
                   'data to an Elasticsearch instance).'.format(hints_for(PROCESS_OPTIONS)))
@click.option('-bs', '--bulk-size', default=BULK_SIZE, metavar='BS',
              help='Define the size of bulk to send to (see --bulk-mode option).')
@click.option('-u', '--update', is_flag=True, default=False,
              help='Update existing documents in Elasticseaerch index before add (should be used with --check flag).')
@click.option('-c', '--check', is_flag=True, default=False,
              help='Check if current record exists in Elasticseaerch before add '
                   'new (this option will be ignored in bulk processing).')
@click.option('--awsauth', is_flag=True, default=False,
              help='Access the Elasticsearch with AWS Signed V4 Requests')
@click.option('-v', '--version', is_flag=True, default=False, help='Display version number and exit.')
@click.option('-q', '--quiet', is_flag=True, default=False, help='Runs as silently as possible.')
@click.option('--fail-fast', is_flag=True, default=False, help='Stop parsing on first index error.')
@click.option('--debug', is_flag=True, default=False, help='Print extra data even in quiet mode.')
@configure
def main(config, *args, **kwargs):
    """AWS - Detailed Billing Records parser"""

    quiet = kwargs.pop('quiet')
    version = kwargs.pop('version')

    echo = ClickEchoWrapper(quiet=quiet)
    display_banner(echo=echo)

    if version:
        return

    # tweak kwargs for expected config object attributes
    kwargs['input_filename'] = kwargs.pop('input', config.input_filename)
    kwargs['output_filename'] = kwargs.pop('output', config.output_filename)
    kwargs['es_year'] = kwargs.pop('year', config.es_year)
    kwargs['es_month'] = kwargs.pop('month', config.es_month)

    config.update_from(**kwargs)

    if not os.path.isfile(config.input_filename):
        sys.exit('Input file not found: {}'.format(config.input_filename))

    start = time.time()
    parser.parse(config, verbose=(not quiet))

    elapsed_time = time.time() - start
    echo('Elapsed time: {}'.format(datetime.timedelta(seconds=elapsed_time)))
