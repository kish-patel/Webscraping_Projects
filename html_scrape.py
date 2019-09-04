# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:46:19 2019

@author: patel
"""

import requests
from bs4 import BeautifulSoup as bsoup
   
my_wm_username = 'kpatel03'

# Create user agent, initialize url, and get url repsone content
useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
search_url = 'http://publicinterestlegal.org/county-list/'
response = requests.get(search_url, headers={"User-Agent": useragent}).content

            
# Parse html
parsed_html = bsoup(response, 'lxml')

# Create a variable to store table rows
target_rows = parsed_html.find_all('tr')

# Create a for loop to get all table data as sublists, and append each sublist to empty list
my_result_list = []
for r in target_rows:
    rows = []
    for j in r.find_all('td'):
        rows.append(j.text)
    my_result_list.append(rows)
print(my_wm_username)
print(len(my_result_list))
print(my_result_list)
