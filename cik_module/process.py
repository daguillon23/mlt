import json
import cik
import boto3

# must fill out header with your own info. bucket with your bucket name
ORG = None
INITIAL = None
EMAIL = None
BUCKET = None

HEADERS = {'user-agent': f'{ORG} {INITIAL} {EMAIL}'}
KEY = "company_tickers_exchange.json"

def lambda_handler(event, context):
    try:
        '''
        expected format:
        {
            "ticker": "NVDA",
            "year": "2021",
            "quarter": "3"
        }
        '''
        sec = cik.Edgar(BUCKET, KEY, HEADERS)

        # receive input as JSON
        # parse input for ticker, year, quarter 
        ticker = event['ticker']
        year = int(event['year'])
        quarter = int(event['quarter'])

        if quarter == 4:
            doc = sec.annual_filing(sec.tick_to_cik(ticker)[0], year)
        else:
            doc = sec.quarterly_filing(sec.tick_to_cik(ticker)[0], year, quarter)

        return {
            'statusCode': 200,
            'body': json.dumps(doc)
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'statusCode': 400,
            'body': "Bad Request"
        }
