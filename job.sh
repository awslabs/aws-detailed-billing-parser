#!/bin/bash

function usage
{
    echo "usage: job [[-pm] | [-h]]"
    echo "Parameters:"
    echo "-pm | --previous-month = process the previous month from current date"
}

BUCKET='s3://bucket-123456'
ACCOUNT='123456789012'
YEAR=$(date +%Y)
MONTH=$(date +%m)
LOCAL_FOLDER='/mnt/jobs'

ES_HOST='elastic-search-host.endopoint.name'
ES_PORT=80

# Process input parameters
while [ "$1" != "" ]; do
    case $1 in
        -pm | --previous-month )echo "Processing previous month!" 
				MONTH=$(date --date='-1 month' +%m)
				YEAR=$(date --date='-1 month' +%Y)
                                ;;
        -h | --help )           usage
                                exit
                                ;;
    esac
    shift
done

DBR_FILE=$ACCOUNT-aws-billing-detailed-line-items-with-resources-and-tags-$YEAR-$MONTH.csv
ZIP_FILE=$DBR_FILE.zip

#Change to local working folder
cd $LOCAL_FOLDER

# Copy the file from bucket to local folder
aws s3 cp $BUCKET/$ZIP_FILE .

# Extract the ziped file
unzip -o  $ZIP_FILE

# Process the file with dbrparser
dbrparser -i $DBR_FILE -e $ES_HOST -p $ES_PORT -t 2 -bm 2 -y $YEAR -m $MONTH --delete-index

# Remove processed file
rm $DBR_FILE
rm $ZIP_FILE

echo 'Finished processing...'
