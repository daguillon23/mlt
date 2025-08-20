import json
import cik

HEADERS = {'user-agent': 'MLT DA diego.eaguillon@gmail.com'}
BUCKET = "aguillon-tickers"
KEY = "company_tickers_exchange.json"

def lambda_handler(event, context):
    try:
        # TODO implement
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
