import datetime
import os
import re

import requests
from bs4 import BeautifulSoup as soup

release = False

# urllib3.disable_warnings()
baseurl = 'https://www.google.co.kr/finance/quote/'
if os.path.exists('etc/backup/stock_list.txt'):
    f = open('etc/backup/stock_list.txt', 'r')
    data = f.readlines()
    f.close()
    tickers = []
    for tic in data:
        tickers.append(tic.replace('\n', ''))
else:

    tickers = ['TSLA:NASDAQ',
               'AMD:NASDAQ',
               'NVDA:NASDAQ',
               'KO:NYSE',
               'LMT:NYSE',
               'MSFT:NASDAQ',
               'SBUX:NASDAQ',
               '005930:KRX',
               '005935:KRX',
               'VZ:NYSE',
               ]
    f = open('stock_list.txt', 'a')
    for tic in tickers:
        f.write(tic + '\n')
    f.close()

# -------------------------------------------------------------------------------------------------
# --------------------------------- MAIN FUNCTION -------------------------------------------------
# -------------------------------------------------------------------------------------------------

spliter = '---------------------------------------------------------------------------------------------------------'
spliter_pivot = 5
updown_tag = '#yDmH0d > c-wiz:nth-child'
nametag = 'zzDege'
indexvaluetag = 'YMlKec fxKbKc'  # div
yesterday_tag = 'P6K39c'  # div

# -------------------------------------------------------------------------------------------------
# DATE
# -------------------------------------------------------------------------------------------------
data = []
data_str = []
now = datetime.datetime.now()
now_str = f"\t{now.year:4d}-{now.month:2d}-{now.day:2d} {now.hour:2d}:{now.minute:2d}:{now.second:2d}"

print(spliter)
print(now_str)
print(spliter)
cnt = 0

result = []

# -------------------------------------------------------------------------------------------------
# -PARSER------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
ticker: str
for ticker in tickers:
    requests_target: str = '{0}{1}?hl=ko'.format(baseurl, ticker)
    pagehtml = requests.get(requests_target)
    pagehtmlbs = soup(pagehtml.text, 'html.parser')
    title = pagehtmlbs.find('div', class_=nametag).text
    stock_value = pagehtmlbs.find('div', class_=indexvaluetag).text
    yesterday_value = pagehtmlbs.find('div', class_=yesterday_tag).text
    cal_stock = float(stock_value[1:].replace(',', ''))
    cal_yes_stock = float(yesterday_value[1:].replace(',', ''))
    rate = ((cal_stock - cal_yes_stock) / cal_yes_stock) * 100

    # -------------------------------------------------------------------------------------------------
    # -PRINT COLOR SETTING-----------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------

    color = ''
    reset = ''
    if not release:
        reset = '\033[0m'
    if rate > 0:
        arrow = '▲'
    else:
        arrow = '▼'

    pivot = 5
    if not release:
        reset = '\033[0m'
        if rate > 0:
            if rate > pivot:
                color = '\033[91m'
            else:
                color = '\033[31m'  #
        else:
            if rate < (-1) * pivot:
                color = '\033[95m'  #
            else:
                color = '\033[34m'  #

    # -------------------------------------------------------------------------------------------------
    # -NAMING SPACE CAL.-------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------

    space_count = 0
    reg = re.compile(r'[a-zA-Z1-9]')
    if reg.match(title): # ALPHABET COUNT
        for lit in title:
            if ' ' == lit:
                space_count += 1

        just_size = int(40)
    else:
        for lit in title: # SPACE COUNT
            if ' ' == lit:
                space_count += 1

        just_size = int(40 - (len(title)) + space_count)


    # STR FORMATING
    str_form = '{}'.format(title).rjust(just_size) + '|'
    str_form = str_form + '\t{:15s}'.format(stock_value)
    str_form = str_form + color
    str_form = str_form + arrow + ' {:7.2f}%'.format(rate)
    str_form = str_form + reset + '\t'
    str_form = str_form + '(전일 종가 {:12s})'.format(yesterday_value)
    print(str_form)
    result.append(str_form)

    cnt += 1
    if cnt == spliter_pivot:
        cnt = 0
        print(spliter)


if cnt != 0:
    print(spliter)
