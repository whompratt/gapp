# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 14:11:56 2019

@author: Dave

Currently Disabled to hide textPassword in logonData
"""
import requests
from lxml import html
from pandas import DataFrame
import pandas as pd

# Create our logon payload. 'hiddenToken' may change at a later date.
logonData = {'textLogin':'######@######', 'textPassword':'#########', 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}

# Logon to GPRO using the logon information provided and store that under our session
session = requests.session()
loginURL = "https://gpro.net/gb/Login.asp"
logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

# Gather the home page information and collect driver ID, track ID, team name, and manager ID
tree = html.fromstring(logonResult.content)

#Define Data Frames
Data_Race = pd.DataFrame(index=['input'], 
                         columns = ('Race-ID', 'Season-No', 'Race-No', 'Division-ID', 'Track Name', 
                         'Q1 Lap Time', 'Q1 Risk', 'Q1 Driver Energy Drop', 'Q1 FWing', 'Q1 RWing', 'Q1 Eng', 'Q1 Bra', 'Q1 Gear', 'Q1 Susp', 'Q1 Tyres',
                         'Q2 Lap Time', 'Q2 Risk', 'Q2 Driver Energy Drop', 'Q2 FWing', 'Q2 RWing', 'Q2 Eng', 'Q2 Bra', 'Q2 Gear', 'Q2 Susp', 'Q2 Tyres',
                         'Race FWing', 'Race RWing', 'Race Eng', 'Race Bra', 'Race Gear', 'Race Susp', 'Race Tyres',
                         'Starting Risk', 'OT Risk', 'DF Risk', 'CT Dry Risk', 'CT Wet Risk', 'Mal Risk',
                         'Driver Name',
                         'OA', 'Con', 'Tal', 'Agr', 'Exp', 'TeI', 'Sta', 'Cha', 'Mot', 'Rep', 'Wei',
                         'OA Delta', 'Con Delta', 'Tal Delta', 'Agr Delta', 'Exp Delta', 'TeI Delta', 'Sta Delta', 'Cha Delta', 'Mot Delta', 'Rep Delta', 'Wei Delta',
                         'DE Before', 'DE After',
                         'Start Position', 'Finish Position', 'Power', 'Handling', 'Acceleration',
                         'Tyre Supplier',
                         'Q1 Weather', 'Q1 Temp', 'Q1 Humidity',
                         'Q2 Weather', 'Q2 Temp', 'Q2 Humidity',
                         'Weather Forecast',
                         'Finish Earnings', 'Qualy Earnings', 'Sponsor Earnings', 'Salary Cost', 'Staff Cost', 'Facility Cost', 'Tyres Cost', 'Current Balance',
                         'Cha Lvl', 'Eng Lvl', 'FWing Lvl', 'RWing Lvl', 'Underb Lvl', 'Sidep Lvl', 'Cool Lvl', 'Gear Lvl', 'Bra Lvl', 'Susp Lvl', 'Elec Lvl',
                         'Cha Before', 'Eng Before', 'FWing Before', 'RWing Before', 'Underb Before', 'Sidep Before', 'Cool Before', 'Gear Before', 'Bra Before', 'Susp Before', 'Elec Before',
                         'Cha After', 'Eng After', 'FWing After', 'RWing After', 'Underb After', 'Sidep After', 'Cool After', 'Gear After', 'Bra After', 'Susp After', 'Elec After',
                         ))
Data_Stint = pd.DataFrame(columns = ('Race-ID', 'Stint ID', 'Tyres', 'Pit on Lap', 'Length of Stint', 'Reason for Pit', 'Tyre Bad Lap', 'Tyre Final', 'Fuel at start (L)', 'Fuel at End (L)',
                                     'Min Temp', 'Max Temp', 'Avg Temp', 'Min Humidity', 'Max Humidity', 'Avg Humidity', 'Fuel Consumption', 'Tyre Bad Km', 'Tyre Total Km'
                          ))
Data_Laps = pd.DataFrame(columns = ('Race-ID', 'Lap #', 'Lap Time', 'Pos', 'Tyres', 'Weather', 'Temp', 'Hum', 'Events', 'Tyre Condition'
                            ))


#%%
# Track ID of next race
trackID = tree.xpath("//a[starts-with(@href, 'TrackDetails.asp')]/@href")
trackURL = "https://gpro.net/gb/" + trackID[0]

# URLs for car and race details, for later use
carURL = "https://www.gpro.net/gb/UpdateCar.asp"
raceURL = "https://www.gpro.net/gb/RaceSetup.asp"
#%%


#%%


#%%
analysisURL = "https://gpro.net/gb/RaceAnalysis.asp"

RaceAnalysis = session.get(analysisURL, headers=dict(referer=analysisURL))
tree = html.fromstring(RaceAnalysis.content)
tree_left = tree.xpath('//div[@class="column left fortyfive nomargin"]')[0]
tree_right = tree.xpath('//div[@class="column right fiftyfive"]')[0]


#%%
#Scrape for Qualification Lap Times
#Done
Data_Race['Q1 Lap Time'] = str(tree_left.xpath("normalize-space(//th[contains(text(), 'Lap times')]/../../tr[3]/td[1]/text())"))
Data_Race['Q2 Lap Time'] = str(tree_left.xpath("normalize-space(//th[contains(text(), 'Lap times')]/../../tr[3]/td[2]/text())"))

#Scrape for Setups

Data_Race['Q1 FWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[2]/text())"))
Data_Race['Q1 RWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[3]/text())"))
Data_Race['Q1 Eng'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[4]/text())"))
Data_Race['Q1 Bra'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[5]/text())"))
Data_Race['Q1 Gear'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[6]/text())"))
Data_Race['Q1 Susp'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[7]/text())"))
Data_Race['Q1 Tyres'] = str(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[3]/td[8]/text())")) 

Data_Race['Q2 FWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[2]/text())"))
Data_Race['Q2 RWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[3]/text())"))
Data_Race['Q2 Eng'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[4]/text())"))
Data_Race['Q2 Bra'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[5]/text())"))
Data_Race['Q2 Gear'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[6]/text())"))
Data_Race['Q2 Susp'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[7]/text())"))
Data_Race['Q2 Tyres'] = str(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[4]/td[8]/text())"))

Data_Race['Race FWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[2]/text())"))
Data_Race['Race RWing'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[3]/text())"))
Data_Race['Race Eng'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[4]/text())"))
Data_Race['Race Bra'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[5]/text())"))
#There is a problem with this line
#Data_Race['Race Gear'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]]/td[6]/text())"))
Data_Race['Race Susp'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[7]/text())"))
Data_Race['Race Tyres'] = str(tree.xpath("normalize-space(//th[contains(text(), 'Setups used')]/../../tr[5]/td[8]/text())"))


#%%
#Scrape for Risks Used
#Done

Data_Race['Starting Risk'] = str(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[5]/td[1]/text())"))
Data_Race['OT Risk'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[7]/td[1]/text())"))
Data_Race['DF Risk'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[7]/td[2]/text())"))
Data_Race['CT Dry Risk'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[7]/td[3]/text())"))
Data_Race['CT Wet Risk'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[7]/td[4]/text())"))
Data_Race['Mal Risk'] = int(tree.xpath("normalize-space(//th[contains(text(), 'Risks used')]/../../tr[7]/td[5]/text())"))
#%%
#Scrape for Driver Attributes
DriverName = str(tree.xpath("normalize-space(//th[contains(text(), 'Driver attributes')]/../../tr[3]/td[1]/a/text())"))

#create lists that contain driver skills and driver delta skills
#final [] parentheses are omitting first few entries which are nonsense
driverskills = tree_left.xpath(".//th[contains(text(), 'Driver attributes')]/../../tr[3]/td/text()")[2:]
#driver delta is list of strings containing the brackets
driverdelta = tree_left.xpath(".//th[contains(text(), 'Driver attributes')]/../../tr[4]/td/text()")
'''
Need to clean up Delta from string to values (or do I?)
'''

#zip the two lists together
Driver_Skills = pd.concat([pd.DataFrame([loop],) for loop in zip(driverskills, driverdelta)], ignore_index=False)
#Transpose the dataframe
Driver_Skills = pd.DataFrame(Driver_Skills.T)
#Name the columns
Driver_Skills.columns =('OA', ' Con',  'Tal', 'Agr', 'Exp', 'TeI', 'Sta', 'Cha', 'Mot', 'Rep', 'Wei')


driverskills = pd.DataFrame(tree_left.xpath(".//th[contains(text(), 'Driver attributes')]/../../tr[3]/td/text()")[2:])
driverdelta = pd.DataFrame(tree_left.xpath(".//th[contains(text(), 'Driver attributes')]/../../tr[4]/td/text()"))
#%%
#Driver Energy
driverenergy = tree_left.xpath(".//td[@title='Before the race']/div[@class='barLabel ']/text()")

#%%
Data_Race['OA']
