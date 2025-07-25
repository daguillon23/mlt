import requests
import copy
import math

class Edgar:

    # initializes Edgar object with most recent data from url
    def __init__(self, url):

        # sets url, establishes headers, and requests json file from url
        self._url = url
        headers = {'user-agent': 'MLT DA diego.eaguillon@gmail.com'}
        req = requests.get(self._url, headers=headers)
        self._json = req.json()

        # dicts is a list of two dicts
        # index 0: name is key, info is value
        # index 1: ticker is key, info is value
        dicts = self._get_dicts()
        self._name_dict = dicts[0]
        self._tick_dict = dicts[1]

    # constructs dicts based on company data
    def _get_dicts(self):
        name_dict = {}
        tick_dict = {}

        for company in self._json['data']:

            cik = company[0]
            name = company[1]
            ticker = company[2]
            exchange = company[3]

            name_dict[name] = [cik, name, ticker, exchange]
            tick_dict[ticker] = [cik, name, ticker, exchange]

        return [name_dict, tick_dict]
    
    # returns company corresponding to name
    def name_to_cik(self, name):
        try:
            # do we care if the user edits the array since the info is refreshed with every cik.py call?
            return copy.deepcopy(self._name_dict[name])
        except:
            return 'Name not found.'
    
    # returns company corresponding to ticker
    def tick_to_cik(self, ticker):
        try:
            return copy.deepcopy(self._tick_dict[ticker])
        except:
            return 'Ticker not found.'
        
    # appends zeros to front of cik in order to meet 10 digits
    def _append_zeros(self, cik):
        BASE = 10
        # take log10 to calculate num digits in cik
        num_digits = int (math.log(cik, BASE)) + 1
        num_zeros = BASE - num_digits
        appended = ''
        for i in range(num_zeros):
            appended += '0'
        appended += str(cik)
        return appended
    
    # returns 10-K form for cik in year
    def annual_filing(self, cik, year):
        cik_append = self._append_zeros(cik)
        url = f'https://data.sec.gov/submissions/CIK{cik_append}.json'
        headers = {'user-agent': 'MLT DA diego.eaguillon@gmail.com'}
        req = requests.get(url, headers=headers)
        json = req.json()
        ind = 0
        for entry in json['filings']['recent']['primaryDocDescription']:
            
            ind += 1
        return ind
        # count digits in cik
        # append appropriate 0s to make 10 digits
        # make request to https://data.sec.gov/submissions/CIK##########.json
        # traverse primaryDocDescription array until you reach '10-K', keeping track of index
        # upon hit, check if corresponding entry in filingDate matches year
        #  
        # ind = array.index('10-K')
        # access accessionNumber and primaryDocument arrays using ind
        # input info into url for next request
        # https://www.sec.gov/Archives/edgar/data/{CIK}/{accessionNumber}/{primaryDocument}
        # return this doc
        return 0
    
    #returns 10-Q for cik in quarter of year
    def quarterly_filing(self, cik, year, quarter):
        return 0


def cik_tests(sec):
    print(sec.name_to_cik('Apple Inc.'))
    print(sec.tick_to_cik('GOOGL'))
    print(sec.name_to_cik('doesnt exist'))
    print(sec.tick_to_cik('doesnt exist'))

def filing_tests(sec):
    # testing with Apple info
    print(sec.annual_filing(320193, 2014))
    print(sec.annual_filing())
    print(sec.annual_filing('doesnt exist', 0))
    print(sec.quarterly_filing(320193, 0, 0))


sec = Edgar('https://www.sec.gov/files/company_tickers_exchange.json')

print(sec.annual_filing(320193, 2014))
#cik_tests(sec)
#filing_tests(sec)
