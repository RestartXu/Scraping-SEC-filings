import urllib.request
import os
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Define functions to download filings
def get_list(ticker):
    base_url_part1 = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="
    base_url_part2 = "&type=10-K&dateb=&owner=&start=0&count=100&output=xml"
    href = []

    base_url = base_url_part1 + ticker + base_url_part2

    sec_page = urllib.request.urlopen(base_url)
    sec_soup = BeautifulSoup(sec_page, "html.parser")

    filings = sec_soup.findAll('filing')

    for filing in filings:
        report_year = int(filing.datefiled.get_text()[0:4])
        if report_year >= 2018:
            filing_href = filing.filinghref.get_text()
            filing_url = "https://www.sec.gov" + filing_href
            href.append(filing_url)

    return href


def download_report(url_list, dir_path):
    for report_url in url_list:
        report_page = urllib.request.urlopen(report_url)
        report_soup = BeautifulSoup(report_page, "html.parser")

        xbrl_file = report_soup.findAll('tr')

        for item in xbrl_file:
            try:
                file_type = item.find('td', text='10-K').find_next('td').text
                if file_type == '10-K':
                    file_url = item.find('a', {'id': 'documentsbutton'})['href']
                    file_name = file_url.split("/")[-1]

                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)

                    target_url = "https://www.sec.gov" + file_url
                    print("Downloading:", target_url)

                    urllib.request.urlretrieve(target_url, os.path.join(dir_path, file_name))
                    print("Downloaded:", file_name)

            except:
                pass


# Step 2: Define function to download filings for each ticker
def download_filings_for_tickers(tickers):
    for ticker in tickers:
        url_list = get_list(ticker)
        base_path = "./Downloaded_Filings"
        dir_path = os.path.join(base_path, ticker)
        download_report(url_list, dir_path)


# Step 3: Import tickers from CSV file and download filings
ticker_file = pd.read_csv("companylist.csv")
tickers = ticker_file['Symbol'].tolist()

download_filings_for_tickers(tickers)
