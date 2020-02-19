import sys
import botocore
import boto3
import json
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    rds = boto3.client('rds')
    lambdaFunc = boto3.client('lambda')
    response = rds.describe_db_clusters(
        DBClusterIdentifier='string',
        MaxRecords=123,
        Marker='string',
        IncludeShared=True|False
    )
    return response
    print (response)
    json.loads
    return
    {
        'message' : "Script execution completed. See Cloudwatch logs for complete output"
    }