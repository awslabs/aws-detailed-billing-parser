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

import datetime
''' Configuration file of AWS Detailed Billing Report parser '''

__author__ = "Rafael M. Koike"
__version__ = "0.2.3"
__date__ = "2015-10-15"
__maintainer__ = "Rafael M. Koike"
__email__ = "koiker@amazon.com"
__status__ = "Development"

# Default arguments if not specified in the cli
today = datetime.date.today()
es_host = 'search-name-hash.region.es.amazonaws.com' # Replace this for the ElasticSearch endpoint/hostname
es_port = 80 # Default port for AWS ElasticSearch, buy if you wil use with standard installation you should use 9200
es_index = 'billing'
es_doctype = 'billing'
es_year = str( datetime.datetime.now().year )
es_month = str( datetime.datetime.now().month )
es_timestamp = 'UsageStartDate' #fieldname that will be replaced by Timestamp
es_index_delete = 0
account_id = '01234567890'
csv_filename = account_id + '-' + 'aws-billing-detailed-line-items-with-resources-and-tags-' + str(es_year) + '-' + str(es_month) + '.csv'
csv_delimiter = ','
encoding = 'utf-8'  #This is the default encoding for most part of the files, but sometimes if the customer use latin/spanish characters you will need to change.
encoding = 'iso-8859-1'
bulk_mode = 0
bulk_size = 10000
update = False #True = Try to update existing documents in Elasticsearch index (Default to false to speed up)
check = False #True = Check if the current record exists before add new. (For incremental updates)
json_filename = csv_filename.split('.')[0] + '.json'

output = 1   # 1 = file output, 2 = elasticsearch output
es_dbr = {
	"billing" : {
		"properties" : {
			es_timestamp : {"type" : "date"}
		}
	}
}
bulk_msg = {"RecordType" : [ "StatementTotal", "InvoiceTotal", "Rounding", "AccountTotal" ]}

mapping = {
	es_doctype: {
        # _timestamp has been deprecated since Elasticsearch 2.0.0-beta2
        # If you will run this script with Elasticsearch 2.0.0-beta2 or above you must comment the line below.
		#"_timestamp": {"enabled": "true", "path": es_timestamp, "format" : "YYYY-MM-dd HH:mm:ss"},
		"properties": {
			"LinkedAccountId": { "type": "string" },
    		"InvoiceID": { "type": "string", "index" : "not_analyzed" },
    		"RecordType": { "type": "string" },
    		"RecordId": { "type": "string", "index" : "not_analyzed" },
    		"UsageType": { "type": "string", "index" : "not_analyzed" },
    		"UsageEndDate": { "type": "date", "format" : "YYYY-MM-dd HH:mm:ss" },
    		"ItemDescription": { "type": "string", "index" : "not_analyzed" },
    		"ProductName": { "type": "string", "index" : "not_analyzed" },
    		"RateId": { "type": "string" },
    		"Rate": { "type": "float" },
    		"AvailabilityZone": { "type": "string", "index" : "not_analyzed" },
    		"PricingPlanId": { "type": "string", "index" : "not_analyzed"},
    		"ResourceId": { "type": "string", "index" : "not_analyzed" },
    		"Cost": { "type": "float" },
    		"PayerAccountId": { "type": "string", "index" : "not_analyzed" },
    		"SubscriptionId": { "type": "string", "index" : "not_analyzed" },
    		"UsageQuantity": { "type": "float" },
    		"Operation": { "type": "string" },
    		"ReservedInstance": { "type": "string", "index" : "not_analyzed" },
    		"UsageStartDate": { "type": "date", "format" : "YYYY-MM-dd HH:mm:ss" },
            "BlendedCost" : { "type": "float" },
            "BlendedRate" : { "type": "float" },
            "UnBlendedCost" : { "type": "float" },
            "UnBlendedRate" : { "type": "float" }
		}
	}
}
