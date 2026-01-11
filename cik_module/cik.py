import requests
import copy
import math
from markdownify import markdownify as md
import codecs
from bs4 import BeautifulSoup

# must fill out header with your own info
ORG = None
INITIAL = None
EMAIL = None

def NOT_FOUND(type):
    return f'{type} not found.'

HEADERS = {'user-agent': f'{ORG} {INITIAL} {EMAIL}'}
URL = 'https://www.sec.gov/files/company_tickers_exchange.json'

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
    
    # returns json from EDGAR for filing use
    def _get_json(self, cik):
        cik_append = self._append_zeros(cik)
        url = f'https://data.sec.gov/submissions/CIK{cik_append}.json'
        req = requests.get(url, headers=HEADERS)
        try:
            return req.json()
        except:
            return NOT_FOUND('CIK')
        
    # helper method to find 10-Q form.
    # assumes company properly files 3 10-Qs per fiscal year.
    def _quarter_search(self, recent, quarter, start, end, step):
        # counts step from given year's 10-K.
        # counts 10-Qs found until num matches 'quarter'.
        # if date of entry exceeds 'year' or array runs out of entries, returns -1.
        # returns index of 10-Q form upon success.

        
        num_q = 0
        if step == 1:
            # if searching chronologically backwards (forward through array),
            # need to account for fact that 10-Qs will appear backwards too 
            num_q = 4
        doc_type = '10-Q'
        ind = -1
        for i in range(start, end, step):
            entry = recent['primaryDocDescription'][i]
            if (doc_type in entry):
                num_q -= step
                if (num_q == quarter):
                    ind = i
                    break
        return ind

    # returns 10-K form for 'cik' in 'year'.
    def annual_filing(self, cik, year):
        return self.quarterly_filing(cik, year, 4)
    
    def _get_filing_month(self, recent, ind):
        date = recent['filingDate'][ind]
        month = int(date[5:7])
        return month
    
    def _find_k(self, year_search, recent, ind, filing_month, FISCAL_CUTOFF):
        after_june = (str(year_search) in recent['filingDate'][ind]) and (filing_month >= FISCAL_CUTOFF)
        before_june = (str(year_search + 1) in recent['filingDate'][ind]) and (filing_month < FISCAL_CUTOFF)
        return after_june or before_june

    # returns 10-Q/10-K form for 'cik' in 'quarter' of 'year'.
    # expect 'quarter' to be between 1 and 4 for user simplicity.
    # 'quarter' of 4 represents 10-K request.
    # 'quarter' of 1 through 3 represents 10-Q request.
    def quarterly_filing(self, cik, year, quarter):
        # verify arguments.
        FISCAL_CUTOFF = 6
        # 10-K will be published in following year (i.e. 2024 10-K published in 2025).
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

        json = self._get_json(cik)

        recent = json['filings']['recent']
        ind = 0
        doc_type = '10-K'
        prev_k_found = False

        for entry in recent['primaryDocDescription']:
            # if correct doc and 
            # 1. year found & filing date after june (i.e. fiscal year takes up majority of calendar year) or
            # 2. year + 1 found & filing date before june
            # then 10-K found
            if (doc_type in entry):
                filing_month = self._get_filing_month(recent, ind)
                
                if not k_search:
                    # if a quarter search, will begin search at previous year's 10-K
                    prev_k_found = self._find_k(year - 1, recent, ind, filing_month, FISCAL_CUTOFF)
                curr_k_found = self._find_k(year, recent, ind, filing_month, FISCAL_CUTOFF)

                if curr_k_found:
                    curr_ind = ind
                    if k_search:
                        break
                if (not k_search) and prev_k_found:
                    break
            ind += 1
        if (not curr_k_found) and (not prev_k_found):
            return NOT_FOUND('10-K')
        
        # if 10-K requested, search complete.
        # if 10-Q requested, must find using prev year's 10-K as starting point.
        # possible that previous year's 10-K does not exist. in that case,
        # use this year as starting point and search forwards (chronologically backwards).
        if not k_search:
            if prev_k_found:
                ind = self._quarter_search(recent, quarter, ind, -1, -1)
            else:
                # if previous 10-K wasnt found, use this year's 10-K as starting point
                # and search forward through array
                ind = self._quarter_search(recent, quarter, curr_ind, len(recent['primaryDocDescription']), 1)
            
            if ind == -1:
                return NOT_FOUND('10-Q')
        
        # create url and make request
        access_num = recent['accessionNumber'][ind].replace('-', '')
        prim_doc = recent['primaryDocument'][ind]
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{access_num}/{prim_doc}'
        req = requests.get(url, headers=HEADERS)
        #req.encoding = "utf-8"
        #return md(req.text)
        #"iso-8559-1"
        result = req.content.decode(req.encoding, errors='replace')
        print(result)
        result = result.encode("utf-8")
        return md(result)
        #return req.text
        # for testing purposes
        #return url
        #soup = BeautifulSoup(req.text.encode('ascii', errors='replace'), "html.parser")
        #return soup.prettify()
        #req.text
        #return req.encoding
        return md(req.text.encode('utf-8', errors='replace'))
        #return md(req.text.encode('utf-8', errors='ignore')).encode('utf-8', errors='ignore')


def cik_tests(sec):
    print('CIK LOOKUP TESTS')
    print(sec.name_to_cik('Apple Inc.'))
    print(sec.tick_to_cik('GOOGL'))
    print(sec.name_to_cik('doesnt exist'))
    print(sec.tick_to_cik('doesnt exist'))
    print(' ')

def filing_tests(sec):
    nvidia_cik = sec.name_to_cik('NVIDIA CORP')[0]
    google_cik = sec.tick_to_cik('GOOGL')[0]
    apple_cik = sec.name_to_cik('Apple Inc.')[0]
    print('EDGAR API TESTS')
    print('annual')
    # should succeed
    print(sec.annual_filing(nvidia_cik, 2024))
    print(sec.annual_filing(google_cik, 2022))
    # errors should be handled
    print(sec.annual_filing(apple_cik, 1904))
    print(sec.annual_filing(google_cik, 0))
    print(sec.annual_filing('doesnt exist', 2024))
    print(' ')

    print('quarterly')
    # should succeed
    print(sec.quarterly_filing(apple_cik, 2025, 1))
    print(sec.quarterly_filing(google_cik, 2022, 3))
    print(sec.quarterly_filing(nvidia_cik, 2020, 4))
    # errors should be handled
    print(sec.quarterly_filing(google_cik, 2025, 3))
    print(sec.quarterly_filing(nvidia_cik, 2015, 5))
    print(' ')

    year = 2024
    quarter = 4
    print(sec.quarterly_filing(nvidia_cik, year, quarter))
    print(sec.quarterly_filing(google_cik, year, quarter))
    print(sec.quarterly_filing(apple_cik, year, quarter))


sec = Edgar(URL)
nvidia_cik = sec.name_to_cik('NVIDIA CORP')[0]
year = 2024
quarter = 4
print(sec.quarterly_filing(nvidia_cik, year, quarter))
#cik_tests(sec)
#filing_tests(sec)




