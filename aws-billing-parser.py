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
__version__ = '0.3.3'
__date__ = '2015-10-15'
__maintainer__ = 'Rafael M. Koike'
__email__ = 'koiker@amazon.com'
__status__ = 'Development'

import argparse
import boto3
import csv
import json
import os
import sys
import time

from datetime import datetime
from datetime import timedelta

from elasticsearch import Elasticsearch, helpers

import config
import functions as func

DEBUG = 0

OUTPUT_TO_FILE = 1
OUTPUT_TO_ELASTICSEARCH = 2

PROCESS_BY_LINE = 0
PROCESS_BY_BULK = 1

INDEX_KEEP = 0
INDEX_DELETE = 1


def parse(args):

    # FIXME: remove (completely or partially) config module;
    # NOTE: passing values from args to config just to keep things as it was before argparser was introduced;
    config.csv_filename = args.input
    config.json_filename = args.output
    config.es_host = args.elasticsearch_host
    config.es_port = args.elasticsearch_port
    config.es_index = args.elasticsearch_index
    config.account_id = args.account_id
    config.es_year = args.year
    config.es_month = args.month
    config.output = args.output_type
    config.csv_delimiter = args.csv_delimiter
    config.update = args.update
    config.check = args.check
    config.bulk_mode = args.bulk_mode
    config.bulk_size = args.bulk_size
    config.es_index_delete = args.delete_index

    if config.json_filename is None:
        # use same name as the input file, but with '.json' extension
        name, extension = os.path.splitext(config.csv_filename)
        config.json_filename = '{}.json'.format(name)

    print( "    ___      _____ ___  ___ ___ ___                      ")
    print( "   /_\ \    / / __|   \| _ ) _ \ _ \__ _ _ _ ___ ___ _ _ ")
    print( "  / _ \ \/\/ /\__ \ |) | _ \   /  _/ _` | '_(_-</ -_) '_|")
    print( " /_/ \_\_/\_/ |___/___/|___/_|_\_| \__,_|_| /__/\___|_| \n")
    print( "AWS - Detailed Billing Records parser \n\n")                                                    

    config.es_index = '{}-{:d}-{:0>2d}'.format(
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
        if config.es_index_delete:
            print( "Deleting current index: {}".format( config.es_index ) )
            es.indices.delete( config.es_index, ignore=404 )
        es.indices.create( config.es_index, ignore=400 )
        es.indices.put_mapping( index=config.es_index, doc_type=config.es_doctype, body=config.mapping)

    row_count = sum(1 for row in file_in)
    print( "The Input file has {0} records".format(row_count) )
    file_in.seek(0) #Move the file pointer to the START again
    print( 'Output to file' if config.output == 1 else 'Output to Elasticsearch')
    print( 'Processing in BULK MODE' if config.bulk_mode else 'Processing in LINE MODE')
    if config.bulk_mode: print( "Bulk size: {}".format(config.bulk_size) )
    pb = func.ProgressBar( barsize=50,barmax=row_count,drawperc=True,empty=' ')
    pb.initialize()
    i=1
    new = exists = updated = control = 0
    if config.bulk_mode:    
        #If you wish to sort the records by UsageStartDate before send to ES just uncomment the 2 lines below and comment the third line
        #reader = csv.DictReader(file_in, delimiter=config.csv_delimiter)
        #csv_file = sorted(reader, key=lambda line: line["UsageStartDate"]+line["UsageEndDate"])
        csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)
        def documents():
            for json_row in csv_file:
                if not func.bulk_data( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) , config.bulk_msg ):
                    if DEBUG: print( json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ),ensure_ascii=False, encoding=config.encoding ) )
                    pb.update(i)
                    yield func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ))

        for ok, result in helpers.streaming_bulk(es, documents(), index=config.es_index, doc_type=config.es_doctype, chunk_size=config.bulk_size):
            i = i+1
            new = new+1
            pb.update(i)
            if not ok:
                print('Failed to index', doc)
    else:
        csv_file = csv.DictReader(file_in, delimiter=config.csv_delimiter)
        
        for json_row in csv_file:
            if not func.bulk_data( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) , config.bulk_msg ):
                if DEBUG: print( json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ),
                    ensure_ascii=False, encoding=config.encoding ) )
                if config.output == 1:
                    new = new + 1
                    file_out.write( json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ) ) )
                    file_out.write('\n')
                elif config.output == 2:
                    try:
                        if config.check:
                            response = es.search_exists( index=config.es_index, doc_type=config.es_doctype, q='RecordId:'+ json_row['RecordId'])
                            if response:
                                if config.update:
                                    updated = updated + 1
                                    print( 'Updating record: (ToDo)' + json_row['RecordId'])
                                else:
                                    exists = exists + 1    
                            else:
                                try:
                                    es.index( index=config.es_index, doc_type=config.es_doctype, 
                                        body=json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ), 
                                            ensure_ascii=False, encoding=config.encoding ) )
                                    new = new + 1
                                except:
                                    print( 'Error adding: ' + json.dumps( json_row) )
                        else:
                            new = new + 1
                            es.index( index=config.es_index, doc_type=config.es_doctype, 
                                body=json.dumps( func.split_subkeys( json.dumps( json_row, ensure_ascii=False, encoding=config.encoding ) ), 
                                    ensure_ascii=False, encoding=config.encoding ) )
                    except:
                        print( 'Error adding: ' + json.dumps( json_row) )
            else:
                control = control + 1
            i=i+1
            pb.update(i) # Update Progressbar
    pb.done() #Finish Progressbar
    print( "Finished processing...\n" )
    #The first line is the header then is skipped by the count bellow
    print( "Documents Processed [Added]  : {0}".format(new) )
    print( "                    [Skipped]: {0}".format(exists) )
    print( "                    [Updated]: {0}".format(updated) )
    print( "Control messages             : {0}\n".format(control))
    file_in.close()
    if config.output == 1:
        print( "Closing Output file." )
        file_out.close()


if __name__ == '__main__':

    now = datetime.now()
    start_time = time.time()

    parser = argparse.ArgumentParser(description='AWS detailed billing parser to Logstash or ElasticSearch')
    parser.add_argument('-i', '--input', required=True, help='Input file (expected to be a CSV file)')
    parser.add_argument('-o', '--output', help='Output file (will generate a JSON file)')
    parser.add_argument('-e', '--elasticsearch-host', metavar='HOST', help='Elasticsearch host name or IP address')
    parser.add_argument('-p', '--elasticsearch-port', type=int, metavar='PORT', help='Elasticsearch port number')
    parser.add_argument('-ei', '--elasticsearch-index', help='Elasticsearch index prefix')
    parser.add_argument('-a', '--account-id', help='AWS Account-ID (Default is 012345678901)')
    parser.add_argument('-y', '--year', type=int, help='Year for the index (uses current year if not provided)')
    parser.add_argument('-m', '--month', type=int, help='Month for the index (uses current month if not provided)')
    parser.add_argument('-t', '--output-type', type=int,
            choices=[OUTPUT_TO_FILE, OUTPUT_TO_ELASTICSEARCH,],
            help='Output type ({}=Output to file, {}=Elasticsearch)'.format(
                    OUTPUT_TO_FILE,
                    OUTPUT_TO_ELASTICSEARCH))
    parser.add_argument('-d', '--csv-delimiter', help='CSV delimiter (default is comma)')
    parser.add_argument('-di', '--delete-index', type=int,
            choices=[INDEX_KEEP, INDEX_DELETE,], 
            help='Delete current index before processing (default is keep)')
    parser.add_argument('-bm', '--bulk-mode', type=int,
            choices=[PROCESS_BY_LINE, PROCESS_BY_BULK,], 
            help='Send DBR line-by-line or in bulk (1=Bulk and 0=Line), default to False')
    parser.add_argument('-bs', '--bulk-size', type=int, metavar='BULK_SIZE', 
            help='Define the size o bulk to send (default=10000)')
    parser.add_argument('-u', '--update', action='store_true', 
            help='Update if current record exist in ES before add (Must use with --check)')
    parser.add_argument('-c', '--check', action='store_true', 
            help='Check if current lines exist in ES before add (If using bulk mode this option won\'t work)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.set_defaults(
            elasticsearch_host='search-name-hash.region.es.amazonaws.com',
            elasticsearch_port=80,
            elasticsearch_index='billing',
            year=now.year,
            month=now.month,
            output_type=OUTPUT_TO_FILE,
            delete_index=0,
            bulk_mode=0,
            bulk_size=10000,
            csv_delimiter=',')

    args = parser.parse_args()
    parse(args)
    elapsed_time = time.time() - start_time
    print( 'Elapsed time: ' + str( timedelta( seconds=elapsed_time ) ) )
