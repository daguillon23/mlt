import requests
import copy
import math

def NOT_FOUND(type):
    return f'{type} not found.'

HEADERS = {'user-agent': 'MLT DA diego.eaguillon@gmail.com'}

class Edgar:
    # initializes Edgar object with most recent data from url
    def __init__(self, url):

        # sets url, establishes headers, and requests json file from url
        self._url = url
        req = requests.get(self._url, headers=HEADERS)
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
        if name not in self._name_dict:
            return NOT_FOUND('Name')
        # returning copy to maintain encapsulation.
        # do we care if the user edits the array since the info is refreshed with every cik.py call?
        return copy.deepcopy(self._name_dict[name])

    # returns company corresponding to ticker
    def tick_to_cik(self, ticker):
        if ticker not in self._tick_dict:
            return NOT_FOUND('Ticker')
        return copy.deepcopy(self._tick_dict[ticker])

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
    
    # returns 'recent' array from EDGAR for filing use
    def _get_recent(self, cik):
        cik_append = self._append_zeros(cik)
        url = f'https://data.sec.gov/submissions/CIK{cik_append}.json'
        req = requests.get(url, headers=HEADERS)
        try:
            return req.json()['filings']['recent']
        except:
            return NOT_FOUND('CIK')
        
    # helper method to find 10-Q form.
    # assumes company properly files 3 10-Qs per fiscal year.
    def _quarter_search(self, recent, year, quarter, start):
        # counts down from prev year's 10-K.
        # counts 10-Qs found until num matches 'quarter'.
        # if date of entry exceeds 'year' or array runs out of entries, returns -1.
        # returns index of 10-Q form upon success.
        num_q = 0
        doc_type = '10-Q'
        ind = -1
        for i in range(start, -1, -1):
            entry = recent['primaryDocDescription'][i]
            if (doc_type in entry):
                num_q += 1
                if str(year) not in recent['filingDate'][i]:
                    # 10-Q in 'year' not found
                    break
                if (num_q == quarter):
                    ind = i
                    break
        return ind

    # returns 10-K form for 'cik' in 'year'.
    def annual_filing(self, cik, year):
        return self.quarterly_filing(cik, year, 4)

    # returns 10-Q/10-K form for 'cik' in 'quarter' of 'year'.
    # expect 'quarter' to be between 1 and 4 for user simplicity.
    # 'quarter' of 4 represents 10-K request.
    # 'quarter' of 1 through 3 represents 10-Q request.
    def quarterly_filing(self, cik, year, quarter):
        
        # verify arguments
        k_search = False
        if (not isinstance(year, int)) or (year < 1900):
            return 'Invalid year.'
        if not isinstance(cik, int):
            return 'Invalid CIK.'
        if (quarter == 4):
            # indicates user is searching for 10-K form
            k_search = True
        elif (quarter < 1) or (quarter > 4):
            return 'Invalid quarter.'

        recent = self._get_recent(cik)
        ind = 0
        found_k = False
        doc_type = '10-K'
    
        # if searching for 10-Q, search for 10-K from (year - 1) first. 
        year_search = year
        if not k_search:
            year_search -= 1

        for entry in recent['primaryDocDescription']:
            # if correct doc and correct year, 10-K found
            if (doc_type in entry) and (str(year_search) in recent['filingDate'][ind]):
                found_k = True
                break
            ind += 1
        if not found_k:
            return NOT_FOUND('10-K')
        
        # if 10-K requested, search complete.
        # if 10-Q requested, must find using prev year's 10-K as starting point.
        if not k_search:
            ind = self._quarter_search(recent, year, quarter, ind)
            if ind == -1:
                return NOT_FOUND('10-Q')
        
        # create url and make request
        access_num = recent['accessionNumber'][ind].replace('-', '')
        prim_doc = recent['primaryDocument'][ind]
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{access_num}/{prim_doc}'
        req = requests.get(url, headers=HEADERS)

        # for testing purposes
        #return url

        return req.text
        # TODO use markdown to remove unnecessary characters for easier use by LLM


def cik_tests(sec):
    print('CIK LOOKUP TESTS')
    print(sec.name_to_cik('Apple Inc.'))
    print(sec.tick_to_cik('GOOGL'))
    print(sec.name_to_cik('doesnt exist'))
    print(sec.tick_to_cik('doesnt exist'))
    print(' ')

def filing_tests(sec):
    # testing with Apple info
    print('EDGAR API TESTS')
    print('annual')
    # should succeed
    print(sec.annual_filing(320193, 2024))
    print(sec.annual_filing(320193, 2014))
    # errors should be handled
    print(sec.annual_filing(320193, 1904))
    print(sec.annual_filing(320193, 0))
    print(sec.annual_filing('doesnt exist', 2024))
    print(' ')

    print('quarterly')
    # should succeed
    print(sec.quarterly_filing(320193, 2025, 1))
    print(sec.quarterly_filing(320193, 2022, 3))
    print(sec.quarterly_filing(320193, 2020, 4))
    # errors should be handled
    print(sec.quarterly_filing(320193, 2025, 3))
    print(sec.quarterly_filing(320193, 2015, 5))
    print(' ')


sec = Edgar('https://www.sec.gov/files/company_tickers_exchange.json')

#cik_tests(sec)
#filing_tests(sec)

