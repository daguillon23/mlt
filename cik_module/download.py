import boto3
import requests

BUCKET = "aguillon-tickers"
KEY = 'company_tickers_exchange.json'

def lambda_handler(event, context):
    url = event['url']
    HEADERS = event['headers']
    response = requests.get(url, headers=HEADERS)
    s3 = boto3.client('s3')

    # creates bucket
    #bucket = s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "us-east-2"})
    
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=response.content)

    # prints body of key in bucket
    #print(s3.get_object(Bucket=BUCKET, Key=KEY)['Body'].read())

    return {
        'statusCode': 200,
        'body': "EDGAR UPLOAD SUCCESS"
    }
