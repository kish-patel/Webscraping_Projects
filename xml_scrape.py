# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 09:48:54 2019

@author: patel
"""

import requests
from lxml import objectify

# Create variables for the url structure
parameter = 'tavg'
state = '44'
month = '08'
year = '2016'

# Use string substitution to generate the url
urlTemplate = "https://www.ncdc.noaa.gov/cag/statewide/rankings/%s-%s-%s%s/data.xml"
urlParameters = (urlTemplate % (state, parameter, year, month))

# Request the url and get the xml conent
response = requests.get(urlParameters).content
root = objectify.fromstring(response)

# Print out desired fields from the 5th period
my_wm_username = 'kpatel03'
for i in range(len(root)):
    for j in range(len(root['data'][i])):
        if root['data'][j]['period'] == 5:
            print(my_wm_username)
            print(root['data'][j]['value'])
            print(root['data'][j]['mean'])
            print(root['data'][j]['departure'])
            print(root['data'][j]['lowRank'])
            print(root['data'][j]['highRank'])