# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:41:14 2019

@author: patel


Gather all NFL team and individual statistics from pro-football-reference.com

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
def cleanpassing(dataframe):
    # Drop all Team and Opp Totals name rows
    dataframe = dataframe[dataframe['Player'] != 'Team Total']
    dataframe = dataframe[dataframe['Player'] != 'Opp Total']
    # Split name column into first and last name
    dataframe[['FirstName', 'LastName']] = dataframe['Player'].str.rsplit(" ", n = 1, expand = True)
    # Dropping old Name columns 
    dataframe.drop(columns = ['Player'], inplace = True)
    dataframe['LastName'] = dataframe['LastName'].str.replace(r'\W+', '')
    return dataframe
def cleanindv(dataframe):
    # Drop all Team and Opp Totals name rows
    dataframe = dataframe[dataframe[('Unnamed: 1_level_0','Player')] != 'Team Total']
    dataframe = dataframe[dataframe[('Unnamed: 1_level_0','Player')] != 'Opp Total']
    # Split name column into first and last name
    dataframe[['FirstName', 'LastName']] = dataframe[('Unnamed: 1_level_0','Player')].str.rsplit(" ", n = 1, expand = True)
    # Dropping old Name columns 
    dataframe.drop(columns = [('Unnamed: 1_level_0','Player')], inplace = True)
    dataframe['LastName'] = dataframe['LastName'].str.replace(r'\W+', '')
    return dataframe
    
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
# Define a function to clea
# Read in the nfl team codes csv and create a list of the codes and a dictionary of code and names
nflteamcodesdf = pd.read_csv('nflteamlist.csv')
teamcodeslist = nflteamcodesdf['Code'].values.tolist()
namecodedict = dict(zip(nflteamcodesdf['Code'], nflteamcodesdf['Name']))
# Initialize empty URL list
urls = []
allteaminfo = []
# Create URL strings to be parsed
for i in teamcodeslist:
    loopedurls = 'https://www.pro-football-reference.com/teams/' + str(i) + '/2018.htm'
    urls.append(loopedurls)
##### Initialize empty data frames that the respective statistics will be inserted into #####
# Team Stats
TeamStatsandRankings = pd.DataFrame()
ScheduleandGameResults = pd.DataFrame()
TeamConversions = pd.DataFrame()
ScoringSummary = pd.DataFrame()
TouchdownLog = pd.DataFrame()
# Individual Player Stats
IndvPassing = pd.DataFrame()
IndvRushingandReceiving = pd.DataFrame()
IndvKickandPuntReturns = pd.DataFrame()
IndvKickingandPunting = pd.DataFrame()
IndvDefenseandFumbles = pd.DataFrame()
# Loop to parse the html data from each url
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
for url in urls:
    print('Gathering Data for... ' + url)
    html = requests.get(url, headers = header)
    teamstatsandrankings_HTML = html2dataframe(html, table_id = 'team_stats')
    scheduleandgameresults_HTML = html2dataframe(html, table_id = 'games')
    teamconversion_HTML = html2dataframe(html, table_id = 'team_conversions')
    scoringsummary_HTML = html2dataframe(html, table_id = "scoring")
    touchdownlog_HTML = html2dataframe(html, table_id = 'team_td_log')
    # Individual Player Stats
    indvpassing_HTML = html2dataframe(html, table_id = 'passing')
    indvrushingandreceiving_HTML = html2dataframe(html, table_id = 'rushing_and_receiving')
    indvkickandpuntreturns_HTML = html2dataframe(html, table_id = 'returns')
    indvkickingandpunting_HTML = html2dataframe(html, table_id = 'kicking')
    indvdefenseandfumbles_HTML = html2dataframe(html, table_id = 'defense')
    # Add a Team Code column with the appropriate team codes to the looped data frames
    teamstatsandrankings_HTML['TeamCode'] = url[-12:-9]
    scheduleandgameresults_HTML['TeamCode'] = url[-12:-9]
    teamconversion_HTML['TeamCode'] = url[-12:-9]
    scoringsummary_HTML['TeamCode'] = url[-12:-9]
    touchdownlog_HTML['TeamCode'] = url[-12:-9]
    indvpassing_HTML['TeamCode'] = url[-12:-9]
    indvrushingandreceiving_HTML['TeamCode'] = url[-12:-9]
    indvkickandpuntreturns_HTML['TeamCode'] = url[-12:-9]
    indvkickingandpunting_HTML['TeamCode'] = url[-12:-9]
    indvdefenseandfumbles_HTML['TeamCode'] = url[-12:-9]
    #Clean the indiviual player statistic tables using the defined function
    indvpassing_HTML = cleanpassing(indvpassing_HTML)
    indvrushingandreceiving_HTML = cleanindv(indvrushingandreceiving_HTML)
    indvkickandpuntreturns_HTML = cleanindv(indvkickandpuntreturns_HTML)
    indvkickingandpunting_HTML = cleanindv(indvkickingandpunting_HTML)
    indvdefenseandfumbles_HTML = cleanindv(indvdefenseandfumbles_HTML)
    # Use the defined function to get a list of playercodes
    PCindvpassing = getplayercodes(html, table_id = 'passing')
    PCindvrushingandreceiving = getplayercodes(html, table_id = 'rushing_and_receiving')
    PCindvkickandpuntreturns = getplayercodes(html, table_id = 'returns')
    PCindvkickingandpunting = getplayercodes(html, table_id = 'kicking')
    PCindvdefenseandfumbles= getplayercodes(html, table_id = 'defense')
    # Create a column to add them to their respective data frame
    indvpassing_HTML['PlayerCode'] = PCindvpassing
    indvrushingandreceiving_HTML['PlayerCode'] = PCindvrushingandreceiving
    indvkickandpuntreturns_HTML['PlayerCode'] = PCindvkickandpuntreturns
    indvkickingandpunting_HTML['PlayerCode'] = PCindvkickingandpunting
    indvdefenseandfumbles_HTML['PlayerCode'] = PCindvdefenseandfumbles
    # Concat loop data frames into respective master data frames
    TeamStatsandRankings = pd.concat([TeamStatsandRankings, teamstatsandrankings_HTML])
    ScheduleandGameResults = pd.concat([ScheduleandGameResults, scheduleandgameresults_HTML])
    TeamConversions = pd.concat([TeamConversions, teamconversion_HTML])
    ScoringSummary = pd.concat([ScoringSummary, scoringsummary_HTML])
    TouchdownLog = pd.concat([TouchdownLog, touchdownlog_HTML])
    IndvPassing = pd.concat([IndvPassing, indvpassing_HTML])
    IndvRushingandReceiving = pd.concat([IndvRushingandReceiving, indvrushingandreceiving_HTML])
    IndvKickandPuntReturns = pd.concat([IndvKickandPuntReturns, indvkickandpuntreturns_HTML])
    IndvKickingandPunting = pd.concat([IndvKickingandPunting, indvkickingandpunting_HTML])
    IndvDefenseandFumbles = pd.concat([IndvDefenseandFumbles, indvdefenseandfumbles_HTML])   
    sleep(5)
# Map team names to each of the data frames  
TeamStatsandRankings['TeamName'] = TeamStatsandRankings['TeamCode'].map(namecodedict)
ScheduleandGameResults['TeamName'] = ScheduleandGameResults['TeamCode'].map(namecodedict)
TeamConversions['TeamName'] = TeamConversions['TeamCode'].map(namecodedict)
ScoringSummary['TeamName'] = ScoringSummary['TeamCode'].map(namecodedict)
TouchdownLog['TeamName'] = TouchdownLog['TeamCode'].map(namecodedict)
IndvPassing['TeamName'] = IndvPassing['TeamCode'].map(namecodedict)
IndvRushingandReceiving['TeamName'] = IndvRushingandReceiving['TeamCode'].map(namecodedict)
IndvKickandPuntReturns['TeamName'] = IndvKickandPuntReturns['TeamCode'].map(namecodedict)
IndvKickingandPunting['TeamName'] = IndvKickingandPunting['TeamCode'].map(namecodedict)
IndvDefenseandFumbles['TeamName'] = IndvDefenseandFumbles['TeamCode'].map(namecodedict)
# Export to dataframes to CSV
TeamStatsandRankings.to_csv('TeamStatsandRankings2018.csv' , header = True)
ScheduleandGameResults.to_csv('ScheduleandGameResults2018.csv' , header = True)
TeamConversions.to_csv('TeamConversions2018.csv' , header = True)
ScoringSummary.to_csv('ScoringSummary2018.csv' , header = True)
TouchdownLog.to_csv('TouchdownLog2018.csv' , header = True)
IndvPassing.to_csv('IndvPassing2018.csv' , header = True)
IndvRushingandReceiving.to_csv('IndvRushingandReceiving2018.csv' , header = True)
IndvKickandPuntReturns.to_csv('IndvKickandPuntReturns2018.csv' , header = True)
IndvKickingandPunting.to_csv('IndvKickingandPunting2018.csv' , header = True)
IndvDefenseandFumbles.to_csv('IndvDefenseandFumbles2018.csv' , header = True)

