# MLT GenAI Project
A generative AI project led by MLT Coach Gerard Spivey. Based on public company data within the SEC's [EDGAR system](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data).

### [cik.py](cik_module/cik.py)
- Requests company data from an EDGAR [data file](https://www.sec.gov/files/company_tickers_exchange.json).
- Upon successful request, creates two dicts that both contain every company's CIK, name, ticker, and exchange association.  
  - `name_dict` accepts company names as keys (retrieved via `name_to_cik()`).  
  - `tick_dict` accepts company tickers as keys (retrieved via `tick_to_cik()`).
- Searches for a company's 10-K and 10-Q forms with `annual_filing` and `quarterly_filing`
  


