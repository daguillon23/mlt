import requests
import copy

class Edgar:

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
    
    def name_to_cik(self, name):
        try:
            return copy.deepcopy(self._name_dict[name])
        except:
            return 'Name not found.'
    
    def tick_to_cik(self, ticker):
        try:
            return copy.deepcopy(self._tick_dict[ticker])
        except:
            return 'Ticker not found.'


def cik_tests(sec):
    print(sec.name_to_cik('Apple Inc.'))
    print(sec.tick_to_cik('GOOGL'))
    print(sec.name_to_cik('doesnt exist'))
    print(sec.tick_to_cik('doesnt exist'))


sec = Edgar('https://www.sec.gov/files/company_tickers_exchange.json')
cik_tests(sec)
