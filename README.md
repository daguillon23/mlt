# MLT GenAI Project
A generative AI project based on the SEC's [EDGAR conformed list](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) of publically-traded companies.

### [cik.py](cik_module/cik.py)
- Requests company data from an SEC [data file](https://www.sec.gov/files/company_tickers_exchange.json).
- Upon successful request, creates two dicts that both contain every company's CIK, name, ticker, and exchange association.  
  - `name_dict` accepts company names as keys (retrieved via `name_to_cik()`).  
  - `tick_dict` accepts company tickers as keys (retrieved via `tick_to_cik()`).


