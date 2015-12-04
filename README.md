<<<<<<< HEAD
# AWS detailed billing parser #
Author: Rafael M. Koike

AWS ProServe

e-mail: koiker@amazon.com

This script was created to support the automatic parse of detailed billing records to JSON format or directly to ElasticSearch

Requirements:
- Python >= 2.7
- Python ElasticSearch import
- aws-sdk (For future use with S3 integration)


Instalation Instructions:
- I will consider that you already have installed the requirements above :-)
- Copy the import_csv.py to a folder (ex: /aws-billing)
- Copy the AWS DBR (Detailed Billing Records) 0123456789012-aws-billing-detailed-line-items-with-resources-and-tags-2015-00.csv
* This version still doesn't support zip extraction of the files from the S3 bucket
- Change to exectutable the file: chmod +x import_csv.py if you are running in Linux

Execute:
- Edit the script to point to your ElasticSearch if you are going to send directly to ES service
- execute the program ./import_csv.py -i <0123456789012-aws-billing-detailed-line-items-with-resources-and-tags-2015-XX.csv>

If you will save the file in JSON format and export later with the bulk function of ElasticSearch you must change the variable output=1 in the script



*TODO
- Parse the arguments:
* Output (1 = file/ 2 = ElasticSearch)
* ES Host (search-name-hash.region.es.amazon.com or any other ElasticSearch server)
* ES port (9200 for standard ElasticSearch installations or 80 for AWS ElasticSearch:defaut to 80 now)
* Unzip (Extract the DBR from zip file)
* S3 (Copy the source file from S3 bucket to local folder to process)

- Incremental updates
The DBR of the current month is incremental, so you have the same file updated many times per day.
We must process the file and save a diff or already processed rows someware, the next time that you execute the program the already processed rows must be skiped to avoid multiples entries in the ElasticSearch.
At this time if you want to avoid that you must delete the index (billing-YYYY.MM) and run again (All registers will be recreated)

- Lambda compatible
To be compatible with Lambda i must run in max 5min and depending on the size of the file this won't be possible, so i will probably need to include a new argument like: MAX ROWS and every call to lambda will process a maximum of 10000 rows for exemple. This will give us a previsibility that lambda will work in the correct timeframe.



version 0.1 - 2015-10-17
* Initial version


Version 0.2 - 2015-10-26
* Filter of control messages (Stop the error in the end of processing)
* Verbose output of the processing
* Progresbar
* Output options: 1 = file / 2 = ElasticSearch
* ElasticSearch Mapping
=======
# aws-detailed-billing-parser
Python script to parse the Detailed Billing Reports to Elasticsearch or .json file 
>>>>>>> 069fee85be14dd9f43331708dd99d0d13f0ac993
