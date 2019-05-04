from tkinter import Tk, ttk, StringVar, IntVar, DoubleVar, E, W, S, BOTH	# To create the GUI
from tkinter.ttk import Notebook	# For tabs in the GUI
from pathlib import Path		# For data paths
from lxml import html, etree	# For xpath trees

import requests			# For html sessions
import re				# For regular expressions
import csv				# For writing data to CSV files
import os				# For getting directory paths
import threading		# For multi threading
import logging			# For error handling and debugging

# Import external data
from calcs import setupCalc, strategyCalc, wearCalc, profileCalc
from funcs import *

# Logging setup
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%y-%m-%d %H:%M')
logger = logging.getLogger(__name__)
# Handlers
dataPath = str(Path.home()) + "\\Documents\\GAPP"
if not os.path.exists(dataPath):
	os.makedirs(dataPath)
fLogFileName = str(Path.home()) + r"\Documents\GAPP\error.log"
gLogFileName = str(Path.home()) + r"\Documents\GAPP\logging.log"
f_handler = logging.FileHandler(fLogFileName)
g_handler = logging.FileHandler(gLogFileName)
f_handler.setLevel(logging.ERROR)
g_handler.setLevel(logging.DEBUG)
# Handler Format
f_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
g_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# Add Handlers
logger.addHandler(f_handler)
logger.addHandler(g_handler)

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
logger.info("Getting reference to GAPP folder in Documents for storage")
dataPath = str(Path.home()) + "\\Documents\\GAPP"
if not os.path.exists(dataPath):
	try:
		logger.info("No GAPP folder found in documents, creating it")
		os.makedirs(dataPath)
	except Exception:
		logger.exception("Unable to create GAPP folder in documents, GAPP may not have permissions to do so")

filename = dataPath + "\\data.dat"

try:
	logger.info("Creating login data file")
	open(filename, "x").close()	
except:
	logger.info("Login data file already exists, skipping")
	pass

try:
	logger.info("Opening login data file for reading")
	file = open(filename, "r")
	credentialCheck = int(float(file.readline()))
	username = file.readline()
	password = file.readline()
	logger.info("Login data file read successfully")
except:
	logger.info("Unable to open or read login data file, setting credential check to 0")
	credentialCheck = 0
finally:
	logger.info("Closing login data file")
	file.close()

# Thread Controller - starts and manages threads as required
def calculateThreadController(*args):
	logger.info("Writing user data to login data file")
	checkData(filename, inputRememberCredentials.get(), inputUsername.get(), inputPassword.get())

	logger.info("Getting tab information to create thread name")
	threadName = notebook.tab(notebook.select(), "text")
	threads = threading.enumerate()

	for thread in threads:
		if not threadName == thread.name:
			logger.info("Starting new thread: %s", threadName)
			threading.Thread(daemon = True, name = threadName, target = calculate, args = (threadName,)).start()
		else:
			logger.warning("Thread of same name already exists: %s", threadName)
		

def fillThreadController(*args):
	logger.info("Writing user data to login data file")
	checkData(filename, inputRememberCredentials.get(), inputUsername.get(), inputPassword.get())

	logger.info("Getting tab information to create thread name")
	threadName = notebook.tab(notebook.select(), "text")
	threads = threading.enumerate()

	for thread in threads:
		if not threadName == thread.name:
			logger.info("Starting new thread: %s", threadName)
			if threadName == "Car Wear":
				threading.Thread(daemon = True, name = threadName, target = fillWear).start()
			elif threadName == "PHA":
				threading.Thread(daemon = True, name = threadName, target = fillProfile).start()
		else:
			logger.warning("Thread of same name already exists: %s", threadName)

# Calculate the setup and others
def calculate(tab):
	logger.info("Starting calculation process")
	try:
		logger.info("Getting user login details")
		username = str(inputUsername.get())
		password = str(inputPassword.get())

		logger.info("Checking user login details are correct and user is in Viper team")
		if(not checkLogin(username, password)):
			logger.warning("Login details are incorrect")
			warningLabel.set("Incorrect Login Details")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return
		elif(not checkTeam(username, password)):
			logger.warning("User not in VIPER team")
			warningLabel.set("VIPER Family Team Only")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return

		if(tab == "Setup"):
			logger.info("Starting Setup calcuation")
			weather = str(inputWeather.get())
			session = str(inputSession.get())
			setup = setupCalc(username, password, weather, session)

			logger.info("Applying calculated setup")
			frontWing.set(str(setup[0]))
			rearWing.set(str(setup[1]))
			engine.set(str(setup[2]))
			brakes.set(str(setup[3]))
			gear.set(str(setup[4]))
			suspension.set(str(setup[5]))
		elif(tab == "Strategy"):
			logger.info("Getting strategy input")
			try:
				wear = float(re.findall(r'\d+', inputWear.get())[0])
			except:
				try:
					wear = float(re.findall(r'\d+.\d+', inputWear.get())[0])
				except:
					logger.warning("Wear input incorrect format, despite input control")
					wear = 0.0
					inputWear.set(0)

			try:
				laps = int(re.findall(r'\d+', inputLaps.get())[0])
			except:
				try:
					laps = inputLaps.get()
				except:
					logger.warning("Laps input incorrect format, despite input control")
					laps = 0
					inputLaps.set(0)

			lapsUpper.set(laps + 1)
			logger.info("Starting Strategy calculation")
			strategy = strategyCalc(username, password, wear, laps)

			logger.info("Applying calculated strategy")
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

			logger.info("Getting track information for stragey tab")
			GPROnextTrackName.set(strategy[10])
			GPROnextTrackLaps.set(strategy[11])
			GPROnextTrackLapDistance.set(strategy[12])
			GPROnextTrackDistance.set(strategy[13])
			GPROnextTrackPitInOut.set(strategy[14])
		elif(tab == "Car Wear"):
			logger.info("Creating GPRO session for web scraping")
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

			# Find userful URLs
			logger.info("Getting GPRO URLs needed for wear calculation")
			driverURL = "https://gpro.net/gb/" + tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")[0]
			trackURL = "https://gpro.net/gb/" + tree.xpath("//a[starts-with(@href, 'TrackDetails.asp')]/@href")[0]

			# Get the driver details
			logger.info("Getting Driver information")
			driverResult = session.get(driverURL, headers=dict(referer=driverURL))
			tree = html.fromstring(driverResult.content)
			driverConcentration = int(tree.xpath("normalize-space(//td[contains(@id, 'Conc')]/text())"))
			driverTalent = int(tree.xpath("normalize-space(//td[contains(@id, 'Talent')]/text())"))
			driverExperience = int(tree.xpath("normalize-space(//td[contains(@id, 'Experience')]/text())"))
			driverFactor = (0.998789138 ** driverConcentration) * (0.998751839 ** driverTalent) * (0.998707677 ** driverExperience)

			# Get the track details
			logger.info("Getting track information")
			trackResult = session.get(trackURL, headers=dict(referer=trackURL))
			tree = html.fromstring(trackResult.content)
			trackName = str(tree.xpath("normalize-space(//h1[contains(@class, 'block')]/text())"))
			trackName = trackName.strip()

			logger.info("Checking user input is in corret format")
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

			logger.info("Calculating and applying car wear")
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
			logger.info("Starting PHA calculation")
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
	
			logger.info("Applying calculated PHA")
			PParts.set(int(round(PTotal, 0)))
			HParts.set(int(round(HTotal, 0)))
			AParts.set(int(round(ATotal, 0)))

			for i in range(3):
				subTotal = 0
				subTotal += PHAParts[i].get()
				subTotal += profileTesting[i].get()
				profileTotals[i].set(int(round(subTotal, 0)))
		elif(tab == "Analysis"):
			# First step is to import current data, which will allow a long running data file for the user
			pastSessionData = []
			try:
				with open("RaceData.csv", mode="r") as csvFile:
					csvReader = csv.DictReader(csvFile)
					for row in csvReader:
						rowData = {}
						for key in row:
							rowData[key] = row[key]
						pastSessionData.append(rowData)
			except:
				logger.warning("Unable to open RaceData.csv data file - might not exist or permission is denied")

			logger.info("Starting pre- and post-race analysis")
			# Create the logon payload and create the session
			username = entryUsername.get()
			password = entryPassword.get()
			logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
			session = requests.session()
			loginURL = "https://gpro.net/gb/Login.asp"
			logonResult = session.post(loginURL, data=logonData, headers=dict(referer=loginURL))
			
			# Gather the session information for the upcoming or past race, based on input choice
			logger.info("Getting ID data for season and race")
			tree = html.fromstring(logonResult.content)
			rawData = tree.xpath("normalize-space(//strong[contains(text(), 'Next race:')]/../text())")
			reSearch = re.findall(r"(\d{2}),\s\w+\s(\d+)", rawData)[0]
			seasonNumber = reSearch[0]
			raceNumber = reSearch[1]
		
			raceState = inputAnalysis.get()

			if(raceState == "Pre-Race"):
				logger.info("Calculating for Pre-Race")
				# Creating raceID
				if(len(raceNumber) == 1):
					raceNumber = "0" + raceNumber
				raceID = "S" + seasonNumber + "R" + raceNumber

				# Define required URLs
				Q1URL = "https://www.gpro.net/gb/Qualify.asp"
				Q2URL = "https://www.gpro.net/gb/Qualify2.asp"
				SetupURL = "https://www.gpro.net/gb/RaceSetup.asp"

				# Get session data
				Q1Result = session.get(Q1URL, headers=dict(referer=Q1URL))
				Q2Result = session.get(Q2URL, headers=dict(referer=Q2URL))
				SetupResult = session.get(SetupURL, headers=dict(referer=SetupURL))

				# List to store the created dictionaries, for easier looped writing
				sessionDicts = []

				# Process data
				# Q1
				try:
					logger.info("Analysing for Q1")
					tree = html.fromstring(Q1Result.content)
					Q1LapData = tree.xpath("//img[contains(@src, 'suppliers')]/../..//*[string-length(text()) > 2]/text()")
					Q1LapData += tree.xpath("//img[contains(@src, 'suppliers')]/@alt")
					Q1LapData.remove(Q1LapData[0])
					Q1LapData.remove(Q1LapData[1])
					Q1LapDict = {
						"RaceID": raceID,
						"Session": "Q1",
						"LapTime": Q1LapData[0],
						"FWing": Q1LapData[1],
						"RWing": Q1LapData[2],
						"Engine": Q1LapData[3],
						"Brakes": Q1LapData[4],
						"Gear": Q1LapData[5],
						"Suspension": Q1LapData[6],
						"Compound": Q1LapData[7],
						"Risk": Q1LapData[8],
						"Supplier": Q1LapData[9]
					}
					sessionDicts.append(Q1LapDict)
				except Exception:
					logger.exception("Pre-Race analysis failed in Q1 - user probably hasn't done Q1 yet")

				# Q2
				try:
					logger.info("Analysing for Q2")
					tree = html.fromstring(Q2Result.content)
					Q2LapData = tree.xpath("//img[contains(@src, 'suppliers')]/../..//*[string-length(text()) > 2]/text()")
					Q2LapData += tree.xpath("//img[contains(@src, 'suppliers')]/@alt")
					Q2LapData.remove(Q2LapData[0])
					Q2LapData.remove(Q2LapData[1])
					Q2LapDict = {
						"RaceID": raceID,
						"Session": "Q2",
						"LapTime": Q2LapData[0],
						"FWing": Q2LapData[1],
						"RWing": Q2LapData[2],
						"Engine": Q2LapData[3],
						"Brakes": Q2LapData[4],
						"Gear": Q2LapData[5],
						"Suspension": Q2LapData[6],
						"Compound": Q2LapData[7],
						"Risk": Q2LapData[8],
						"Supplier": Q2LapData[9]
					}
					sessionDicts.append(Q2LapDict)
				except Exception:
					logger.exception("Pre-Race analysis failed in Q2 - user probably hasn't done Q2 yet")
					return

				# Setup
				try:
					logger.info("Anlysing race setup")
					tree = html.fromstring(SetupResult.content)
					SetupDict = {}
					# Session Information
					SetupDict["RaceID"] = raceID
					SetupDict["Session"] = "Setup"
					# Car Setup
					SetupDict["FWing"] = str(tree.xpath("//input[contains(@id, 'FWing')]/@value")[0])
					SetupDict["RWing"] = str(tree.xpath("//input[contains(@id, 'RWing')]/@value")[0])
					SetupDict["Engine"] = str(tree.xpath("//input[contains(@id, 'Engine')]/@value")[0])
					SetupDict["Brakes"] = str(tree.xpath("//input[contains(@id, 'Brakes')]/@value")[0])
					SetupDict["Gear"] = str(tree.xpath("//input[contains(@id, 'Gear')]/@value")[0])
					SetupDict["Suspension"] = str(tree.xpath("//input[contains(@id, 'Suspension')]/@value")[0])
					# Fuel
					SetupDict["FuelStart"] = str(tree.xpath("//input[contains(@name, 'FuelStart')]/@value")[0])
					SetupDict["FuelStop1"] = str(tree.xpath("//input[contains(@name, 'FuelStop1')]/@value")[0])
					SetupDict["FuelStop2"] = str(tree.xpath("//input[contains(@name, 'FuelStop2')]/@value")[0])
					SetupDict["FuelStop3"] = str(tree.xpath("//input[contains(@name, 'FuelStop3')]/@value")[0])
					SetupDict["FuelStop4"] = str(tree.xpath("//input[contains(@name, 'FuelStop4')]/@value")[0])
					SetupDict["FuelStop5"] = str(tree.xpath("//input[contains(@name, 'FuelStop5')]/@value")[0])
					# Risks
					SetupDict["RiskOver"] = str(tree.xpath("//input[contains(@name, 'RiskOver')]/@value")[0])
					SetupDict["RiskDefend"] = str(tree.xpath("//input[contains(@name, 'RiskDefend')]/@value")[0])
					SetupDict["DriverRisk"] = str(tree.xpath("//input[@name='DriverRisk']/@value")[0])
					SetupDict["RiskWet"] = str(tree.xpath("//input[contains(@name, 'RiskWet')]/@value")[0])
					SetupDict["DriverRiskProb"] = str(tree.xpath("//input[contains(@name, 'DriverRiskProb')]/@value")[0])
					# Boosts
					SetupDict["BoostLap1"] = str(tree.xpath("//input[contains(@name, 'BoostLap1')]/@value")[0])
					SetupDict["BoostLap2"] = str(tree.xpath("//input[contains(@name, 'BoostLap2')]/@value")[0])
					SetupDict["BoostLap3"] = str(tree.xpath("//input[contains(@name, 'BoostLap3')]/@value")[0])
					sessionDicts.append(SetupDict)
				except Exception:
					logger.exception("Pre-Race analysis failed in race setup - user probably hasn't done race setup yet")

				# Write the data to file
				try:
					logger.info("Writing pre-race analysis to CSV")
					with open("RaceData.csv", "a", newline = "") as csvFile:
						fieldnames = [
							"RaceID",
							"Session",
							"LapTime",
							"FWing",
							"RWing",
							"Engine",
							"Brakes",
							"Gear",
							"Suspension",
							"Compound",
							"Risk",
							"Supplier",
							"FuelStart",
							"FuelStop1",
							"FuelStop2",
							"FuelStop3",
							"FuelStop4",
							"FuelStop5",
							"RiskOver",
							"RiskDefend",
							"DriverRisk",
							"RiskWet",
							"DriverRiskProb",
							"BoostLap1",
							"BoostLap2",
							"BoostLap3"
						]

						logger.info("Writing pre-race data to CSV file")
						writer = csv.DictWriter(csvFile, fieldnames = fieldnames)
						if len(pastSessionData) == 0:
							writer.writeheader()
						for sessionDict in sessionDicts:
							if not any(session["RaceID"] == sessionDict["RaceID"] and session["Session"] == sessionDict["Session"] for session in pastSessionData):
								try:
									logger.info("Writing session to data file")
									writer.writerow(sessionDict)
								except Exception:
									logger.exception("Unable to write session to data file")
							else:
								logger.warning("Session already exists in RaceData.csv")
				except Exception:
					logger.exception("Unable to open data file for analysis - file might be open in another application")
					warningLabel.set("File error: permission denied")
					foregroundColour("Status.Label", "Red")
					root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
					return
						
			elif(raceState == "Post-Race"):
				logger.info("Calculating for Post-Race")
				pass
			else:
				logger.error("Unable to get session information, so unable to perform analysis, this shouldn't be possible with radio buttons")
				warningLabel.set("Error")
				foregroundColour("Status.Label", "Red")
				root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
				return

		logger.info("Updating status label to notify user of completed calculations")
		warningLabel.set("Updated")
		foregroundColour("Status.Label", "#00FF00")
		root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
	except Exception:
		logger.exception("Something went wrong with calculations, see exception")

def fillWear():
	logger.info("Starting fillWear() function")
	try:
		username = entryUsername.get()
		password = entryPassword.get()

		if(not checkLogin(username, password)):
			logger.warning("Incorrect login details provided by user")
			warningLabel.set("Incorrect Login Details")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return
		elif(not checkTeam(username, password)):
			logger.warning("User not in team Viper")
			warningLabel.set("VIPER Family Team Only")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return

		# Create our logon payload. 'hiddenToken' may change at a later date.
		logger.info("Starting GPRO session for wear fill")
		logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
		
		# Logon to GPRO using the logon information provided and store that under our session
		session = requests.session()
		loginURL = "https://gpro.net/gb/Login.asp"
		session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

		# URL for car
		carURL = "https://www.gpro.net/gb/UpdateCar.asp"

		# Request the car information page and scrape the car character and part level and wear data
		logger.info("Getting car wear information")
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
			carWearChassis = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/font/text())"))
		wearChassis.set(int((re.findall(r"\d+", carWearChassis))[0]))

		carWearEngine = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/text())"))
		if(carWearEngine == ""):
			carWearEngine = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/font/text())"))
		wearEngine.set(int((re.findall(r"\d+", carWearEngine))[0]))

		carWearFrontWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/text())"))
		if(carWearFrontWing == ""):
			carWearFrontWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/font/text())"))
		wearFWing.set(int((re.findall(r"\d+", carWearFrontWing))[0]))

		carWearRearWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/text())"))
		if(carWearRearWing == ""):
			carWearRearWing = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/font/text())"))
		wearRWing.set(int((re.findall(r"\d+", carWearRearWing))[0]))

		carWearUnderbody = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/text())"))
		if(carWearUnderbody == ""):
			carWearUnderbody = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/font/text())"))
		wearUnderbody.set(int((re.findall(r"\d+", carWearUnderbody))[0]))

		carWearSidepod = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/text())"))
		if(carWearSidepod == ""):
			carWearSidepod = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/font/text())"))
		wearSidepods.set(int((re.findall(r"\d+", carWearSidepod))[0]))

		carWearCooling = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/text())"))
		if(carWearCooling == ""):
			carWearCooling = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/font/text())"))
		wearCooling.set(int((re.findall(r"\d+", carWearCooling))[0]))

		carWearGears = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/text())"))
		if(carWearGears == ""):
			carWearGears = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/font/text())"))
		wearGearbox.set(int((re.findall(r"\d+", carWearGears))[0]))

		carWearBrakes = str(tree.xpath(r"normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/text())"))
		if(carWearBrakes == ""):
			carWearBrakes = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/font/text())"))
		wearBrakes.set(int((re.findall(r"\d+", carWearBrakes))[0]))

		carWearSuspension = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/text())"))
		if(carWearSuspension == ""):
			carWearSuspension = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/font/text())"))
		wearSuspension.set(int((re.findall(r"\d+", carWearSuspension))[0]))

		carWearElectronics = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/text())"))
		if(carWearElectronics == ""):
			carWearElectronics = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/font/text())"))
		wearElectronics.set(int((re.findall(r"\d+", carWearElectronics))[0]))
	except Exception:
		logger.exception("Unable to fill wear, see exception for details")

def fillProfile():
	logger.info("Starting fillProfile() function")
	try:
		username = entryUsername.get()
		password = entryPassword.get()

		if(not checkLogin(username, password)):
			logger.warning("Incorrect login details provided by user")
			warningLabel.set("Incorrect Login Details")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))
			return
		elif(not checkTeam(username, password)):
			logger.warning("User not in team Viper")
			warningLabel.set("VIPER Family Team Only")
			foregroundColour("Status.Label", "Red")
			root.after(1000, lambda: foregroundColour("Status.Label", "Black"))

		# Create our logon payload. 'hiddenToken' may change at a later date.
		logger.info("Starting GPRO session for profile fill")
		logonData = {'textLogin':username, 'textPassword':password, 'hiddenToken':'9da482f717cf1319f10f55e35ab767a5', 'Logon':'Login', 'LogonFake':'Sign in'}
		
		# Logon to GPRO using the logon information provided and store that under our session
		session = requests.session()
		loginURL = "https://gpro.net/gb/Login.asp"
		session.post(loginURL, data=logonData, headers=dict(referer=loginURL))

		# URL for car
		carURL = "https://www.gpro.net/gb/UpdateCar.asp"

		# Request the car information page and scrape the car character and part level and wear data
		logger.info("Getting car profile data")
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
	except Exception:
		logger.exception("Unable to fill car character profile information - see exception for details")


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
frameAnalysis = ttk.Frame(notebook, name = "analysis")

# Add the pages to notebook
notebook.add(frameSetup, text = "Setup")
notebook.add(frameStrategy, text = "Strategy")
notebook.add(frameWear, text = "Car Wear")
notebook.add(frameProfile, text = "PHA")
notebook.add(frameAnalysis, text = "Analysis")

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

# Analysis variables
# INPUT
inputAnalysis = StringVar()
inputAnalysis.set("Pre-Race")

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
ttk.Button(frameSetup, text = "Calculate", command = calculateThreadController).grid(column = 1, row = 4, sticky = E+W)
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
ttk.Button(frameStrategy, text = "Calculate", command = calculateThreadController).grid(column = 9, columnspan = 2, row = 1, sticky = E+W)

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
ttk.Button(frameWear, text = "Calculate", command = calculateThreadController).grid(column = 2, columnspan = 2, row = 0, sticky = E+W)
ttk.Button(frameWear, text = "Fill", command = fillThreadController).grid(column = 0, columnspan = 2, row = 0, sticky = E+W)
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
ttk.Button(frameProfile, text = "Fill", command = fillThreadController).grid(column = 0, columnspan = 2, row = 0, sticky = E+W)
ttk.Button(frameProfile, text = "Calculate", command = calculateThreadController).grid(column = 2, columnspan = 2, row = 0, sticky = E+W)

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

# Analysis Page
# BUTTONS
ttk.Button(frameAnalysis, text = "Calculate", command = calculateThreadController).grid(column = 0, columnspan = 2, row = 0, sticky = E+W, padx = 5, pady = 5)

# RADIOS
radioQ1 = ttk.Radiobutton(frameAnalysis, text = "Pre-Race", variable = inputAnalysis, value = "Pre-Race").grid(column = 3, row = 0, sticky = (W, E), padx = 5, pady = 5)
radioQ2 = ttk.Radiobutton(frameAnalysis, text = "Post-Race", variable = inputAnalysis, value = "Post-Race").grid(column = 3, row = 1, sticky = (W, E), padx = 5, pady = 5)

# LABELS
labelAnalysisStatus = ttk.Label(frameAnalysis, textvariable = warningLabel)
labelAnalysisStatus.grid(column = 0, row = 1, columnspan = 1)
labelsStatus.append(labelAnalysisStatus)

# Set the style for the status labels
for label in labelsStatus:
	label.configure(style = "Status.Label")

# Automatically organize the window
for child in frameSetup.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameStrategy.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameWear.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameProfile.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameAnalysis.winfo_children(): child.grid_configure(padx = 5, pady = 5)

# Set some QOL things, like auto focus for text entry and how to handle an "Enter" press
entryUsername.focus()
root.bind('<Return>', calculateThreadController)
root.resizable(False, False)

# Pack the notebook after doing everything else to set the window size and organize everything
notebook.pack(expand = True, fill = BOTH)
notebook.enable_traversal()

# Open the window
root.mainloop()