# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 18:46:22 2019

@author: Dave

Worked from example:
    https://medium.com/analytics-vidhya/web-scraping-wiki-tables-using-beautifulsoup-and-python-6b9ea26d8722
    
    Currently Disabled to hide textPassword in logonData
"""
import requests

# Create our logon payload. 'hiddenToken' may change at a later date.
#logonData = {'textLogin':'##########@#######', 'textPassword':'###########', 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}

# Logon to GPRO using the logon information provided and store that under our session
session = requests.session()
loginURL = "https://gpro.net/gb/Login.asp"
logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

analysisURL = "https://gpro.net/gb/RaceAnalysis.asp"
RaceAnalysis = session.get(analysisURL, headers=dict(referer=analysisURL))

from bs4 import BeautifulSoup
soup = BeautifulSoup(RaceAnalysis.content,'lxml')

#Iterate over left table for each sub-table
Left_Table = soup.find('div',{'class':'column left fortyfive nomargin'})
Qualify_Times = Left_Table.find('table',{'class':'styled bordered center'})
Setups_Used = Qualify_Times.find_next('table',{'class':'styled bordered center'})
Risks_Used = Setups_Used.find_next('table',{'class':'styled bordered center'})
Driver_Attributes = Risks_Used.find_next('table',{'class':'styled bordered center'})
#Driver Energy table does not use the same format
#Driver_Energy = Driver_Attributes.find_next('table',{'class':'styled bordered center'})
Positions = Driver_Attributes.find_next('table',{'class':'styled bordered center'})
Overall_CCP = Positions.find_next('table',{'class':'styled bordered center'})
Weather = Overall_CCP.find_next('table',{'class':'styled bordered center'})
Stint = soup.find('table',{'class':'styled bordered leftalign'})
Financials = soup.find('table',{'id':'Table1'})

Right_Table = soup.find('div',{'class':'column right fiftyfive'})
Car_Parts = Right_Table.find('table',{'class':'styled bordered center'})
Lap_Times = Right_Table.find('table',{'class':'styled borderbottom'})
#Don't yet have Tyre Supplier
#Don't yet have start fuel
#Don't yet have Pit Parameters
#Don't yet have finish conditions

Find = Lap_Times.findAll('tr')

Stints = []
for tr in Find:
    tds = tr.find_all('td')

