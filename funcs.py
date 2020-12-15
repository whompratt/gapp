import re

import mechanize


# checkData
# This function will check to see if the user has selected "save credentials"
# If they have, it will store the credentials given in the data.dat file, otherwise it will erase that file
def checkData(filename, rememberCredentials, username, password):
	if (rememberCredentials == 1):
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
	# Best read the mechanize documentation for info on how mechanize works.
	# Create a new broser reference
	browser = mechanize.Browser()
	# Open the login page and select the login section
	browser.open("https://gpro.net/gb/Login.asp")
	browser.select_form(id="Form1")
	# Input the username and password
	browser.form["textLogin"] = username
	browser.form["textPassword"] = password
	# Submit the completed page
	browser.submit()
	response = list(browser.links(url_regex=re.compile("DriverProfile")))
	browser.close()

	# At this point, if the login was successful, there should be 1 links with "DriverProfile" in.
	return True if (len(response) is 1) else False
