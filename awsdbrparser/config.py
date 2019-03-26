# -*- coding: utf-8 -*-
#
# awsdbrparser/config.py
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

import os
import json

from datetime import datetime

OUTPUT_TO_FILE = '1'
OUTPUT_TO_ELASTICSEARCH = '2'

OUTPUT_OPTIONS = (
    (OUTPUT_TO_FILE, 'Output to File'),
    (OUTPUT_TO_ELASTICSEARCH, 'Output to Elasticsearch'),)

PROCESS_BY_LINE = '1'
PROCESS_BY_BULK = '2'
PROCESS_BI_ONLY = '3'

PROCESS_OPTIONS = (
    (PROCESS_BY_LINE, 'Process by Line'),
    (PROCESS_BY_BULK, 'Process in Bulk'),
    (PROCESS_BI_ONLY, 'Process BI Only'))

BULK_SIZE = 1000
ES_TIMEOUT = 30

DEFAULT_ES2 = True
DATA_PATH = 'data'
DOCTYPE_FILES = {
    '2': 'dbr_doctype_es2x.json',
    '6': 'dbr_doctype_es6x.json'
}

"""
DBR document properties for actual document type.
See :attr:`Config.es_doctype` and :attr:`Config.mapping` for details.
"""


class Config(object):
    def __init__(self):
        today = datetime.today()

        # elasticsearch default values
        self.es_host = 'search-name-hash.region.es.amazonaws.com'
        self.es_port = 80
        self.es_index = 'billing'
        self.es_doctype = 'billing'
        self.es_year = today.year
        self.es_month = today.month
        self.es_timestamp = 'UsageStartDate'  # fieldname that will be replaced by Timestamp
        self.es_timeout = ES_TIMEOUT

        # aws account id
        self.account_id = '01234567890'

        # encoding (this is the default encoding for most files, but if
        # customer uses latin/spanish characters you may to change
        # self.encoding = 'iso-8859-1'
        self.encoding = 'utf-8'

        # update flag (if True update existing documents in Elasticsearch index;
        # defaults to False for performance reasons)
        self.update = False

        # check flag (check if current record exists before add new -- for
        # incremental updates)
        self.check = False

        # Use AWS Signed requests to access the Elasticsearch
        self.awsauth = False

        # Run Business Intelligence on the line items
        self.analytics = False

        # Time to wait for the analytics process. Default is 30 minutes
        self.analytics_timeout = 30

        # Run Business Intelligence Only
        self.bi_only = False

        # delete index flag indicates whether or not the current elasticsearch
        # should be kept or deleted
        self.delete_index = False

        # debug flag (will force print some extra data even in quiet mode)
        self.debug = False

        # fail fast flag (if True stop parsing on first index error)
        self.fail_fast = False

        # input and output filenames
        self._input_filename = None
        self._output_filename = None

        # other defaults
        self.csv_delimiter = ','
        self._output_type = OUTPUT_TO_FILE
        self._bulk_mode = PROCESS_BY_LINE
        self.bulk_size = BULK_SIZE
        self.bulk_msg = {
            "RecordType": [
                "StatementTotal",
                "InvoiceTotal",
                "Rounding",
                "AccountTotal"]}
        self._es2 = False
        self._doctype = None

    @property
    def mapping(self):
        return {self.es_doctype: self.doctype}

    @property
    def output_type(self):
        return self._output_type

    @output_type.setter
    def output_type(self, value):
        if value not in (v for v, s in OUTPUT_OPTIONS):
            raise ValueError('Invalid output type value: {!r}'.format(value))
        self._output_type = value

    @property
    def output_to_file(self):
        return self.output_type == OUTPUT_TO_FILE

    @property
    def output_to_elasticsearch(self):
        return self.output_type == OUTPUT_TO_ELASTICSEARCH

    @property
    def process_mode(self):
        return self._bulk_mode

    @process_mode.setter
    def process_mode(self, value):
        if value not in (v for v, s in PROCESS_OPTIONS):
            raise ValueError('Invalid bulk mode value: {!r}'.format(value))
        self._bulk_mode = value

    @property
    def input_filename(self):
        return self._input_filename or self._sugest_filename('.csv')

    @input_filename.setter
    def input_filename(self, value):
        self._input_filename = value

    @property
    def output_filename(self):
        return self._output_filename or self._sugest_filename('.json')


    @property
    def doctype(self):
        return self._doctype

    @doctype.setter
    def doctype(self, version):
        if not version in ('2', '6'):
            raise Exception('Invalid document type version.')

        try:
            filename = os.path.join(os.path.dirname(__file__), DATA_PATH, DOCTYPE_FILES[version])
            self._doctype = json.load(open(filename))
        except IOError:
            print('Unable to load Elastic Search Doctype')
            raise

    @property
    def es2(self):
        return self._es2

    @es2.setter
    def es2(self, is_es2x):
        self._es2 = is_es2x
        if self._es2:
            version = '2'
        else:
            version = '6'
        self.doctype = version

    @property
    def index_name(self):
        if self.es2:
            # if using Elasticsearch 2.x the index is composed by <index-name>-<year>-<month>
            return '{}-{:d}-{:02d}'.format(self.es_index, self.es_year, self.es_month)
        else:
            # if using Elasticsearch 6.x the index is just the prefix <index-name>
            return self.es_index


    @output_filename.setter
    def output_filename(self, value):
        self._output_filename = value

    def update_from(self, **kwargs):
        for attr, value in kwargs.items():
            if value is None:
                # simply ignore None values
                continue
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise AttributeError('{!r} object has no attribute {!r}'.format(
                    self.__class__.__name__, attr))

    def _sugest_filename(self, extension):
        return '{}-aws-billing-detailed-line-items-with-' \
               'resources-and-tags-{:04d}-{:02d}{}'.format(self.account_id, self.es_year, self.es_month, extension)
