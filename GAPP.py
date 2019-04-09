from tkinter import *
from tkinter import ttk
from tkinter.ttk import Notebook
import requests
import re
import csv
import collections
import math
import os
import sys
from pathlib import Path
from lxml import html
from lxml import etree

# Import external data
from calcs import *


class Autoresized_Notebook(Notebook):
	def __init__(self, master = None, **kw):
		Notebook.__init__(self, master, **kw)
		self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

	def _on_tab_changed(self, event):
		event.widget.update_idletasks()
		tab = event.widget.nametowidget(event.widget.select())
		event.widget.configure(height = tab.winfo_reqheight(), width = tab.winfo_reqwidth())

'''
Data Storage Setup
'''
dataPath = str(Path.home()) + "\Documents\GAPP"
if not os.path.exists(dataPath):
	os.makedirs(dataPath)

filename = dataPath + "\data.dat"

try:
	file = open(filename, "x")
	file.close()
except:
	pass

try:
	file = open(filename, "r")
except:
	pass

try:
	credentialCheck = int(float(file.readline()))
except:
	credentialCheck = 0

try:
	username = file.readline()
	password = file.readline()
	file.close()
except:
	pass

# Calculate the setup and others
def calculate(*args):
	if(inputRememberCredentials.get() == 1):
		try:
			file = open(filename, "w")
			file.close()
		except:
			pass
		try:
			file = open(filename, "a")
			file.write("1\n")
			file.write(inputUsername.get() + "\n")
			file.write(inputPassword.get() + "\n")
			file.close()
		except:
			pass
	else:
		try:
			file.open(filename, "w")
			file.close()
		except:
			pass

	tab = notebook.tab(notebook.select(), "text")
	try:
		username = str(inputUsername.get())
		password = str(inputPassword.get())
		if(tab == "Setup"):
			weather = str(inputWeather.get())
			session = str(inputSession.get())
			setup = setupCalc(username, password, weather, session)		
			if(setup[0] == 0):
				warningLabel.set("Incorrect Login Details")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			elif(setup[0] == 1):
				warningLabel.set("VIPER Family Team Only")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			else:
				warningLabel.set("Updated")
				foregroundColour("Status.Label", "#00FF00")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
				frontWing.set(str(setup[0]))
				rearWing.set(str(setup[1]))
				engine.set(str(setup[2]))
				brakes.set(str(setup[3]))
				gear.set(str(setup[4]))
				suspension.set(str(setup[5]))
		elif(tab == "Strategy"):
			try:
				wear = float(re.findall('\d+.\d+', inputWear.get())[0])
			except:
				try:
					wear = float(re.findall('\d+', inputWear.get())[0])
				except:
					wear = 0.0
					inputWear.set(0)

			try:
				laps = int(re.findall('\d+', inputLaps.get())[0])
			except:
				try:
					laps = inputLaps.get()
				except:
					laps = 0
					inputLaps.set(0)

			lapsUpper.set(laps + 1)

			strategy = strategyCalc(username, password, wear, laps)

			if(strategy == 1):
				warningLabel.set("Incorrect Login Details")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			elif(strategy == 2):
				warningLabel.set("VIPER Family Team Only")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			else:
				warningLabel.set("Updated")
				foregroundColour("Status.Label", "#00FF00")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))

				for i in range(5):
					stops[i].set(strategy[0][i])
					stintlaps[i].set(strategy[1][i])
					fuels[i].set(strategy[2][i])
					pitTimes[i].set(strategy[3][i])
					TCDs[i].set(strategy[4][i])
					FLDs[i].set(strategy[5][i])
					pitTotals[i].set(strategy[6][i])
					totals[i].set(strategy[7][i])

				lapsFuelLoadLower.set(strategy[8][0])
				lapsFuelLoadUpper.set(strategy[8][1])

				for i in range(len(labelsTotal)):
					labelsTotal[i].configure(style = "Black.Label")
				labelsTotal[strategy[9]].configure(style = "Green.Label")

			GPROnextTrackName.set(strategy[10])
			GPROnextTrackLaps.set(strategy[11])
			GPROnextTrackLapDistance.set(strategy[12])
			GPROnextTrackDistance.set(strategy[13])
			GPROnextTrackPitInOut.set(strategy[14])
		elif(tab == "Car Wear"):
			# Get user and password
			username = entryUsername.get()
			password = entryPassword.get()
			# Create our logon payload. 'hiddenToken' may change at a later date.
			logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
			
			# Logon to GPRO using the logon information provided and store that under our session
			session = requests.session()
			loginURL = "https://gpro.net/gb/Login.asp"
			logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

			# Gather the home page information and collect driver ID, track ID, team name, and manager ID
			tree = html.fromstring(logonResult.content)

			driverID = tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")
			try:
				driverURL = "https://gpro.net/gb/" + driverID[0]
				warningLabel.set("Updated")
				foregroundColour("Status.Label", "#00FF00")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			except:
				warningLabel.set("Incorrect Login Details")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
				return

			trackID = tree.xpath("//a[starts-with(@href, 'TrackDetails.asp')]/@href")
			trackURL = "https://gpro.net/gb/" + trackID[0]

			teamName = tree.xpath("//a[starts-with(@href, 'TeamProfile.asp')]/text()")
			if(teamName[0] != "VIPER AUTOSPORT") and (teamName[0] != "TEAM VIPER") and (teamName[0] != "VIPER RACING"):
				warningLabel.set("VIPER Family Team Only")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))

			driverResult = session.get(driverURL, headers=dict(referer=driverURL))
			tree = html.fromstring(driverResult.content)
			driverConcentration = int(tree.xpath("normalize-space(//td[contains(@id, 'Conc')]/text())"))
			driverTalent = int(tree.xpath("normalize-space(//td[contains(@id, 'Talent')]/text())"))
			driverExperience = int(tree.xpath("normalize-space(//td[contains(@id, 'Experience')]/text())"))
			driverFactor = (0.998789138 ** driverConcentration) * (0.998751839 ** driverTalent) * (0.998707677 ** driverExperience)

			# Track ID of next race
			trackResult = session.get(trackURL, headers=dict(referer=trackURL))
			tree = html.fromstring(trackResult.content)
			trackName = str(tree.xpath("normalize-space(//h1[contains(@class, 'block')]/text())"))
			trackName = trackName.strip()

			for i in range(len(startWears)):
				try:
					int(startWears[i].get())
				except:
					startWears[i].set(0)

				try:
					int(wearlevels[i].get())
				except:
					wearlevels[i].set(1)

			try:
				int(wearClearTrackRisk.get())
			except:
				wearClearTrackRisk.set(0)

			for i in range(len(startWears)):
				raceWears[i].set(round(float(wearCalc(startWears[i].get(), int(wearlevels[i].get()), driverFactor, trackName, wearClearTrackRisk.get(), i)), 2))
				endWears[i].set(int(round(raceWears[i].get() + round(startWears[i].get(), 0), 0)))
				if(endWears[i].get() >= 90):
					endLabels[i].configure(style = "Red.Label")
				elif(endWears[i].get() >= 80):
					endLabels[i].configure(style = "Orange.Label")
				else:
					endLabels[i].configure(style = "Black.Label")
		elif(tab == "PHA"):
			partNames = ["Chassis", "Engine", "Front Wing", "Rear Wing", "Underbody", "Sidepods", "Cooling", "Gearbox", "Brakes", "Suspension", "Electronics"]

			for i in range(len(PHA) - 1):
				profile = profileCalc(partNames[i], profilePartLevels[i].get())
				for j in range(len(PHA[i])):
					PHA[i][j].set(round(profile[j], 2))
	
			PTotal = HTotal = ATotal = 0
	
			for i in range(len(PHA) - 1):
				PTotal += PHA[i][0].get()
				HTotal += PHA[i][1].get()
				ATotal += PHA[i][2].get()
	
			PParts.set(int(round(PTotal, 0)))
			HParts.set(int(round(HTotal, 0)))
			AParts.set(int(round(ATotal, 0)))

			for i in range(3):
				subTotal = 0
				subTotal += PHAParts[i].get()
				subTotal += profileTesting[i].get()
				profileTotals[i].set(int(round(subTotal, 0)))

			warningLabel.set("Updated")
			foregroundColour("Status.Label", "#00FF00")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			
	except ValueError:
		pass

def fillWear():
	try:
		username = entryUsername.get()
		password = entryPassword.get()
		# Create our logon payload. 'hiddenToken' may change at a later date.
		logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
		
		# Logon to GPRO using the logon information provided and store that under our session
		session = requests.session()
		loginURL = "https://gpro.net/gb/Login.asp"
		logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

		# Gather the home page information and collect driver ID, track ID, team name, and manager ID
		tree = html.fromstring(logonResult.content)

		driverID = tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")
		try:
			driverURL = "https://gpro.net/gb/" + driverID[0]
			warningLabel.set("Updated")
			foregroundColour("Status.Label", "#00FF00")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
		except:
			warningLabel.set("Incorrect Login Details")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return

		teamName = tree.xpath("//a[starts-with(@href, 'TeamProfile.asp')]/text()")
		if(teamName[0] != "VIPER AUTOSPORT") and (teamName[0] != "TEAM VIPER") and (teamName[0] != "VIPER RACING"):
			warningLabel.set("VIPER Family Team Only")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))

		# URL for car
		carURL = "https://www.gpro.net/gb/UpdateCar.asp"

		# Request the car information page and scrape the car character and part level and wear data
		carResult = session.get(carURL, headers=dict(referer=carURL))
		tree = html.fromstring(carResult.content)

		wearlevelChassis.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[2]/text())")))
		wearlevelEngine.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[2]/text())")))
		wearlevelFWing.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[2]/text())")))
		wearlevelRWing.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[2]/text())")))
		wearlevelUnderbody.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[2]/text())")))
		wearlevelSidepods.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[2]/text())")))
		wearlevelCooling.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[2]/text())")))
		wearlevelGearbox.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[2]/text())")))
		wearlevelBrakes.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[2]/text())")))
		wearlevelSuspension.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[2]/text())")))
		wearlevelElectronics.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[2]/text())")))

		carWearChassis = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/text())"))
		if(carWearChassis == ""):
			carWearChassis = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/font/text())"));
		wearChassis.set(int((re.findall("\d+", carWearChassis))[0]))

		carWearEngine = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/text())"))
		if(carWearEngine == ""):
			carWearEngine = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/font/text())"));
		wearEngine.set(int((re.findall("\d+", carWearEngine))[0]))

		carWearFrontWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/text())"))
		if(carWearFrontWing == ""):
			carWearFrontWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/font/text())"));
		wearFWing.set(int((re.findall("\d+", carWearFrontWing))[0]))

		carWearRearWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/text())"))
		if(carWearRearWing == ""):
			carWearRearWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/font/text())"));
		wearRWing.set(int((re.findall("\d+", carWearRearWing))[0]))

		carWearUnderbody = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/text())"))
		if(carWearUnderbody == ""):
			carWearUnderbody = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/font/text())"));
		wearUnderbody.set(int((re.findall("\d+", carWearUnderbody))[0]))

		carWearSidepod = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/text())"))
		if(carWearSidepod == ""):
			carWearSidepod = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/font/text())"));
		wearSidepods.set(int((re.findall("\d+", carWearSidepod))[0]))

		carWearCooling = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/text())"))
		if(carWearCooling == ""):
			carWearCooling = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/font/text())"));
		wearCooling.set(int((re.findall("\d+", carWearCooling))[0]))

		carWearGears = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/text())"))
		if(carWearGears == ""):
			carWearGears = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/font/text())"));
		wearGearbox.set(int((re.findall("\d+", carWearGears))[0]))

		carWearBrakes = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/text())"))
		if(carWearBrakes == ""):
			carWearBrakes = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/font/text())"));
		wearBrakes.set(int((re.findall("\d+", carWearBrakes))[0]))

		carWearSuspension = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/text())"))
		if(carWearSuspension == ""):
			carWearSuspension = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/font/text())"));
		wearSuspension.set(int((re.findall("\d+", carWearSuspension))[0]))

		carWearElectronics = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/text())"))
		if(carWearElectronics == ""):
			carWearElectronics = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/font/text())"));
		wearElectronics.set(int((re.findall("\d+", carWearElectronics))[0]))
	except ValueError:
		pass

def fillProfile():
	try:
		username = entryUsername.get()
		password = entryPassword.get()
		# Create our logon payload. 'hiddenToken' may change at a later date.
		logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
		
		# Logon to GPRO using the logon information provided and store that under our session
		session = requests.session()
		loginURL = "https://gpro.net/gb/Login.asp"
		logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

		# Gather the home page information and collect driver ID, track ID, team name, and manager ID
		tree = html.fromstring(logonResult.content)

		driverID = tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")
		try:
			driverURL = "https://gpro.net/gb/" + driverID[0]
			warningLabel.set("Updated")
			foregroundColour("Status.Label", "#00FF00")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
		except:
			warningLabel.set("Incorrect Login Details")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return

		teamName = tree.xpath("//a[starts-with(@href, 'TeamProfile.asp')]/text()")
		if(teamName[0] != "VIPER AUTOSPORT") and (teamName[0] != "TEAM VIPER") and (teamName[0] != "VIPER RACING"):
			warningLabel.set("VIPER Family Team Only")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))

		# URL for car
		carURL = "https://www.gpro.net/gb/UpdateCar.asp"

		# Request the car information page and scrape the car character and part level and wear data
		carResult = session.get(carURL, headers=dict(referer=carURL))
		tree = html.fromstring(carResult.content)

		profilelevelChassis.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[2]/text())")))
		profilelevelEngine.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[2]/text())")))
		profilelevelFWing.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[2]/text())")))
		profilelevelRWing.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[2]/text())")))
		profilelevelUnderbody.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[2]/text())")))
		profilelevelSidepods.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[2]/text())")))
		profilelevelCooling.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[2]/text())")))
		profilelevelGearbox.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[2]/text())")))
		profilelevelBrakes.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[2]/text())")))
		profilelevelSuspension.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[2]/text())")))
		profilelevelElectronics.set(int(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[2]/text())")))

		profilePowerTotal.set(int(tree.xpath("normalize-space(//td[contains(text(), 'Power')]/../../tr[3]/td[1]/text())")))
		profileHandlingTotal.set(int(tree.xpath("normalize-space(//td[contains(text(), 'Power')]/../../tr[3]/td[2]/text())")))
		profileAccelerationTotal.set(int(tree.xpath("normalize-space(//td[contains(text(), 'Power')]/../../tr[3]/td[3]/text())")))

		partNames = ["Chassis", "Engine", "Front Wing", "Rear Wing", "Underbody", "Sidepods", "Cooling", "Gearbox", "Brakes", "Suspension", "Electronics"]

		for i in range(len(PHA) - 1):
			profile = profileCalc(partNames[i], profilePartLevels[i].get())
			for j in range(len(PHA[i])):
				PHA[i][j].set(round(profile[j], 2))

		PTotal = 0
		HTotal = 0
		ATotal = 0

		for i in range(len(PHA) - 1):
			PTotal += PHA[i][0].get()
			HTotal += PHA[i][1].get()
			ATotal += PHA[i][2].get()

		PParts.set(int(round(PTotal, 0)))
		HParts.set(int(round(HTotal, 0)))
		AParts.set(int(round(ATotal, 0)))

		profileTestingPower.set(int(profilePowerTotal.get()) - int(PParts.get()))
		profileTestingHandling.set(int(profileHandlingTotal.get()) - int(HParts.get()))
		profileTestingAcceleration.set(int(profileAccelerationTotal.get()) - int(AParts.get()))
	except:
		pass


def validateFloat(P):
	if(P == ""):
		return True
	else:
		try:
			int(P)
			return True
		except:
			try:
				float(P)
				return True
			except:
				return False

def validateInt(P):
	if(P == ""):
		return True
	else:
		try:
			int(P)
			return True
		except:
			return False

def foregroundColour(styleName, colourName):
	style.configure(styleName, foreground = colourName)

# Create the root window
root = Tk()
root.title("GAPP")

vcmdInt = root.register(validateInt)
vcmdFloat = root.register(validateFloat)


# Create the tab controller
notebook = Autoresized_Notebook(root)

# Create the pages
frameSetup = ttk.Frame(notebook, name = "setup")
frameStrategy = ttk.Frame(notebook, name = "strategy")
frameWear = ttk.Frame(notebook, name = "wear")
frameProfile = ttk.Frame(notebook, name = "profile")

# Add the pages to notebook
notebook.add(frameSetup, text = "Setup")
notebook.add(frameStrategy, text = "Strategy")
notebook.add(frameWear, text = "Car Wear")
notebook.add(frameProfile, text = "PHA")

# Configure root layout
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

# Global variables
warningLabel = StringVar()

# Setup page variables
# Input
inputUsername = StringVar()
inputUsername.set(username.strip())
inputPassword = StringVar()
inputPassword.set(password.strip())
inputWeather = StringVar()
inputWeather.set("Dry")
inputSession = StringVar()
inputSession.set("Race")
inputRememberCredentials = IntVar()
inputRememberCredentials.set(credentialCheck)

# Output
frontWing = StringVar()
rearWing = StringVar()
engine = StringVar()
brakes = StringVar()
gear = StringVar()
suspension = StringVar()
frontWing.set("000")
rearWing.set("000")
engine.set("000")
brakes.set("000")
gear.set("000")
suspension.set("000")

# Strategy variables
# Input
inputWear = StringVar()
inputWear.set("20")
inputLaps = IntVar()
inputLaps.set(1)

# Output
lapsFuelLoadLower = StringVar()
lapsFuelLoadLower.set("0 L")
lapsFuelLoadUpper = StringVar()
lapsFuelLoadUpper.set("1 L")

lapsLower = IntVar()
lapsLower.set(0)
lapsUpper = IntVar()
lapsUpper.set(0)

extraStops = StringVar()
softStops = StringVar()
mediumStops = StringVar()
hardStops = StringVar()
rainStops = StringVar()

extraLaps = StringVar()
softLaps = StringVar()
mediumLaps = StringVar()
hardLaps = StringVar()
rainLaps = StringVar()

extraFuel = StringVar()
softFuel = StringVar()
mediumFuel = StringVar()
hardFuel = StringVar()
rainFuel = StringVar()

extraPitTime = StringVar()
softPitTime = StringVar()
mediumPitTime = StringVar()
hardPitTime = StringVar()
rainPitTime = StringVar()

extraTCD = StringVar()
softTCD = StringVar()
mediumTCD = StringVar()
hardTCD = StringVar()
rainTCD = StringVar()

extraFLD = StringVar()
softFLD = StringVar()
mediumFLD = StringVar()
hardFLD = StringVar()
rainFLD = StringVar()

extraPitTotal = StringVar()
softPitTotal = StringVar()
mediumPitTotal = StringVar()
hardPitTotal = StringVar()
rainPitTotal = StringVar()

extraTotal = StringVar()
softTotal = StringVar()
mediumTotal = StringVar()
hardTotal = StringVar()
rainTotal = StringVar()

stops = [extraStops, softStops, mediumStops, hardStops, rainStops]
stintlaps = [extraLaps, softLaps, mediumLaps, hardLaps, rainLaps]
fuels = [extraFuel, softFuel, mediumFuel, hardFuel, rainFuel]
pitTimes = [extraPitTime, softPitTime, mediumPitTime, hardPitTime, rainPitTime]
TCDs = [extraTCD, softTCD, mediumTCD, hardTCD, rainTCD]
FLDs = [extraFLD, softFLD, mediumFLD, hardFLD, rainFLD]
pitTotals = [extraPitTotal, softPitTotal, mediumPitTotal, hardPitTotal, rainPitTotal]
totals = [extraTotal, softTotal, mediumTotal, hardTotal, rainTotal]

grid = [stops, stintlaps, fuels, pitTimes, TCDs, FLDs, pitTotals]

for stop in stops:
	stop.set("0")
for lap in stintlaps:
	lap.set("0")
for fuel in fuels:
	fuel.set("0")
for pitTime in pitTimes:
	pitTime.set("0")
for TCD in TCDs:
	TCD.set("0")
for FLD in FLDs:
	FLD.set("0")
for pitTotal in pitTotals:
	pitTotal.set("0")
for total in totals:
	total.set("0")

extraTCD.set("0")
rainTCD.set("0")

GPROnextTrackName = StringVar()
GPROnextTrackLaps = IntVar()
GPROnextTrackLapDistance = StringVar()
GPROnextTrackDistance = StringVar()
GPROnextTrackPitInOut = DoubleVar()

GPROnextTrackName.set("-")
GPROnextTrackLaps.set("-")
GPROnextTrackLapDistance.set("-")
GPROnextTrackDistance.set("-")
GPROnextTrackPitInOut.set("-")

# Wear variables
# Input
wearClearTrackRisk = IntVar()
wearClearTrackRisk.set(0)

wearChassis = IntVar()
wearEngine = IntVar()
wearFWing = IntVar()
wearRWing = IntVar()
wearUnderbody = IntVar()
wearSidepods = IntVar()
wearCooling = IntVar()
wearGearbox = IntVar()
wearBrakes = IntVar()
wearSuspension = IntVar()
wearElectronics = IntVar()

wearChassis.set(0)
wearEngine.set(0)
wearFWing.set(0)
wearRWing.set(0)
wearUnderbody.set(0)
wearSidepods.set(0)
wearCooling.set(0)
wearGearbox.set(0)
wearBrakes.set(0)
wearSuspension.set(0)
wearElectronics.set(0)

wearlevelChassis = IntVar()
wearlevelEngine = IntVar()
wearlevelFWing = IntVar()
wearlevelRWing = IntVar()
wearlevelUnderbody = IntVar()
wearlevelSidepods = IntVar()
wearlevelCooling = IntVar()
wearlevelGearbox = IntVar()
wearlevelBrakes = IntVar()
wearlevelSuspension = IntVar()
wearlevelElectronics = IntVar()

wearlevelChassis.set(0)
wearlevelEngine.set(0)
wearlevelFWing.set(0)
wearlevelRWing.set(0)
wearlevelUnderbody.set(0)
wearlevelSidepods.set(0)
wearlevelCooling.set(0)
wearlevelGearbox.set(0)
wearlevelBrakes.set(0)
wearlevelSuspension.set(0)
wearlevelElectronics.set(0)

# Output
raceChassis = DoubleVar()
raceEngine = DoubleVar()
raceFWing = DoubleVar()
raceRWing = DoubleVar()
raceUnderbody = DoubleVar()
raceSidepods = DoubleVar()
raceCooling = DoubleVar()
raceGearbox = DoubleVar()
raceBrakes = DoubleVar()
raceSuspension = DoubleVar()
raceElectronics = DoubleVar()

raceChassis.set(0.0)
raceEngine.set(0.0)
raceFWing.set(0.0)
raceRWing.set(0.0)
raceUnderbody.set(0.0)
raceSidepods.set(0.0)
raceCooling.set(0.0)
raceGearbox.set(0.0)
raceBrakes.set(0.0)
raceSuspension.set(0.0)
raceElectronics.set(0.0)

endChassis = IntVar()
endEngine = IntVar()
endFWing = IntVar()
endRWing = IntVar()
endUnderbody = IntVar()
endSidepods = IntVar()
endCooling = IntVar()
endGearbox = IntVar()
endBrakes = IntVar()
endSuspension = IntVar()
endElectronics = IntVar()

endChassis.set(0)
endEngine.set(0)
endFWing.set(0)
endRWing.set(0)
endUnderbody.set(0)
endSidepods.set(0)
endCooling.set(0)
endGearbox.set(0)
endBrakes.set(0)
endSuspension.set(0)
endElectronics.set(0)

# Group the wear values for easy getting/setting
startWears = [wearChassis, wearEngine, wearFWing, wearRWing, wearUnderbody, wearSidepods, wearCooling, wearGearbox, wearBrakes, wearSuspension, wearElectronics]
wearlevels = [wearlevelChassis, wearlevelEngine, wearlevelFWing, wearlevelRWing, wearlevelUnderbody, wearlevelSidepods, wearlevelCooling, wearlevelGearbox, wearlevelBrakes, wearlevelSuspension, wearlevelElectronics]
raceWears = [raceChassis, raceEngine, raceFWing, raceRWing, raceUnderbody, raceSidepods, raceCooling, raceGearbox, raceBrakes, raceSuspension, raceElectronics]
endWears = [endChassis, endEngine, endFWing, endRWing, endUnderbody, endSidepods, endCooling, endGearbox, endBrakes, endSuspension, endElectronics]

# Profile variables
profilelevelChassis = IntVar()
profilelevelEngine = IntVar()
profilelevelFWing = IntVar()
profilelevelRWing = IntVar()
profilelevelUnderbody = IntVar()
profilelevelSidepods = IntVar()
profilelevelCooling = IntVar()
profilelevelGearbox = IntVar()
profilelevelBrakes = IntVar()
profilelevelSuspension = IntVar()
profilelevelElectronics = IntVar()

profilelevelChassis.set(0)
profilelevelEngine.set(0)
profilelevelFWing.set(0)
profilelevelRWing.set(0)
profilelevelUnderbody.set(0)
profilelevelSidepods.set(0)
profilelevelCooling.set(0)
profilelevelGearbox.set(0)
profilelevelBrakes.set(0)
profilelevelSuspension.set(0)
profilelevelElectronics.set(0)

profilePartLevels = [profilelevelChassis, profilelevelEngine, profilelevelFWing, profilelevelRWing, profilelevelUnderbody, profilelevelSidepods, profilelevelCooling, profilelevelGearbox, profilelevelBrakes, profilelevelSuspension, profilelevelElectronics]

PChassis = DoubleVar()
HChassis = DoubleVar()
AChassis = DoubleVar()
PHAChassis = [PChassis, HChassis, AChassis]

PEngine = DoubleVar()
HEngine = DoubleVar()
AEngine = DoubleVar()
PHAEngine = [PEngine, HEngine, AEngine]

PFrontWing = DoubleVar()
HFrontWing = DoubleVar()
AFrontWing = DoubleVar()
PHAFrontWing = [PFrontWing, HFrontWing, AFrontWing]

PRearWing = DoubleVar()
HRearWing = DoubleVar()
ARearWing = DoubleVar()
PHARearWing = [PRearWing, HRearWing, ARearWing]

PUnderbody = DoubleVar()
HUnderbody = DoubleVar()
AUnderbody = DoubleVar()
PHAUnderbody = [PUnderbody, HUnderbody, AUnderbody]

PSidepods = DoubleVar()
HSidepods = DoubleVar()
ASidepods = DoubleVar()
PHASidepods = [PSidepods, HSidepods, ASidepods]

PCooling = DoubleVar()
HCooling = DoubleVar()
ACooling = DoubleVar()
PHACooling = [PCooling, HCooling, ACooling]

PGearbox = DoubleVar()
HGearbox = DoubleVar()
AGearbox = DoubleVar()
PHAGearbox = [PGearbox, HGearbox, AGearbox]

PBrakes = DoubleVar()
HBrakes = DoubleVar()
ABrakes = DoubleVar()
PHABrakes = [PBrakes, HBrakes, ABrakes]

PSuspension = DoubleVar()
HSuspension = DoubleVar()
ASuspension = DoubleVar()
PHASuspension = [PSuspension, HSuspension, ASuspension]

PElectronics = DoubleVar()
HElectronics = DoubleVar()
AElectronics = DoubleVar()
PHAElectronics = [PElectronics, HElectronics, AElectronics]

PParts = DoubleVar()
HParts = DoubleVar()
AParts = DoubleVar()
PHAParts = [PParts, HParts, AParts]

PHA = [PHAChassis, PHAEngine, PHAFrontWing, PHARearWing, PHAUnderbody, PHASidepods, PHACooling, PHAGearbox, PHABrakes, PHASuspension, PHAElectronics, PHAParts]

for part in PHA:
	for point in part:
		point.set(0)

profileTestingPower = DoubleVar()
profileTestingHandling = DoubleVar()
profileTestingAcceleration = DoubleVar()
profileTestingPower.set(0)
profileTestingHandling.set(0)
profileTestingAcceleration.set(0)

profileTesting = [profileTestingPower, profileTestingHandling, profileTestingAcceleration]

profilePowerTotal = IntVar()
profileHandlingTotal = IntVar()
profileAccelerationTotal = IntVar()
profilePowerTotal.set(0)
profileHandlingTotal.set(0)
profileAccelerationTotal.set(0)

profileTotals = [profilePowerTotal, profileHandlingTotal, profileAccelerationTotal]

# Creating Styles
style = ttk.Style()
style.configure("Status.Label", foreground = "black")
style.configure("Red.Label", foreground = "red")
style.configure("Orange.Label", foreground = "orange")
style.configure("Green.Label", foreground = "green")

# And a list of labels to apply the warnings
labelsStatus = []

# Build the pages
# Setup page
# BUTTONS
ttk.Button(frameSetup, text = "Calculate", command = calculate).grid(column = 1, row = 4, sticky = E+W)
rememberCredentials = ttk.Checkbutton(frameSetup, text = "Remember Credentials", onvalue = 1, offvalue = 0, variable = inputRememberCredentials)
rememberCredentials.grid(column = 1, row = 2, sticky = E+W)

# RADIO
radioQ1 = ttk.Radiobutton(frameSetup, text = "Q1", variable = inputSession, value = "Q1").grid(column = 3, row = 0, sticky = (W, E))
radioQ2 = ttk.Radiobutton(frameSetup, text = "Q2", variable = inputSession, value = "Q2").grid(column = 3, row = 1, sticky = (W, E))
radioRace = ttk.Radiobutton(frameSetup, text = "Race", variable = inputSession, value = "Race").grid(column = 3, row = 2, sticky = (W, E))
radioDry = ttk.Radiobutton(frameSetup, text = "Dry", variable = inputWeather, value = "Dry")
radioDry.grid(column = 3, row = 4, sticky = (W, E))
radioWet = ttk.Radiobutton(frameSetup, text = "Wet", variable = inputWeather, value = "Wet")
radioWet.grid(column = 3, row = 5, sticky = (W, E))

# ENTRY
entryUsername = ttk.Entry(frameSetup, width = 30, textvariable = inputUsername)
entryUsername.grid(column = 1, row = 0, sticky = (W, E))
entryPassword = ttk.Entry(frameSetup, width = 30, show = "*", textvariable = inputPassword)
entryPassword.grid(column = 1, row = 1, sticky = (W, E))

# LABELS
ttk.Label(frameSetup, text = "Email: ").grid(column = 0, row = 0, sticky = (W, E))
ttk.Label(frameSetup, text = "Password: ").grid(column = 0, row = 1, sticky = (W, E))
ttk.Label(frameSetup, text = "Session: ", padding = "40 0 0 0").grid(column = 2, row = 0, sticky = E)
ttk.Label(frameSetup, text = "Weather: ").grid(column = 2, row = 4, sticky = E)
labelSetupStatus = ttk.Label(frameSetup, textvariable = warningLabel)
labelSetupStatus.grid(column = 1, row = 3)
labelsStatus.append(labelSetupStatus)

ttk.Label(frameSetup, text = "Front Wing: ", padding = "40 0 0 0").grid(column = 5, row = 0, sticky = W+E)
ttk.Label(frameSetup, text = "Rear Wing: ", padding = "40 0 0 0").grid(column = 5, row = 1, sticky = W+E)
ttk.Label(frameSetup, text = "Engine: ", padding = "40 0 0 0").grid(column = 5, row = 2, sticky = W+E)
ttk.Label(frameSetup, text = "Brakes: ", padding = "40 0 0 0").grid(column = 5, row = 3, sticky = W+E)
ttk.Label(frameSetup, text = "Gear: ", padding = "40 0 0 0").grid(column = 5, row = 4, sticky = W+E)
ttk.Label(frameSetup, text = "Suspension: ", padding = "40 0 0 0").grid(column = 5, row = 5, sticky = W+E)

ttk.Label(frameSetup, textvariable = frontWing).grid(column = 6, row = 0)
ttk.Label(frameSetup, textvariable = rearWing).grid(column = 6, row = 1)
ttk.Label(frameSetup, textvariable = engine).grid(column = 6, row = 2)
ttk.Label(frameSetup, textvariable = brakes).grid(column = 6, row = 3)
ttk.Label(frameSetup, textvariable = gear).grid(column = 6, row = 4)
ttk.Label(frameSetup, textvariable = suspension).grid(column = 6, row = 5)

# Strategy page
# BUTTONS
ttk.Button(frameStrategy, text = "Calculate", command = calculate).grid(column = 9, columnspan = 2, row = 1, sticky = E+W)

# RADIO

# ENTRY
ttk.Entry(frameStrategy, width = 10, textvariable = inputWear, validate = "key", validatecommand = (vcmdInt, '%P'), justify = "center").grid(column = 10, row = 0, sticky = (W, E))
ttk.Entry(frameStrategy, width = 10, textvariable = inputLaps, validate = "key", validatecommand = (vcmdInt, '%P'), justify = "center").grid(column = 9, row = 4, sticky = W+E)

# LABELS
labelStrategyStatus = ttk.Label(frameStrategy, textvariable = warningLabel)
labelStrategyStatus.grid(column = 9, row = 2, columnspan = 2)
labelsStatus.append(labelStrategyStatus)
ttk.Label(frameStrategy, text = "Wear % :", padding = "0 10 5 5").grid(column = 9, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Laps", padding = "0 0 10 0", justify = "center").grid(column = 9, row = 3)
ttk.Label(frameStrategy, text = "Fuel", padding = "0 0 10 0", justify = "center").grid(column = 10, row = 3)

ttk.Label(frameStrategy, text = "Tyre", padding = "0 10").grid(column = 0, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Stops", padding = "0 10", justify = "center").grid(column = 1, row = 0, sticky = (E))
ttk.Label(frameStrategy, text = "Stint Laps", padding = "0 10", justify = "center").grid(column = 2, row = 0, sticky = W)
ttk.Label(frameStrategy, text = "Fuel Load (L)", padding = "0 10", justify = "center").grid(column = 3, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Pit Time (s)", padding = "0 10", justify = "center").grid(column = 4, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "TC Loss (s)", padding = "0 10", justify = "center").grid(column = 5, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Fuel Loss (s)", padding = "0 10", justify = "center").grid(column = 6, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Pit Total (s)", padding = "0 10", justify = "center").grid(column = 7, row = 0, sticky = (W))
ttk.Label(frameStrategy, text = "Total (s)", padding = "0 10", justify = "center").grid(column = 8, row = 0, sticky = (W))

ttk.Label(frameStrategy, text = "Extra Soft", padding = "0 0 10 0").grid(column = 0, row = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "Soft", padding = "0 0 10 0").grid(column = 0, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Medium", padding = "0 0 10 0").grid(column = 0, row = 3, sticky = (W, E))
ttk.Label(frameStrategy, text = "Hard", padding = "0 0 10 0").grid(column = 0, row = 4, sticky = (W, E))
ttk.Label(frameStrategy, text = "Rain", padding = "0 0 10 0").grid(column = 0, row = 5, sticky = (W, E))

ttk.Label(frameStrategy, textvariable = lapsUpper, justify = "center").grid(column = 9, row = 5)
ttk.Label(frameStrategy, textvariable = lapsFuelLoadLower, justify = "center").grid(column = 10, row = 4)
ttk.Label(frameStrategy, textvariable = lapsFuelLoadUpper, justify = "center").grid(column = 10, row = 5)

ttk.Label(frameStrategy, text = "Track Information", padding = "0 10 10 0").grid(column = 0, row = 6, columnspan = 2, sticky = W+E)
ttk.Label(frameStrategy, text = "Track Name:", padding = "0 0 10 0").grid(column = 0, columnspan = 2, row = 7, sticky = W)
ttk.Label(frameStrategy, text = "Laps:", padding = "0 0 10 0").grid(column = 0, columnspan = 2, row = 8, sticky = W)
ttk.Label(frameStrategy, text = "Lap Distance:", padding = "0 0 10 0").grid(column = 0, columnspan = 2, row = 9, sticky = W)
ttk.Label(frameStrategy, text = "Distance:", padding = "0 0 10 0").grid(column = 0, columnspan = 2, row = 10, sticky = W)
ttk.Label(frameStrategy, text = "Pit In/Out:", padding = "0 0 10 0").grid(column = 0, columnspan = 2, row = 11, sticky = W)

ttk.Label(frameStrategy, text = "GPRO Data", padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 6, sticky = W+S)
ttk.Label(frameStrategy, textvariable = GPROnextTrackName, padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 7, sticky = W)
ttk.Label(frameStrategy, textvariable = GPROnextTrackLaps, padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 8, sticky = W)
ttk.Label(frameStrategy, textvariable = GPROnextTrackLapDistance, padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 9, sticky = W)
ttk.Label(frameStrategy, textvariable = GPROnextTrackDistance, padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 10, sticky = W)
ttk.Label(frameStrategy, textvariable = GPROnextTrackPitInOut, padding = "0 0 10 0").grid(column = 2, columnspan = 2, row = 11, sticky = W)

x = 1
for values in grid:
	y = 1
	for value in values:
		ttk.Label(frameStrategy, textvariable = value, justify = "center").grid(column = x, row = y)
		y = y + 1
	x = x + 1

labelExtraTotal = ttk.Label(frameStrategy, textvariable = totals[0], justify = "center")
labelExtraTotal.grid(column = 8, row = 1)
labelSoftTotal = ttk.Label(frameStrategy, textvariable = totals[1], justify = "center")
labelSoftTotal.grid(column = 8, row = 2)
labelMediumTotal = ttk.Label(frameStrategy, textvariable = totals[2], justify = "center")
labelMediumTotal.grid(column = 8, row = 3)
labelHardTotal = ttk.Label(frameStrategy, textvariable = totals[3], justify = "center")
labelHardTotal.grid(column = 8, row = 4)
labelRainTotal = ttk.Label(frameStrategy, textvariable = totals[4], justify = "center")
labelRainTotal.grid(column = 8, row = 5)
labelsTotal = [labelExtraTotal, labelSoftTotal, labelMediumTotal, labelHardTotal, labelRainTotal]

# Wear page
# BUTTONS
ttk.Button(frameWear, text = "Calculate", command = calculate).grid(column = 2, columnspan = 2, row = 0, sticky = E+W)
ttk.Button(frameWear, text = "Fill", command = fillWear).grid(column = 0, columnspan = 2, row = 0, sticky = E+W)
# RADIO
# ENTRY
ttk.Entry(frameWear, width = 5, textvariable = wearClearTrackRisk, validate = "key", validatecommand = (vcmdInt, '%P'), justify = "center").grid(column = 7, row = 0, sticky = W+E)

ttk.Entry(frameWear, width = 5, textvariable = wearChassis, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 1, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearEngine, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 2, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearFWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 3, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearRWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 4, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearUnderbody, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 5, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearSidepods, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 6, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearCooling, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 7, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearGearbox, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 8, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearBrakes, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 9, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearSuspension, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 10, row = 2)
ttk.Entry(frameWear, width = 5, textvariable = wearElectronics, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 11, row = 2)

ttk.Entry(frameWear, width = 5, textvariable = wearlevelChassis, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 1, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelEngine, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 2, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelFWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 3, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelRWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 4, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelUnderbody, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 5, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelSidepods, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 6, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelCooling, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 7, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelGearbox, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 8, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelBrakes, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 9, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelSuspension, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 10, row = 3)
ttk.Entry(frameWear, width = 5, textvariable = wearlevelElectronics, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 11, row = 3)
# LABELS
labelWearStatus = ttk.Label(frameWear, textvariable = warningLabel)
labelWearStatus.grid(column = 4, row = 0, columnspan = 2)
labelsStatus.append(labelWearStatus)

ttk.Label(frameWear, text = "Risk:", padding = "5 0").grid(column = 6, row = 0, sticky = W)

ttk.Label(frameWear, text = "Chassis", padding = "2 0 2 10").grid(column = 1, row = 1)
ttk.Label(frameWear, text = "Engine", padding = "2 0 2 10").grid(column = 2, row = 1)
ttk.Label(frameWear, text = "Front Wing", padding = "2 0 2 10").grid(column = 3, row = 1)
ttk.Label(frameWear, text = "Rear Wing", padding = "2 0 2 10").grid(column = 4, row = 1)
ttk.Label(frameWear, text = "Underbody", padding = "2 0 2 10").grid(column = 5, row = 1)
ttk.Label(frameWear, text = "Sidepods", padding = "2 0 2 10").grid(column = 6, row = 1)
ttk.Label(frameWear, text = "Cooling", padding = "2 0 2 10").grid(column = 7, row = 1)
ttk.Label(frameWear, text = "Gearbox", padding = "2 0 2 10").grid(column = 8, row = 1)
ttk.Label(frameWear, text = "Brakes", padding = "2 0 2 10").grid(column = 9, row = 1)
ttk.Label(frameWear, text = "Suspension", padding = "2 0 2 10").grid(column = 10, row = 1)
ttk.Label(frameWear, text = "Electronics", padding = "2 0 2 10").grid(column = 11, row = 1)

ttk.Label(frameWear, text = "Wear Before", padding = "5").grid(column = 0, row = 2, sticky = W)
ttk.Label(frameWear, text = "Level", padding = "5").grid(column = 0, row = 3, sticky = W)
ttk.Label(frameWear, text = "Race Wear", padding = "5").grid(column = 0, row = 4, sticky = W)
ttk.Label(frameWear, text = "Wear After", padding = "5").grid(column = 0, row = 5, sticky = W)

ttk.Label(frameWear, textvariable = raceChassis, padding = "5 0").grid(column = 1, row = 4)
ttk.Label(frameWear, textvariable = raceEngine, padding = "5 0").grid(column = 2, row = 4)
ttk.Label(frameWear, textvariable = raceFWing, padding = "5 0").grid(column = 3, row = 4)
ttk.Label(frameWear, textvariable = raceRWing, padding = "5 0").grid(column = 4, row = 4)
ttk.Label(frameWear, textvariable = raceUnderbody, padding = "5 0").grid(column = 5, row = 4)
ttk.Label(frameWear, textvariable = raceSidepods, padding = "5 0").grid(column = 6, row = 4)
ttk.Label(frameWear, textvariable = raceCooling, padding = "5 0").grid(column = 7, row = 4)
ttk.Label(frameWear, textvariable = raceGearbox, padding = "5 0").grid(column = 8, row = 4)
ttk.Label(frameWear, textvariable = raceBrakes, padding = "5 0").grid(column = 9, row = 4)
ttk.Label(frameWear, textvariable = raceSuspension, padding = "5 0").grid(column = 10, row = 4)
ttk.Label(frameWear, textvariable = raceElectronics, padding = "5 0").grid(column = 11, row = 4)

labelEndChassis = ttk.Label(frameWear, textvariable = endChassis, padding = "5 0")
labelEndChassis.grid(column = 1, row = 5)
labelEndEngine = ttk.Label(frameWear, textvariable = endEngine, padding = "5 0")
labelEndEngine.grid(column = 2, row = 5)
labelEndFWing = ttk.Label(frameWear, textvariable = endFWing, padding = "5 0")
labelEndFWing.grid(column = 3, row = 5)
labelEndRWing = ttk.Label(frameWear, textvariable = endRWing, padding = "5 0")
labelEndRWing.grid(column = 4, row = 5)
labelEndUnderbody = ttk.Label(frameWear, textvariable = endUnderbody, padding = "5 0")
labelEndUnderbody.grid(column = 5, row = 5)
labelEndSidepods = ttk.Label(frameWear, textvariable = endSidepods, padding = "5 0")
labelEndSidepods.grid(column = 6, row = 5)
labelEndCooling = ttk.Label(frameWear, textvariable = endCooling, padding = "5 0")
labelEndCooling.grid(column = 7, row = 5)
labelEndGearbox = ttk.Label(frameWear, textvariable = endGearbox, padding = "5 0")
labelEndGearbox.grid(column = 8, row = 5)
labelEndBrakes = ttk.Label(frameWear, textvariable = endBrakes, padding = "5 0")
labelEndBrakes.grid(column = 9, row = 5)
labelEndSuspension = ttk.Label(frameWear, textvariable = endSuspension, padding = "5 0")
labelEndSuspension.grid(column = 10, row = 5)
labelEndElectronics = ttk.Label(frameWear, textvariable = endElectronics, padding = "5 0")
labelEndElectronics.grid(column = 11, row = 5)

endLabels = [labelEndChassis, labelEndEngine, labelEndFWing, labelEndRWing, labelEndUnderbody, labelEndSidepods, labelEndCooling, labelEndGearbox, labelEndBrakes, labelEndSuspension, labelEndElectronics]

# Profile Page
# BUTTONS
ttk.Button(frameProfile, text = "Fill", command = fillProfile).grid(column = 0, columnspan = 2, row = 0, sticky = E+W)
ttk.Button(frameProfile, text = "Calculate", command = calculate).grid(column = 2, columnspan = 2, row = 0, sticky = E+W)

# ENTRY
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelChassis, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 1, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelEngine, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 2, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelFWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 3, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelRWing, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 4, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelUnderbody, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 5, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelSidepods, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 6, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelCooling, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 7, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelGearbox, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 8, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelBrakes, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 9, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelSuspension, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 10, row = 2)
ttk.Entry(frameProfile, width = 5, textvariable = profilelevelElectronics, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 11, row = 2)

ttk.Entry(frameProfile, width = 5, textvariable = profileTestingPower, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 13, row = 3)
ttk.Entry(frameProfile, width = 5, textvariable = profileTestingHandling, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 13, row = 4)
ttk.Entry(frameProfile, width = 5, textvariable = profileTestingAcceleration, justify = "center", validate = "key", validatecommand = (vcmdInt, '%P')).grid(column = 13, row = 5)

# LABELS
labelProfileStatus = ttk.Label(frameProfile, textvariable = warningLabel)
labelProfileStatus.grid(column = 4, row = 0, columnspan = 2)
labelsStatus.append(labelProfileStatus)

ttk.Label(frameProfile, text = "Part").grid(column = 0, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Level").grid(column = 0, row = 2, sticky = W)
ttk.Label(frameProfile, text = "Power").grid(column = 0, row = 3, sticky = W)
ttk.Label(frameProfile, text = "Handling").grid(column = 0, row = 4, sticky = W)
ttk.Label(frameProfile, text = "Acceleration").grid(column = 0, row = 5, sticky = W)

ttk.Label(frameProfile, text = "Chassis").grid(column = 1, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Engine").grid(column = 2, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Front Wing").grid(column = 3, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Rear Wing").grid(column = 4, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Underbody").grid(column = 5, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Sidepods").grid(column = 6, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Cooling").grid(column = 7, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Gearbox").grid(column = 8, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Brakes").grid(column = 9, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Suspension").grid(column = 10, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Electronics").grid(column = 11, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Part Total").grid(column = 12, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Testing").grid(column = 13, row = 1, sticky = W)
ttk.Label(frameProfile, text = "Total").grid(column = 14, row = 1, sticky = W)

ttk.Label(frameProfile, textvariable = profilePowerTotal).grid(column = 14, row = 3)
ttk.Label(frameProfile, textvariable = profileHandlingTotal).grid(column = 14, row = 4)
ttk.Label(frameProfile, textvariable = profileAccelerationTotal).grid(column = 14, row = 5)

x = 1
for part in PHA:
	y = 3
	for point in part:
		ttk.Label(frameProfile, textvariable = point, justify = "center").grid(column = x, row = y)
		y += 1
	x += 1

# Set the style for the status labels
for label in labelsStatus:
	label.configure(style = "Status.Label")

# Automatically organize the window
for child in frameSetup.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameStrategy.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameWear.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameProfile.winfo_children(): child.grid_configure(padx=5, pady=5)

# Set some QOL things, like auto focus for text entry and how to handle an "Enter" press
entryUsername.focus()
root.bind('<Return>', calculate)
#root.resizable(False, False)

# Pack the notebook after doing everything else to set the window size and organize everything
notebook.pack(expand = True, fill = BOTH)
notebook.enable_traversal()

# Open the window
root.mainloop()