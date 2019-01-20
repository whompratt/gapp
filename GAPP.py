from tkinter import *
from tkinter import ttk
import requests
import re
import csv
import collections
import math
from lxml import html
from lxml import etree


# Data collection function
def collection(username, password, weather, temp, wear, clearTrackRisk):
	token = "9da482f717cf1319f10f55e35ab767a5"
	logon = "Login"
	logonFake = "Sign in"
	
	data = {'textLogin':username, 'textPassword':password, 'token':token, 'Logon':logon, 'LogonFake':logonFake}
	
	weather = weather.upper()	
	
	# Logon to GPRO using the logon information provided
	session = requests.session()
	login_url = "https://gpro.net/gb/Login.asp"
	logonResult = session.post(login_url, data=data, headers=dict(referer=login_url))
	
	# After logging in, gather the home page information and collect driver ID and track ID
	tree = html.fromstring(logonResult.content)
	driverID = tree.xpath("//a[starts-with(@href, 'DriverProfile.asp')]/@href")
	try:
		driver_url = "https://gpro.net/gb/" + driverID[0]
	except:
		return [0, 0, 0, 0, 0, 0]
	teamName = tree.xpath("//a[starts-with(@href, 'TeamProfile.asp')]/text()")
	if(teamName[0] != "VIPER AUTOSPORT") and (teamName[0] != "TEAM VIPER") and (teamName[0] != "VIPER RACING"):
		return [1, 0, 0, 0, 0, 0]
	trackID = tree.xpath("//a[starts-with(@href, 'TrackDetails.asp')]/@href")
	track_url = "https://gpro.net/gb/" + trackID[0]
	car_url = "https://www.gpro.net/gb/UpdateCar.asp"
	race_url = "https://www.gpro.net/gb/RaceSetup.asp"
	managerID = tree.xpath("//a[contains(@href, 'viewnation')]/../a[2]/@href")
	manager_url = "https://gpro.net/gb/" + managerID[0]
	
	
	# Request the driver information page and scrape the driver data
	driverResult = session.get(driver_url, headers=dict(referer=driver_url))
	tree = html.fromstring(driverResult.content)
	driverOve = int(tree.xpath("normalize-space(//tr[contains(@data-step, '4')]//td/text())"))
	driverCon = int(tree.xpath("normalize-space(//td[contains(@id, 'Conc')]/text())"))
	driverTal = int(tree.xpath("normalize-space(//td[contains(@id, 'Talent')]/text())"))
	driverAgg = int(tree.xpath("normalize-space(//td[contains(@id, 'Aggr')]/text())"))
	driverExp = int(tree.xpath("normalize-space(//td[contains(@id, 'Experience')]/text())"))
	driverTec = int(tree.xpath("normalize-space(//td[contains(@id, 'TechI')]/text())"))
	driverSta = int(tree.xpath("normalize-space(//td[contains(@id, 'Stamina')]/text())"))
	driverCha = int(tree.xpath("normalize-space(//td[contains(@id, 'Charisma')]/text())"))
	driverMot = int(tree.xpath("normalize-space(//td[contains(@id, 'Motivation')]/text())"))
	driverRep = int(tree.xpath("normalize-space(//tr[contains(@data-step, '13')]//td/text())"))
	driverWei = int(tree.xpath("normalize-space(//tr[contains(@data-step, '14')]//td/text())"))
	driverAge = int(tree.xpath("normalize-space(//tr[contains(@data-step, '15')]//td/text())"))


	# Request the manager page and scrape tyre data
	managerResult = session.get(manager_url, headers = dict(referer = manager_url))
	tree = html.fromstring(managerResult.content)
	tyreSupplier = str(tree.xpath("//img[contains(@src, 'suppliers')]/@alt")[0])

	
	# Request the track information page and scrape the track data
	trackResult = session.get(track_url, headers=dict(referer=track_url))
	tree = html.fromstring(trackResult.content)
	trackNam = str(tree.xpath("normalize-space(//h1[contains(@class, 'block')]/text())"))
	trackNam = trackNam.strip()
	trackPow = int(tree.xpath("normalize-space(//td[contains(text(), 'Power')]/following-sibling::td/@title)"))
	trackHan = int(tree.xpath("normalize-space(//td[contains(text(), 'Handling')]/following-sibling::td/@title)"))
	trackAcc = int(tree.xpath("normalize-space(//td[contains(text(), 'Acceleration')]/following-sibling::td/@title)"))
	trackDst = str(tree.xpath("normalize-space(//td[contains(text(), 'Race distance')]/following-sibling::td/text())"))
	trackDst = float((re.findall("\d+.\d+", trackDst))[0])
	trackLDs = str(tree.xpath("normalize-space(//td[contains(text(), 'Lap distance')]/following-sibling::td/text())"))
	trackLDs = float((re.findall("\d+.\d+", trackLDs))[0])
	trackLps = int(tree.xpath("normalize-space(//td[contains(text(), 'Laps')]/following-sibling::td/text())"))
	trackPit = str(tree.xpath("normalize-space(//td[contains(text(), 'Time in')]/following-sibling::td/text())"))
	trackPit = float((re.findall("\d+.\d+", trackPit))[0])
	trackDow = str(tree.xpath("normalize-space(//td[contains(text(), 'Downforce')]/following-sibling::td/text())"))
	trackOtk = str(tree.xpath("normalize-space(//td[contains(text(), 'Overtaking')]/following-sibling::td/text())"))
	trackSus = str(tree.xpath("normalize-space(//td[contains(text(), 'Suspension')]/following-sibling::td/text())"))
	trackFue = str(tree.xpath("normalize-space(//td[contains(text(), 'Fuel consumption')]/following-sibling::td/text())"))
	trackTyr = str(tree.xpath("normalize-space(//td[contains(text(), 'Tyre wear')]/following-sibling::td/text())"))
	trackGrp = str(tree.xpath("normalize-space(//td[contains(text(), 'Grip level')]/following-sibling::td/text())"))


	# Request race strategy pace and scrape the race weather data
	raceResult = session.get(race_url, headers=dict(referer=race_url))
	tree = html.fromstring(raceResult.content)
	RtempRangeOne = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[1]/text())"))
	RtempRangeTwo = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[2]/td[2]/text())"))
	RtempRangeThr = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[1]/text())"))
	RtempRangeFou = str(tree.xpath("normalize-space(//td[contains(text(), 'Temp')]/../../tr[4]/td[2]/text())"))
	# This returns results like "Temp: 12*-17*", but we want just integers, so clean up the values
	RtempMinOne = int((re.findall("\d+", RtempRangeOne))[0])
	RtempMaxOne = int((re.findall("\d+", RtempRangeOne))[1])
	RtempMinTwo = int((re.findall("\d+", RtempRangeTwo))[0])
	RtempMaxTwo = int((re.findall("\d+", RtempRangeTwo))[1])
	RtempMinThr = int((re.findall("\d+", RtempRangeThr))[0])
	RtempMaxThr = int((re.findall("\d+", RtempRangeThr))[1])
	RtempMinFou = int((re.findall("\d+", RtempRangeFou))[0])
	RtempMaxFou = int((re.findall("\d+", RtempRangeFou))[1])
	# Find the averages of these temps for the setup
	Rtemp = ((RtempMinOne + RtempMaxOne) + (RtempMinTwo + RtempMaxTwo) + (RtempMinThr + RtempMaxThr) + (RtempMinFou + RtempMaxFou)) / 8

	
	# Using the race strategy page requested earlier, scrape the qualifying weather data
	QOneTemp = str(tree.xpath("normalize-space(//img[contains(@name, 'WeatherQ')]/../text()[contains(., 'Temp')])"))
	QOneTemp = int((re.findall("\d+", QOneTemp))[0])
	QTwoTemp = str(tree.xpath("normalize-space(//img[contains(@name, 'WeatherR')]/../text()[contains(., 'Temp')])"))
	QTwoTemp = int((re.findall("\d+", QTwoTemp))[0])

	if(temp == "Race"):
		temp = Rtemp
	elif(temp == "Q1"):
		temp = QOneTemp
	elif(temp == "Q2"):
		temp = QTwoTemp
	
	# Request the car information page and scrape the car character and part level and wear data
	carResult = session.get(car_url, headers=dict(referer=car_url))
	tree = html.fromstring(carResult.content)
	carPow = int(tree.xpath("normalize-space(//table[contains(@data-step, '1')]/tr[3]/td[1]/text())"))
	carHan = int(tree.xpath("normalize-space(//table[contains(@data-step, '1')]/tr[3]/td[2]/text())"))
	carAcc = int(tree.xpath("normalize-space(//table[contains(@data-step, '1')]/tr[3]/td[3]/text())"))
	# Level
	carLevelCha = int(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[2]/text())"))
	carLevelEng = int(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[2]/text())"))
	carLevelFWi = int(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[2]/text())"))
	carLevelRWi = int(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[2]/text())"))
	carLevelUnd = int(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[2]/text())"))
	carLevelSid = int(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[2]/text())"))
	carLevelCol = int(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[2]/text())"))
	carLevelGea = int(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[2]/text())"))
	carLevelBra = int(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[2]/text())"))
	carLevelSus = int(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[2]/text())"))
	carLevelEle = int(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[2]/text())"))
	# And wear
	carWearCha = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/text())"))
	if(carWearCha == ""):
		carWearCha = str(tree.xpath("normalize-space(//b[contains(text(), 'Chassis')]/../../td[4]/font/text())"));
	carWearCha = int((re.findall("\d+", carWearCha))[0])
	carWearEng = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/text())"))
	if(carWearEng == ""):
		carWearEng = str(tree.xpath("normalize-space(//b[contains(text(), 'Engine')]/../../td[4]/font/text())"));
	carWearEng = int((re.findall("\d+", carWearEng))[0])
	carWearFWi = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/text())"))
	if(carWearFWi == ""):
		carWearFWi = str(tree.xpath("normalize-space(//b[contains(text(), 'Front wing')]/../../td[4]/font/text())"));
	carWearFWi = int((re.findall("\d+", carWearFWi))[0])
	carWearRWi = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/text())"))
	if(carWearRWi == ""):
		carWearRWi = str(tree.xpath("normalize-space(//b[contains(text(), 'Rear wing')]/../../td[4]/font/text())"));
	carWearRWi = int((re.findall("\d+", carWearRWi))[0])
	carWearUnd = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/text())"))
	if(carWearUnd == ""):
		carWearUnd = str(tree.xpath("normalize-space(//b[contains(text(), 'Underbody')]/../../td[4]/font/text())"));
	carWearUnd = int((re.findall("\d+", carWearUnd))[0])
	carWearSid = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/text())"))
	if(carWearSid == ""):
		carWearSid = str(tree.xpath("normalize-space(//b[contains(text(), 'Sidepods')]/../../td[4]/font/text())"));
	carWearSid = int((re.findall("\d+", carWearSid))[0])
	carWearCol = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/text())"))
	if(carWearCol == ""):
		carWearCol = str(tree.xpath("normalize-space(//b[contains(text(), 'Cooling')]/../../td[4]/font/text())"));
	carWearCol = int((re.findall("\d+", carWearCol))[0])
	carWearGea = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/text())"))
	if(carWearGea == ""):
		carWearGea = str(tree.xpath("normalize-space(//b[contains(text(), 'Gearbox')]/../../td[4]/font/text())"));
	carWearGea = int((re.findall("\d+", carWearGea))[0])
	carWearBra = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/text())"))
	if(carWearBra == ""):
		carWearBra = str(tree.xpath("normalize-space(//b[contains(text(), 'Brakes')]/../../td[4]/font/text())"));
	carWearBra = int((re.findall("\d+", carWearBra))[0])
	carWearSus = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/text())"))
	if(carWearSus == ""):
		carWearSus = str(tree.xpath("normalize-space(//b[contains(text(), 'Suspension')]/../../td[4]/font/text())"));
	carWearSus = int((re.findall("\d+", carWearSus))[0])
	carWearEle = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/text())"))
	if(carWearEle == ""):
		carWearEle = str(tree.xpath("normalize-space(//b[contains(text(), 'Electronics')]/../../td[4]/font/text())"));
	carWearEle = int((re.findall("\d+", carWearEle))[0])
	
	
	# Setup calculations
	# Begin by storig the track base values
	# TODO: Automate this data collection (possibly from GPRO, probably from my own online database)
	with open('trackData.csv', 'rt', newline='') as f:
		r = csv.reader(f)
		trackData = collections.OrderedDict((row[0], row[1:]) for row in r);
	baseWin = float(trackData[trackNam][0]) * 2
	baseEng = float(trackData[trackNam][1])
	baseBra = float(trackData[trackNam][2])
	baseGea = float(trackData[trackNam][3])
	baseSus = float(trackData[trackNam][4])
	baseWSp = float(trackData[trackNam][5])

		# Create the setup dictionary
	baseOffsets = {
		"wingWeatherDry": 6,
		"wingWeatherWet": 1,
		"wingWeatherOffset": 263,
		"engineWeatherDry": -3,
		"engineWeatherWet": 0.7,
		"engineWeatherOffset": -190,
		"brakesWeatherDry": 6,
		"brakesWeatherWet": 3.988375441,
		"brakesWeatherOffset": 105.5325924,
		"gearsWeatherDry": -4,
		"gearsWeatherWet": -8.0019964182,
		"gearsWeatherOffset": -4.742711704,
		"suspensionWeatherDry": -6,
		"suspensionWeatherWet": -1,
		"suspensionWeatherOffset": -257, 
		"wingDriverMultiplier": -0.001349079032746,
		"engineDriverMultiplier": 0.001655723,
		"engineDriverOffset": 0.0469416263186552
	}
	
	levelOffsets = [
		[-19.74, 0, 30.03, 30.03, -15.07, 0, 0, 0, 0, 0, 0],
		[0, 16.04, 0, 0, 0, 0, 4.9, 0, 0, 0, 3.34],
		[6.04, 0, 0, 0, 0, 0, 0, 0, -29.14, 0, 6.11],
		[0, 0, 0, 0, 0, 0, 0, -41, 0, 0, 9],
		[-15.27, 0, 0, 0, -10.72, 6.03, 0, 0, 0, 31, 0]
	]
	
	wearOffsets = [
		[0.47, 0, -0.59, -0.59, 0.32, 0, 0, 0, 0, 0, 0],
		[0, -0.51, 0, 0, 0, 0, -0.09, 0, 0, 0, -0.04],
		[-0.14, 0, 0, 0, 0, 0, 0, 0, 0.71, 0, -0.09],
		[0, 0, 0, 0, 0, 0, 0, 1.09, 0, 0, -0.14],
		[0.34, 0, 0, 0, 0.23, -0.12, 0, 0, 0, -0.70, 0]
	]
	
	driverOffsets = [
		[0, 0, 0, 0, 0],
		[0, 0, 0.3, 0, 0],
		[0, -0.5, 0, 0, 0],
		[0.5, 0, 0, 0, 0],
		[0, 0, 0, 0.75, 2]
	]

	# And now calculate the actual setup for the race
	# Wings
	temp = int(temp)
	if(weather != "WET"):
		setupWeather = baseOffsets["wingWeatherDry"] * temp * 2;
	else:
		setupWeather = ((baseOffsets["wingWeatherWet"] * temp) + baseOffsets["wingWeatherOffset"]) * 2;
	setupDriver = driverTal * (baseWin + setupWeather) * baseOffsets["wingDriverMultiplier"]
	setupCarLevel = (levelOffsets[0][0] * carLevelCha) + (levelOffsets[0][2] * carLevelFWi) + (levelOffsets[0][3] * carLevelRWi) + (levelOffsets[0][4] * carLevelUnd)
	setupCarWear = ((wearOffsets[0][0] * carWearCha) + (wearOffsets[0][2] * carWearFWi) + (wearOffsets[0][3] * carWearRWi) + (wearOffsets[0][4] * carWearUnd))
	setupWings = (baseWin + setupWeather + setupDriver + setupCarLevel + setupCarWear) / 2

	# Wing Split
	setupWingSplit = baseWSp + (driverTal * -0.246534498671854) + (3.69107049712848 * (carLevelFWi + carLevelRWi) / 2) + (setupWings * -0.189968386659174) + (temp * 0.376337780506523)
	setupFWi = setupWings + setupWingSplit
	setupRWi = setupWings - setupWingSplit

	# Engine
	if(weather != "WET"):
		setupWeather = baseOffsets["engineWeatherDry"] * temp;
	else:
		setupWeather = ((baseOffsets["engineWeatherWet"] * temp) + baseOffsets["engineWeatherOffset"]) * 2;
	setupDriver = (driverOffsets[1][2] * driverAgg) + (driverExp * (((baseEng + setupWeather) * baseOffsets["engineDriverMultiplier"]) + baseOffsets["engineDriverOffset"]))
	setupCarLevel = ((levelOffsets[1][1] * carLevelEng) + (levelOffsets[1][6] * carLevelCol) + (levelOffsets[1][10] * carLevelEle))
	setupCarWear = ((wearOffsets[1][1] * carWearEng) + (wearOffsets[1][6] * carWearCol) + (wearOffsets[1][10] * carWearEle))
	setupEng = (baseEng + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Brakes
	if(weather != "WET"):
		setupWeather = baseOffsets["brakesWeatherDry"] * temp;
	else:
		setupWeather = ((baseOffsets["brakesWeatherWet"] * temp) + baseOffsets["brakesWeatherOffset"]) * 2;
	setupDriver = (driverOffsets[2][1] * driverTal)
	setupCarLevel = ((levelOffsets[2][0] * carLevelCha) + (levelOffsets[2][8] * carLevelBra) + (levelOffsets[2][10] * carLevelEle))
	setupCarWear = ((wearOffsets[2][0] * carWearCha) + (wearOffsets[2][8] * carWearBra) + (wearOffsets[2][10] * carWearEle))
	setupBra = (baseBra + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Gears
	if(weather != "WET"):
		setupWeather = baseOffsets["gearsWeatherDry"] * temp;
	else:
		setupWeather = ((baseOffsets["gearsWeatherWet"] * temp) + baseOffsets["gearsWeatherOffset"]) * 2;
	setupDriver = (driverOffsets[3][0] * driverCon)
	setupCarLevel = ((levelOffsets[3][7] * carLevelGea) + (levelOffsets[3][10] * carLevelEle))
	setupCarWear = ((wearOffsets[3][7] * carWearGea) + (wearOffsets[3][10] * carWearEle))
	setupGea = (baseGea + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	# Suspension
	if(weather != "WET"):
		setupWeather = baseOffsets["suspensionWeatherDry"] * temp;
	else:
		setupWeather = ((baseOffsets["suspensionWeatherWet"] * temp) + baseOffsets["suspensionWeatherOffset"]) * 2;
	setupDriver = (driverOffsets[4][3] * driverExp) + (driverOffsets[4][4] * driverWei)
	setupCarLevel = ((levelOffsets[4][0] * carLevelCha) + (levelOffsets[4][4] * carLevelUnd) + (levelOffsets[4][5] * carLevelSid) + (levelOffsets[4][9] * carLevelSus))
	setupCarWear = ((wearOffsets[4][0] * carWearCha) + (wearOffsets[4][4] * carWearUnd) + (wearOffsets[4][5] * carWearSid) + (wearOffsets[4][9] * carWearSus))
	setupSus = (baseSus + setupWeather + setupDriver + setupCarLevel + setupCarWear)

	setup = [int(setupFWi), int(setupRWi), int(setupEng), int(setupBra), int(setupGea), int(setupSus)]

	tyreBrand = {"Pipirelli": 1, "Avonn": 8, "Yokomama": 3, "Dunnolop": 4, "Contimental": 8, "Badyear": 7}
	trackWearLevel = {"Very low": 0, "Low": 1, "Medium": 2, "High": 3, "Very high": 4}

	wearFactors = [0.998163750229071, 0.997064844817654, 0.996380346554349, 0.995862526048112, 0.996087854384523]

	for i in range(5):
		stops[i].set(str(stopCalc(trackDst, trackWearLevel[trackTyr], Rtemp, tyreBrand[tyreSupplier], i, carLevelSus, driverAgg, driverExp, driverWei, clearTrackRisk, float(trackData[trackNam][9]), wear, wearFactors[i])))

	return setup

# Pit Stop Calc
# trackDst = Track Distance
# tracWearLevel = Very Low, Low, Medium, High, Very High, and it's relating factor, 0, 1, 2, 3, 4 respectively
# Rtemp = Race Temperature
# tyreBrand = Tyre Brand Factor, 1 for Pipirello, 8 for Avonn, etc.
# tyreType = Tyre Compound Factor, 0.998163750229071 for Extra Soft (look at wearFactors)
# carLevelSus = Suspension Level equipped to car
# driverAgg = Driver Aggressiveness
# driverExp = Driver Experience
# driverWeight = Driver Weight
# clearTrackRisk = Clear Track Risk used, as a percentage
# trackBaseWear = Track Base Wear from trackData.csv
# wearLimit = The manager chosen limit for tyre wear before pitting, so at 10%, we assume the stint will end when the tyres hit 10% wear
def stopCalc(trackDst, trackWearLevel, Rtemp, tyreBrand, tyreType, carLevelSus, driverAgg, driverExp, driverWeight, clearTrackRisk, trackBaseWear, wearLimit, tyreWearFactor):
	baseWear = 129.776458172062
	productFactors = (0.896416176238624 ** trackWearLevel) * (0.988463622 ** Rtemp) * (1.048876356 ** tyreBrand) * (1.355293715 ** tyreType) * (1.009339294 ** carLevelSus) * (0.999670155 ** driverAgg) * (1.00022936 ** driverExp) * (0.999858329 ** driverWeight) * (tyreWearFactor ** (clearTrackRisk / 100))
	stops = math.ceil((trackDst) / ((productFactors * (tyreWearFactor ** clearTrackRisk) * baseWear * trackBaseWear) * ((100 - wearLimit) / 100))) - 1
	return stops


# Warning window
def warning(*args):
	frontWing.set("Login")
	rearWing.set("incorrect")

def exit():
	warning.Toplevel.destroy()

# Precheck to handle errors nicely
def calculate(*args):
	try:
		username = str(inputUsername.get())
		password = str(inputPassword.get())
		weather = str(inputWeather.get())
		session = str(inputSession.get())
		try:
			wear = float(re.findall('\d+.\d+', inputWear.get())[0])
		except:
			try:
				wear = float(re.findall('\d+', inputWear.get())[0])
			except:
				wear = 0.0
		try:
			clearTrackRisk = int(re.findall('\d+', inputCTR.get())[0])
		except:
			clearTrackRisk = 0

		setup = collection(username, password, weather, session, wear, clearTrackRisk)

		if(setup[0] == 0):
			warningLabel.set("Incorect Login Details")
		elif(setup[0] == 1):
			warningLabel.set("VIPER Family Team Only")
		else:
			warningLabel.set("")
			frontWing.set(str(setup[0]))
			rearWing.set(str(setup[1]))
			engine.set(str(setup[2]))
			brakes.set(str(setup[3]))
			gear.set(str(setup[4]))
			suspension.set(str(setup[5]))
		
	except ValueError:
		pass


# Create the window
root = Tk()
root.title("GAPP")


# and build the frame
frameSetup = ttk.LabelFrame(root, padding = "3 3 12 12")
frameSetup.grid(column = 0, row = 0, sticky = (N, W, E, S))
frameStrategy = ttk.LabelFrame(root, padding = "3 3 12 12")
frameStrategy.grid(column = 1, row = 0, sticky = (N, W, E))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)
frameSetup.columnconfigure(0, weight = 1)
frameSetup.rowconfigure(0, weight = 1)
frameStrategy.columnconfigure(0, weight = 1)
frameStrategy.rowconfigure(0, weight = 1)


# Declare our userful variables
inputUsername = StringVar()
inputPassword = StringVar()
inputWeather = StringVar()
inputWeather.set("Dry")
inputTemp = IntVar()
inputSession = StringVar()
inputSession.set("Race")
warningLabel = StringVar()

inputWear = StringVar()
inputWear.set("20")
inputCTR = StringVar()
inputCTR.set("0")

frontWing = StringVar()
rearWing = StringVar()
engine = StringVar()
brakes = StringVar()
gear = StringVar()
suspension = StringVar()

frontWing.set("0")
rearWing.set("0")
engine.set("0")
brakes.set("0")
gear.set("0")
suspension.set("0")


# INPUT
# Build the entry boxes
entryUsername = ttk.Entry(frameSetup, width = 30, textvariable = inputUsername)
entryUsername.grid(column = 2, row = 1, sticky = (W, E))

entryPassword = ttk.Entry(frameSetup, width = 30, show = "*", textvariable = inputPassword)
entryPassword.grid(column = 2, row = 2, sticky = (W, E))

radioQ1 = ttk.Radiobutton(frameSetup, text = "Q1", variable = inputSession, value = "Q1").grid(column = 2, row = 3, sticky = (W, E))
radioQ2 = ttk.Radiobutton(frameSetup, text = "Q2", variable = inputSession, value = "Q2").grid(column = 2, row = 4, sticky = (W, E))
radioRace = ttk.Radiobutton(frameSetup, text = "Race", variable = inputSession, value = "Race").grid(column = 2, row = 5, sticky = (W, E))

radioDry = ttk.Radiobutton(frameSetup, text = "Dry", variable = inputWeather, value = "Dry")
radioDry.grid(column = 2, row = 6, sticky = (W, E))
radioWet = ttk.Radiobutton(frameSetup, text = "Wet", variable = inputWeather, value = "Wet")
radioWet.grid(column = 2, row = 7, sticky = (W, E))


# Add labels to the entry boxes
ttk.Label(frameSetup, text = "Username: ").grid(column = 1, row = 1, sticky = (W, E))
ttk.Label(frameSetup, text = "Password: ").grid(column = 1, row = 2, sticky = (W, E))
ttk.Label(frameSetup, text = "Session: ").grid(column = 1, row = 3, sticky = (W, E))
ttk.Label(frameSetup, text = "Weather: ").grid(column = 1, row = 6, sticky = (W, E))


# Add a button to calculate the setup
ttk.Button(frameSetup, text = "Calculate", command = calculate).grid(column = 1, row = 8)
ttk.Label(frameSetup, textvariable = warningLabel).grid(column = 2, row = 8)



# OUTPUT
ttk.Label(frameSetup, text = "Front Wing: ").grid(column = 1, row = 9, sticky = (W, E))
ttk.Label(frameSetup, text = "Rear Wing: ").grid(column = 1, row = 10, sticky = (W, E))
ttk.Label(frameSetup, text = "Engine: ").grid(column = 1, row = 11, sticky = (W, E))
ttk.Label(frameSetup, text = "Brakes: ").grid(column = 1, row = 12, sticky = (W, E))
ttk.Label(frameSetup, text = "Gear: ").grid(column = 1, row = 13, sticky = (W, E))
ttk.Label(frameSetup, text = "Suspension: ").grid(column = 1, row = 14, sticky = (W, E))

ttk.Label(frameSetup, textvariable = frontWing).grid(column = 2, row = 9)
ttk.Label(frameSetup, textvariable = rearWing).grid(column = 2, row = 10)
ttk.Label(frameSetup, textvariable = engine).grid(column = 2, row = 11)
ttk.Label(frameSetup, textvariable = brakes).grid(column = 2, row = 12)
ttk.Label(frameSetup, textvariable = gear).grid(column = 2, row = 13)
ttk.Label(frameSetup, textvariable = suspension).grid(column = 2, row = 14)


# Strategy
ttk.Label(frameStrategy, text = "Wear:", padding = "5 10").grid(column = 1, row = 1, sticky = (W, E))
entryWear = ttk.Entry(frameStrategy, width = 10, textvariable = inputWear).grid(column = 2, row = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "CTR:", padding = "5 10").grid(column = 3, row = 1, sticky = (W, E))
entryCTR = ttk.Entry(frameStrategy, width = 10, textvariable = inputCTR).grid(column = 4, row = 1, sticky = (W, E))

ttk.Label(frameStrategy, text = "Tyre", padding = "5 10").grid(column = 1, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Stops", padding = "5 10").grid(column = 2, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Fuel Load", padding = "5 10").grid(column = 3, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Pit Time", padding = "5 10").grid(column = 4, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Compound Loss", padding = "5 10").grid(column = 5, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Fuel Loss", padding = "5 10").grid(column = 6, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Pit Total", padding = "5 10").grid(column = 7, row = 2, sticky = (W, E))
ttk.Label(frameStrategy, text = "Total", padding = "5 10").grid(column = 8, row = 2, sticky = (W, E))

ttk.Label(frameStrategy, text = "Extra Soft").grid(column = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "Soft").grid(column = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "Medium").grid(column = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "Hard").grid(column = 1, sticky = (W, E))
ttk.Label(frameStrategy, text = "Rain").grid(column = 1, sticky = (W, E))

# Strategy grid variables
extraStops = StringVar()
softStops = StringVar()
mediumStops = StringVar()
hardStops = StringVar()
rainStops = StringVar()
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
fuels = [extraFuel, softFuel, mediumFuel, hardFuel, rainFuel]
pitTimes = [extraPitTime, softPitTime, mediumPitTime, hardPitTime, rainPitTime]
TCDs = [extraTCD, softTCD, mediumTCD, hardTCD, rainTCD]
FLDs = [extraFLD, softFLD, mediumFLD, hardFLD, rainFLD]
totals = [extraTotal, softTotal, mediumTotal, hardTotal, rainTotal]

grid = [stops, fuels, pitTimes, TCDs, FLDs, totals]

for stop in stops:
	stop.set("0")
for fuel in fuels:
	fuel.set("0")
for pitTime in pitTimes:
	pitTime.set("0")
for TCD in TCDs:
	TCD.set("0")
for FLD in FLDs:
	FLD.set("0")
for total in totals:
	total.set("0")

x = 2
for values in grid:
	y = 3
	for value in values:
		ttk.Label(frameStrategy, textvariable = value).grid(column = x, row = y, sticky = (W))
		y = y + 1
	x = x + 1

# Automatically organize the window
for child in frameSetup.winfo_children(): child.grid_configure(padx=5, pady=5)
for child in frameStrategy.winfo_children(): child.grid_configure(padx=5, pady=5)


# Set some QOL things, like auto focus for text entry and how to handle an "Enter" press
entryUsername.focus()
root.bind('<Return>', calculate)
root.resizable(False, False)


# Create the window
root.mainloop()