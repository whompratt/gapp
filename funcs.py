from lxml import html
from lxml import etree

import requests

# checkData
# This function will check to see if the user has selected "save credentials"
# If they have, it will store the credentials given in the data.dat file, otherwise it will erase that file
def checkData(filename, rememberCredentials, username, password):
	if(rememberCredentials == 1):
		try:
			file = open(filename, "w")
			file.write("1\n")
			file.write(username + "\n")
			file.write(password + "\n")
			file.close()
		except Exception:
			pass
	else:
		try:
			open(filename, "w").close()
		except:
			pass

# checkLogin
# Takes login details and confirms they are correct, warning the user if something is amiss
def checkLogin(username, password):
	# Create our logon payload. 'hiddenToken' may change at a later date.
	logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
	
	# Logon to GPRO using the logon information provided and store that under our session
	session = requests.session()
	loginURL = "https://gpro.net/gb/Login.asp"
	logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

	# Gather the home page information and collect driver ID, track ID, team name, and manager ID
	tree = html.fromstring(logonResult.content)

	# Get the managerID, which will be empty if the logon details are wrong
	managerID = tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")

	# If managerID exists, return True, else return False
	return True if managerID else False

def checkTeam(username, password):
	# Create our logon payload. 'hiddenToken' may change at a later date.
	logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
	
	# Logon to GPRO using the logon information provided and store that under our session
	session = requests.session()
	loginURL = "https://gpro.net/gb/Login.asp"
	logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

	# Gather the home page information and collect driver ID, track ID, team name, and manager ID
	tree = html.fromstring(logonResult.content)

	# Get the teamName
	teamName = tree.xpath("//a[starts-with(@href, 'TeamProfile.asp')]/text()")

	# If the user is in the correct team, return True, else False
	return True if (teamName[0] == "VIPER AUTOSPORT") or (teamName[0] == "TEAM VIPER") or (teamName[0] == "VIPER RACING") else False