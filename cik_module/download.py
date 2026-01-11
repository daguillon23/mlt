import boto3
import requests
import json

# replace with your bucket name
BUCKET = None
KEY = 'company_tickers_exchange.json'

def lambda_handler(event, context):
    try:

        url = "https://www.sec.gov/files/company_tickers_exchange.json"
        HEADERS = {"user-agent": "MLT DA diego.eaguillon@gmail.com"}
        response = requests.get(url, headers=HEADERS)
        s3 = boto3.client('s3')

        # creates bucket
        #bucket = s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "us-east-2"})
        
        s3.put_object(Bucket=BUCKET, Key=KEY, Body=response.content)

        # prints body of key in bucket
        # print(s3.get_object(Bucket=BUCKET, Key=KEY))
        # print(s3.get_object(Bucket=BUCKET, Key=KEY)['Body'][0])
        print("EDGAR UPLOAD SUCCESS")
        return {
            'statusCode': 200,
            'body': "EDGAR UPLOAD SUCCESS"
        }
    except Exception as e:
        print(f"ERROR: {e}")
