#!/usr/bin/python
# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


''' AWS Detailed Billing parser to Logstash/ElasticSearch '''

__author__ = 'Rafael M. Koike'
__version__ = '0.3.0'
__date__ = '2015-10-15'
__maintainer__ = 'Rafael M. Koike'
__email__ = 'koiker@amazon.com'
__status__ = 'Development'

import argparse
import csv
import json
import os
import sys

from datetime import datetime

from elasticsearch import Elasticsearch

import config
import functions as func

DEBUG = 0

OUTPUT_TO_FILE = 1
OUTPUT_TO_ELASTICSEARCH = 2


def parse(args):

    # FIXME: remove (completely or partially) config module;
    # NOTE: passing values from args to config just to keep things as it was before argparser was introduced;
    config.csv_filename = args.input
    config.json_filename = args.output
    config.es_host = args.elasticsearch_host
    config.es_port = args.elasticsearch_port
    config.account_id = args.account_id
    config.es_year = args.year
    config.es_month = args.month
    config.output = args.output_type
    config.csv_delimiter = args.csv_delimiter

    if config.json_filename is None:
        # use same name as the input file, but with '.json' extension
        name, extension = os.path.splitext(config.csv_filename)
        config.json_filename = '{}.json'.format(name)

    print( "AWS - Detailed Billing Records parser \n\n")

    config.es_index = '{}-{:d}-{:d}'.format(
            config.es_index,
            config.es_year,
            config.es_month)

    #Open input and output (file or elasticsearch) to work
    try:
        print( "Opening Input file: {0}\n".format(config.csv_filename) )
        file_in = open( config.csv_filename, 'rb')
    except IOError as e:
        print( "I/O error({0}): {1}".format(e.errno, e.strerror) )
        sys.exit(2)
    except:
        print( "Unexpected error:", sys.exc_info()[0] )
        sys.exit(2)

    if config.output == 1:
        try:
            print( "Opening Output file: {0}\n".format(config.json_filename) )
            file_out = open( config.json_filename, 'wb')
        except IOError as e:
            print( "I/O error({0}): {1}".format(e.errno, e.strerror) )
            sys.exit(2)
        except:
            print( "Unexpected error:", sys.exc_info()[0] )
            sys.exit(2)

    elif config.output == 2:
        print( "Sending DBR to Elasticsearch host: {0} Port: {1}".format( config.es_host, config.es_port ) )
        es = Elasticsearch( [{'host': config.es_host, 'port': config.es_port}])
        es.indices.create( config.es_index, ignore=400 )
        es.indices.put_mapping( index=config.es_index, doc_type=config.es_doctype, body=config.mapping)


    row_count = sum(1 for row in file_in)
    print( "The Input file has {0} records".format(row_count) )
    file_in.seek(0) #Move the file pointer to the START again
    print( 'Output to file' if config.output == 1 else 'Output to Elasticsearch')
    print( "Parsing CSV file to JSON" )
    csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)
    pb = func.ProgressBar( barsize=50,barmax=row_count,drawperc=True,empty=' ')
    pb.initialize()
    i=1
    for json_row in csv_file:
        if not func.bulk_data( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) , config.bulk_msg ):
            if DEBUG: print( json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ),ensure_ascii=False, encoding=config.encoding ) )
            if config.output == 1:
                file_out.write( json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ) ) )
                file_out.write('\n')
            elif config.output == 2:
                es.index( index=config.es_index, doc_type=config.es_doctype, body=json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ), ensure_ascii=False, encoding=config.encoding ) )
        i=i+1
        pb.update(i) # Update Progressbar

    pb.done() #Finish Progressbar
    print( "Finished processing..." )
    file_in.close()
    if config.output == 1:
        print( "Closing Output file." )
        file_out.close()


if __name__ == '__main__':

    now = datetime.now()

    parser = argparse.ArgumentParser(description='AWS detailed billing parser to Logstash or ElasticSearch')
    parser.add_argument('-i', '--input', required=True, help='Input file (expected to be a CSV file)')
    parser.add_argument('-o', '--output', help='Output file (will generate a JSON file)')
    parser.add_argument('-e', '--elasticsearch-host', metavar='HOST', help='Elasticsearch host name or IP address')
    parser.add_argument('-p', '--elasticsearch-port', type=int, metavar='PORT', help='Elasticsearch port number')
    parser.add_argument('-a', '--account-id', help='AWS Account-ID (Default is 012345678901)')
    parser.add_argument('-y', '--year', type=int, help='Year for the index (uses current year if not provided)')
    parser.add_argument('-m', '--month', type=int, help='Month for the index (uses current month if not provided)')
    parser.add_argument('-t', '--output-type', type=int,
            choices=[OUTPUT_TO_FILE, OUTPUT_TO_ELASTICSEARCH,],
            help='Output type ({}=Output to file, {}=Elasticsearch)'.format(
                    OUTPUT_TO_FILE,
                    OUTPUT_TO_ELASTICSEARCH))
    parser.add_argument('-d', '--csv-delimiter', help='CSV delimiter (default is comma)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.set_defaults(
            elasticsearch_host='search-name-hash.region.es.amazonaws.com',
            elasticsearch_port=80,
            year=now.year,
            month=now.month,
            output_type=OUTPUT_TO_FILE,
            csv_delimiter=',')

    args = parser.parse_args()
    parse(args)
