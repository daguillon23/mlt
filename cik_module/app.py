import requests
import json

class Edgar:

    def __init__(self, url):

        # sets url, establishes headers, and requests json file from url
        self.url = url
        headers = {'user-agent': 'MLT DA diego.eaguillon@gmail.com'}
        req = requests.get(self.url, headers=headers)
        self.json = req.json()

        # print(type(self.json))

        # dicts is a list of two dicts
        # index 0: name is key, info is value
        # index 1: ticker is key, info is value
        dicts = self._get_dicts()
        self.name_dict = dicts[0]
        self.tick_dict = dicts[1]

    def _get_dicts(self):
        name_dict = {}
        tick_dict = {}
       # with open('info.text', 'w') as file:
        #    json.dump(self.json, file, indent=4)
        for company in self.json['data']:
            #print(company)
            cik = company[0]
            name = company[1]
            ticker = company[2]
            exchange = company[3]
            #print(name)
            name_dict[name] = [cik, name, ticker, exchange]
            tick_dict[ticker] = [cik, name, ticker, exchange]

            #print(name_dict)
          #  for item in company:
           #     print(item)

        return [name_dict, tick_dict]
    
    def name_to_cik(self, name):
        return self.name_dict[name]
    
    def tick_to_cik(self, ticker):
        return self.tick_dict[ticker]


sec = Edgar('https://www.sec.gov/files/company_tickers_exchange.json')