# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 08:50:22 2019

@author: patel

Gathering NFL Roster Data from pro-football-reference.com


"""
import pandas as pd
import requests
from time import sleep
from bs4 import BeautifulSoup


# Define a function to read html data and read into frames 
def html2dataframe(HTML, table_id = ''):
    stat_html = HTML.text
    stat_html = stat_html.replace('<!--', "")
    stat_html = stat_html.replace('-->', "")
    table_html = pd.read_html(stat_html, attrs={'id': table_id})[0]
    htmldataframe = pd.DataFrame(table_html)
    return htmldataframe
# Define a function to get a list of player codes
def getplayercodes(HTML, table_id = ''):
    links = []
    html_txt = HTML.text
    html_txt = html_txt.replace('<!--', "")
    html_txt = html_txt.replace('-->', "")
    soup = BeautifulSoup(html_txt, 'lxml')
    table = soup.find('table', attrs={'id': table_id})
    for row in table.find_all('tr'):
        for cells in row.find_all('td', attrs = {'data-stat':'player'}):
            for link in cells.find_all('a'):
                links.append(link.get('href')) # gets the links
    playercodes = [links[i][-12:-4] for i in range(len(links))]
    return playercodes
# Define a function to clean all roster data
def cleanrosters(dataframe):
    # Drop all Team Totals name rows
    dataframe = dataframe[dataframe['Player'] != 'Team Total']
    # Split name column into first and last name
    dataframe[['FirstName', 'LastName']] = dataframe['Player'].str.rsplit(" ", n = 1, expand = True) 
    # Dropping old Name columns 
    dataframe.drop(columns = ['Player'], inplace = True)
    # Recording Pro-Bowl and All-Pro appearances and cleaning Last Name column
    dataframe['ProBowl'] = dataframe['LastName'].str.extract(r'(\*)')
    dataframe['AllPro'] = dataframe['LastName'].str.extract(r'(\+)')
    dataframe['ProBowl'] = dataframe['ProBowl'].str.replace(r'\*', '1')
    dataframe['AllPro'] = dataframe['AllPro'].str.replace(r'\+', '1')
    dataframe['LastName'] = dataframe['LastName'].str.replace(r'\W+', '')
    # Extract player's draft information and clean up appropriate columns
    dataframe[['draftteam', 'draftrnd', 'draftpick', 'draftyr']] = dataframe['Drafted (tm/rnd/yr)'].str.rsplit("/", expand = True) 
    dataframe.drop(columns = ['Drafted (tm/rnd/yr)'], inplace = True)
    dataframe['draftrnd'] = dataframe['draftrnd'].str.replace(r'\D+', '')
    dataframe['draftpick'] = dataframe['draftpick'].str.replace(r'\D+', '')
    dataframe['draftyr'] = dataframe['draftyr'].str.replace(r'\D+', '')
    # Clean up Yrs column
    dataframe['Yrs'] = dataframe['Yrs'].astype(str).str.replace(r'Rook', '0')
    # Clean Height column to be one single height in inches
    dataframe[['Htft', 'Htin']] = dataframe['Ht'].str.rsplit("-", expand = True).astype('float')
    dataframe['Ht'] = dataframe['Htft']*12 + dataframe['Htin']
    dataframe.drop(columns = dataframe[['Htft', 'Htin']] , inplace = True)
    return dataframe
# Define a function to clean all starter data
def cleanstarters(dataframe):
    # Drop all Team Totals name rows
    dataframe = dataframe[dataframe['Player'] != 'Offensive Starters']
    dataframe = dataframe[dataframe['Player'] != 'Defensive Starters']
    dataframe = dataframe[dataframe['Player'] != 'Special Teams Starters']
        # Split name column into first and last name
    dataframe[['FirstName', 'LastName']] = dataframe['Player'].str.rsplit(" ", n = 1, expand = True) 
    # Dropping old Name columns 
    dataframe.drop(columns = ['Player'], inplace = True)
    # Recording Pro-Bowl and All-Pro appearances and cleaning Last Name column
    dataframe['ProBowl'] = dataframe['LastName'].str.extract(r'(\*)')
    dataframe['AllPro'] = dataframe['LastName'].str.extract(r'(\+)')
    dataframe['ProBowl'] = dataframe['ProBowl'].str.replace(r'\*', '1')
    dataframe['AllPro'] = dataframe['AllPro'].str.replace(r'\+', '1')
    dataframe['LastName'] = dataframe['LastName'].str.replace(r'\W+', '')
    # Extract player's draft information and clean up appropriate columns
    dataframe[['draftteam', 'draftrnd', 'draftpick', 'draftyr']] = dataframe['Drafted (tm/rnd/yr)'].str.rsplit("/", expand = True) 
    dataframe.drop(columns = ['Drafted (tm/rnd/yr)'], inplace = True)
    dataframe['draftrnd'] = dataframe['draftrnd'].str.replace(r'\D+', '')
    dataframe['draftpick'] = dataframe['draftpick'].str.replace(r'\D+', '')
    dataframe['draftyr'] = dataframe['draftyr'].str.replace(r'\D+', '')
    # Clean up Yrs column
    dataframe['Yrs'] = dataframe['Yrs'].astype(str).str.replace(r'Rook', '0')
    dataframe.drop(columns = ['Summary of Player Stats'], inplace = True)
    return dataframe
# Read in the nfl team codes csv and create a list of the codes and a dictionary of code and names
nflteamcodesdf = pd.read_csv('nflteamlist.csv')
teamcodeslist = nflteamcodesdf['Code'].values.tolist()
namecodedict = dict(zip(nflteamcodesdf['Code'], nflteamcodesdf['Name']))
# Initialize empty URL list
urls = []
# Create URL strings to be parsed
for i in teamcodeslist:
    loopedurls = 'https://www.pro-football-reference.com/teams/' + str(i) + '/2018_roster.htm'
    urls.append(loopedurls)
##### Initialize empty data frames that the respective statistics will be inserted into #####
starters = pd.DataFrame()
rosterandsalary = pd.DataFrame()
# Loop to parse the html data from each url
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
for url in urls:
    print('Gathering Data for... ' + url)
    html = requests.get(url, headers = header)
    starters_HTML = html2dataframe(html, table_id = 'starters')
    rosterandsalary_HTML = html2dataframe(html, table_id = 'games_played_team')
    # Add a Team Code column with the appropriate team codes to the looped data frames
    starters_HTML['TeamCode'] = url[-19:-16]
    rosterandsalary_HTML['TeamCode'] = url[-19:-16]
    # Use the defined functions to clean the tables
    starters_HTML = cleanstarters(starters_HTML)
    rosterandsalary_HTML = cleanrosters(rosterandsalary_HTML)
    # Get list of player IDs and add them to the tables
    startersplayerids = getplayercodes(html, table_id = 'starters')
    rosterplayerids = getplayercodes(html, table_id = 'games_played_team')
    starters_HTML['PlayerCode'] = startersplayerids
    rosterandsalary_HTML['PlayerCode'] = rosterplayerids
    # Concat loop data frames into respective master data frames
    starters = pd.concat([starters, starters_HTML])
    rosterandsalary = pd.concat([rosterandsalary, rosterandsalary_HTML])
    sleep(5)
# Map team names to each of the data frames  
starters['TeamName'] = starters['TeamCode'].map(namecodedict)
rosterandsalary['TeamName'] = rosterandsalary['TeamCode'].map(namecodedict)
# Export to dataframes to CSV
starters.to_csv('starters2018.csv' , header = True)
rosterandsalary.to_csv('rosterandsalary2018.csv' , header = True)