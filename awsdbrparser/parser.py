# -*- coding: utf-8 -*-
#
# awsdbrparser/parser.py
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
from __future__ import print_function

import collections
import csv
import json
import time
import threading

import boto3
import click
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers
from requests_aws4auth import AWS4Auth

from . import utils
from .config import PROCESS_BY_BULK, PROCESS_BY_LINE, PROCESS_BI_ONLY

Summary = collections.namedtuple('Summary', 'added skipped updated control_messages')
"""
Holds the summary of documents processed by the parser.
"""


class ParserError(Exception):
    pass


def analytics(config):
    """
    This function generate extra information in elasticsearch analyzing the lineitems of the file
    :param config:
    :return:
    """
    index_name = '{}-{:d}-{:02d}'.format(
        config.es_index,
        config.es_year,
        config.es_month)

    # Opening Input filename again to run in parallel
    file_in = open(config.input_filename, 'r')
    awsauth = None
    if config.awsauth:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            region = session.region_name
            awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es',
                               session_token=credentials.token)

    es = Elasticsearch([{'host': config.es_host, 'port': config.es_port}], timeout=30, http_auth=awsauth,
                       connection_class=RequestsHttpConnection)
    csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)
    analytics_list = list()
    date_set = set()
    for recno, json_row in enumerate(csv_file):
        if is_control_message(json_row, config):
            continue

        else:
            analytics_list.append(json.dumps(utils.pre_process(
                json.dumps(json_row, ensure_ascii=False, encoding=config.encoding))))
            date_set.add(json_row.get('UsageStartDate'))

    # Lets work with the Analytics list
    print(date_set)

    file_in.close()


def ec2_per_usd(items):
    """
    This function receive a list of DBRrt dict and return a new list with dict items to send to Elasticsearch
    :param items:
    :return analytics_list:
    """
    analytics_list = list()
    for key, value in items:




def parse(config, verbose=False):
    """

    :param verbose:
    :param config: An instance of :class:`~awsdbrparser.config.Config` class,
        used for parsing parametrization.

    :rtype: Summary
    """
    global analytics_start
    echo = utils.ClickEchoWrapper(quiet=(not verbose))

    index_name = '{}-{:d}-{:02d}'.format(
        config.es_index,
        config.es_year,
        config.es_month)

    echo('Opening input file: {}'.format(config.input_filename))
    file_in = open(config.input_filename, 'r')

    if config.output_to_file:
        echo('Opening output file: {}'.format(config.output_filename))
        file_out = open(config.output_filename, 'w')

    elif config.output_to_elasticsearch:
        echo('Sending DBR to Elasticsearch host: {}:{}'.format(config.es_host, config.es_port))
        awsauth = None
        if config.awsauth:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                region = session.region_name
                awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es',
                                   session_token=credentials.token)

        es = Elasticsearch([{'host': config.es_host, 'port': config.es_port}], timeout=30, http_auth=awsauth,
                           connection_class=RequestsHttpConnection)
        if config.delete_index:
            echo('Deleting current index: {}'.format(index_name))
            es.indices.delete(index_name, ignore=404)
        es.indices.create(index_name, ignore=400)
        es.indices.put_mapping(index=index_name, doc_type=config.es_doctype, body=config.mapping)

    if verbose:
        progressbar = click.progressbar

        # calculate number of rows in input file in preparation to display a progress bar
        record_count = sum(1 for row in file_in) - 1
        file_in.seek(0)  # reset file descriptor

        echo("Input file has {} record(s)".format(record_count))

        if config.process_mode == PROCESS_BY_BULK:
            echo('Processing in BULK MODE, size: {}'.format(config.bulk_size))
        else:
            echo('Processing in LINE MODE')
    else:
        # uses a 100% bug-free progressbar, guaranteed :-)
        progressbar = utils.null_progressbar
        record_count = 0

    # If BI is enabled, create a thread and start running
    if config.analytics:
        analytics_start = time.time()
        echo('Starting the BI Analytics Thread')
        thread = threading.Thread(target=analytics, args=(config,))
        thread.start()

    added = skipped = updated = control = 0

    if config.process_mode == PROCESS_BY_BULK:
        with progressbar(length=record_count) as pbar:
            # If you wish to sort the records by UsageStartDate before send to
            # ES just uncomment the 2 lines below and comment the third line
            # reader = csv.DictReader(file_in, delimiter=config.csv_delimiter)
            # csv_file = sorted(reader, key=lambda line: line["UsageStartDate"]+line["UsageEndDate"])
            csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)

            def documents():
                for json_row in csv_file:
                    if not is_control_message(json_row, config):
                        if config.debug:
                            print(json.dumps(  # do not use 'echo()' here
                                utils.pre_process(
                                    json.dumps(json_row, ensure_ascii=False, encoding=config.encoding)),
                                ensure_ascii=False, encoding=config.encoding))
                        yield utils.pre_process(json.dumps(json_row, ensure_ascii=False, encoding=config.encoding))
                        pbar.update(1)

            for recno, (success, result) in enumerate(helpers.streaming_bulk(es, documents(),
                                                                             index=index_name,
                                                                             doc_type=config.es_doctype,
                                                                             chunk_size=config.bulk_size)):
                # <recno> integer, the record number (0-based)
                # <success> bool
                # <result> a dictionary like this one:
                #
                #   {
                #       'create': {
                #           'status': 201,
                #           '_type': 'billing',
                #           '_shards': {
                #               'successful': 1,
                #               'failed': 0,
                #               'total': 2
                #           },
                #           '_index': 'billing-2015-12',
                #           '_version': 1,
                #           '_id': u'AVOmiEdSF_o3S6_4Qeur'
                #       }
                #   }
                #
                if not success:
                    message = 'Failed to index record {:d} with result: {!r}'.format(recno, result)
                    if config.fail_fast:
                        raise ParserError(message)
                    else:
                        echo(message, err=True)
                else:
                    added += 1

    elif config.process_mode == PROCESS_BY_LINE:
        with progressbar(length=record_count) as pbar:
            csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)
            for recno, json_row in enumerate(csv_file):
                if is_control_message(json_row, config):
                    control += 1
                else:
                    if config.debug:
                        print(json.dumps(  # do not use 'echo()' here
                            utils.pre_process(
                                json.dumps(json_row, ensure_ascii=False, encoding=config.encoding)),
                            ensure_ascii=False, encoding=config.encoding))

                    if config.output_to_file:
                        file_out.write(json.dumps(utils.pre_process(
                            json.dumps(json_row, ensure_ascii=False, encoding=config.encoding))))
                        file_out.write('\n')
                        added += 1

                    elif config.output_to_elasticsearch:
                        if config.check:
                            # FIXME: the way it was, `search_exists` will not suffice, since we'll need the document _id for the update operation; # noqa
                            # FIXME: use `es.search` with the following sample body: `{'query': {'match': {'RecordId': '43347302922535274380046564'}}}`; # noqa
                            # SEE: https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.search; # noqa
                            response = es.search_exists(index=index_name, doc_type=config.es_doctype,
                                                        q='RecordId:{}'.format(json_row['RecordId']))
                            if response:
                                if config.update:
                                    # TODO: requires _id from the existing document
                                    # FIXME: requires use of `es.search` method instead of `es.search_exists`
                                    # SEE: https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.update; # noqa
                                    skipped += 1
                                else:
                                    skipped += 1
                            else:
                                response = es.index(index=index_name, doc_type=config.es_doctype,
                                                    body=body_dump(json_row, config))
                                if not es_index_successful(response):
                                    message = 'Failed to index record {:d} with result {!r}'.format(recno, response)
                                    if config.fail_fast:
                                        raise ParserError(message)
                                    else:
                                        echo(message, err=True)
                                else:
                                    added += 1
                        else:
                            response = es.index(index=index_name, doc_type=config.es_doctype,
                                                body=body_dump(json_row, config))
                            if not es_index_successful(response):
                                message = 'Failed to index record {:d} with result {!r}'.format(recno, response)
                                if config.fail_fast:
                                    raise ParserError(message)
                                else:
                                    echo(message, err=True)
                            else:
                                added += 1

                pbar.update(1)
    elif config.process_mode == PROCESS_BI_ONLY and config.analytics:
        echo('Processing Analytics Only')
        while thread.is_alive():
            # Wait for a timeout
            analytics_now = time.time()
            if analytics_start - analytics_now > config.analytics_timeout * 60:
                echo('Analytics processing timeout. exiting')
                break
            time.sleep(5)

    else:
        echo('Nothing to do!')

    file_in.close()

    if config.output_to_file:
        file_out.close()

    echo('Finished processing!')
    echo('')

    # the first line is the header then is skipped by the count bellow
    echo('Summary of documents processed...')
    echo('           Added: {}'.format(added))
    echo('         Skipped: {}'.format(skipped))
    echo('         Updated: {}'.format(updated))
    echo('Control messages: {}'.format(control))
    echo('')

    return Summary(added, skipped, updated, control)


def is_control_message(record, config):
    # <record> record dict
    # <config> an instance of `awsdbrparser.config.Config`
    # data = json.dumps(record, ensure_ascii=False, encoding=config.encoding)
    return utils.bulk_data(record, config.bulk_msg)


def body_dump(record, config):
    # <record> record dict
    # <config> an instance of `awsdbrparser.config.Config`
    body = json.dumps(utils.pre_process(json.dumps(record, ensure_ascii=False, encoding=config.encoding)),
                      ensure_ascii=False, encoding=config.encoding)
    return body


def es_index_successful(response):
    """
    Test if an Elasticsearch client ``index`` method response indicates a
    successful index operation. The response parameter should be a dictionary
    with following keys:

    .. sourcecode:: python

        {
            '_shards': {
                'total': 2,
                'failed': 0,
                'successful': 1
            },
            '_index': u'billing-2015-12',
            '_type': u'billing',
            '_id': u'AVOmKFXgF_o3S6_4PkP1',
            '_version': 1,
            'created': True
        }

    According to `Elasticsearch Index API <https://www.elastic.co/guide/en/
    elasticsearch/reference/current/docs-index_.html>`, an index operation is
    successful in the case ``successful`` is at least 1.

    :rtype: bool
    """
    return response.get('_shards', {}).get('successful', 0) >= 1
