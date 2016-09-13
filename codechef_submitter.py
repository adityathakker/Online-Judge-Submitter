import mechanize
import os.path
import getpass
import pickle
from bs4 import BeautifulSoup
import os

CREDENTIALS_FILE_NAME = "credentials"
OJ_NAME = "CodeChef"

def get_credentials():
	username = raw_input("Enter Your " + OJ_NAME + " Username: ")
	password = getpass.getpass("Enter Your " + OJ_NAME + " Password: ")
	credentials_file = open(CREDENTIALS_FILE_NAME, "wb")
	credentials_dict = {"username": username, "password": password}
	pickle.dump(credentials_dict, credentials_file)
	credentials_file.close()

#purely for debugging
def save_file(name, content):
	file_obj = open(name, "wb")
	file_obj.write(content)
	file_obj.close()

def login(browser):
	print("Logging in to CodeChef....Wait A Moment")

	# check if credentials file exists? If it does not,
	# then take username and password
	if not os.path.isfile(CREDENTIALS_FILE_NAME):
		get_credentials()

	#getting credentials
	credentials_dict = pickle.load(open(CREDENTIALS_FILE_NAME, "r"))

	#opening brower and enter input to form
	browser.open("https://www.codechef.com/")
	browser.select_form(nr = 0)
	browser.form['name'] = credentials_dict["username"]
	browser.form['pass'] = credentials_dict["password"]
	browser.submit()

	#create soup object to check if login was success or not
	soup = BeautifulSoup(browser.response().read(), "lxml")
	error_div = soup.findAll("input", {"class": "error"})
	if len(error_div) > 0: 
		print("Entered Username/Password is Wrong\nPlease Enter Credentials Again.")
		get_credentials()
		login(browser)
	else:
		print("Login Was Successful")
		return

def get_languages():
	languages = {
	"C++(gcc-4.9.2)": 1,
	"Java(javac 8)": 10,
	"Python(Pypy)": 99
	}
	return languages

def get_language_input():
	languages = get_languages()
	print("List Of Languages: ")
	for each_lang in list(languages.keys()):
		print("\t" + each_lang + ": " + str(languages[each_lang]))

	language_value = raw_input("Enter Language Value to Select: ")
	try:
		while int(language_value) not in languages.values():
			language_value = raw_input("Enter Language Value to Select: ")
	except ValueError:
		print("Please Enter an Integer Value Corresponding to Language")
		get_language_input()

	return language_value

def submit_solution(browser):
	#get problem code from user
	problem_code = raw_input("Enter Problems Unique Code: ")
	solution_path = raw_input("Enter Solution Files Path: ")
	solution_path = os.path.abspath(solution_path)

	language_value = get_language_input()

	print("\nSubmitting Solution to CodeChef...Wait a Sec")

	browser.open("https://www.codechef.com/submit/" + problem_code)
	save_file("solution.html", browser.response().read())
	browser.select_form(nr=0)
	browser.form.add_file(open(solution_path), 'text/plain', os.path.basename(solution_path), name='files[sourcefile]')
	form = browser.form
	form["language"] = [language_value]
	browser.submit()



browser = mechanize.Browser()
browser.set_handle_robots(False)

login(browser)
submit_solution(browser)

