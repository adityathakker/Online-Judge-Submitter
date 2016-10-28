import cookielib
import urllib2

import time
from termcolor import colored
import mechanize
import os.path
import getpass
import pickle
from bs4 import BeautifulSoup
import os


# Todo: Comment about last changes in login function

class CodeChef:
    OJ_NAME = "CodeChef"
    CREDENTIALS_FILE_NAME = OJ_NAME + "_credentials"
    HISTORY_FILE_NAME = OJ_NAME + "_history"
    COOKIES_FILE_NAME = OJ_NAME + "_cookies"
    browser = mechanize.Browser()

    def __init__(self, browser):
        self.browser = browser

    # getting username and password from the file saved
    def get_credentials(self):
        username = raw_input(colored("Enter Your " + self.OJ_NAME + " Username: ", "blue"))
        password = getpass.getpass(colored("Enter Your " + self.OJ_NAME + " Password: ", "blue"))
        credentials_file = open(self.CREDENTIALS_FILE_NAME, "wb")
        credentials_dict = {"username": username, "password": password}
        pickle.dump(credentials_dict, credentials_file)
        credentials_file.close()

    # purely for debugging
    def save_file(self, name, content):
        file_obj = open(name, "wb")
        file_obj.write(content)
        file_obj.close()

    def __login(self):
        print("Logging in to " + self.OJ_NAME + "....Wait A Moment")

        cookies_jar = cookielib.LWPCookieJar()
        if os.path.isfile(self.COOKIES_FILE_NAME):
            cookies_jar.load(self.COOKIES_FILE_NAME, ignore_discard=False, ignore_expires=False)
            self.browser.set_cookiejar(cookies_jar)

        try:
            # opening browser and enter input to form
            self.browser.open("https://www.codechef.com/")
        except (mechanize.HTTPError, urllib2.HTTPError) as e:
            print(colored("Something Went Wrong", "red"))
            print(colored("Trying Again...", "red"))
            self.__login()
            return

        # creating soup object to check if already logged-in or not
        soup = BeautifulSoup(self.browser.response().read(), "lxml")
        login_li = soup.findAll("li", {"class": "loggedin-user"})
        if len(login_li) > 0:
            # Already Logged In
            print(colored("You Are Already Logged In", "green"))

            # for debug
            # self.save_file("login_already.html", self.browser.response().read())

            if "limit" in str(soup.title).lower():
                print(colored("Session Limit Exceeded...", "yellow"))
                ans = raw_input(colored("Do you want to terminate other sessions [y/n]: ", "yellow"))

                if ans == "y":
                    while "limit" in str(soup.title).lower():
                        try:
                            self.browser.select_form(nr=0)
                            self.browser.form.set_all_readonly(False)

                            radio_value = str()
                            for control in self.browser.form.controls:
                                if control.type == "radio" and "current" not in str(
                                        [label.text for label in control.items[0].get_labels()]):
                                    radio_value = control.items[0].name
                                    break

                            self.browser.form.set_value([radio_value], name='sid')
                            self.browser.submit()
                            soup = BeautifulSoup(self.browser.response().read(), "lxml")
                        except (mechanize.HTTPError, urllib2.HTTPError) as e:
                            print(colored("Something Went Wrong", "red"))
                            print(colored("Trying Again...", "red"))
                            pass

                else:
                    exit()

        else:
            # Not Logged In

            # check if credentials file exists? If it does not,
            # then take username and password
            if not os.path.isfile(self.CREDENTIALS_FILE_NAME):
                self.get_credentials()

            # getting credentials
            credentials_dict = pickle.load(open(self.CREDENTIALS_FILE_NAME, "r"))

            try:
                self.browser.set_cookiejar(cookies_jar)
                self.browser.select_form(nr=0)
                self.browser.form['name'] = credentials_dict["username"]
                self.browser.form['pass'] = credentials_dict["password"]
                self.browser.submit()
            except (mechanize.HTTPError, urllib2.HTTPError) as e:
                print(colored("Something Went Wrong", "red"))
                print(colored("Trying Again...", "red"))
                self.__login()
                return

            # create soup object to check if login was success or not
            soup = BeautifulSoup(self.browser.response().read(), "lxml")
            error_div = soup.findAll("input", {"class": "error"})
            if len(error_div) > 0:
                print(colored("Entered Username/Password is Wrong\nPlease Enter Credentials Again.", "yellow"))

                # for debug
                # self.save_file("login_fail.html", self.browser.response().read())

                # repeat
                self.get_credentials()
                self.__login()
            else:
                cookies_jar.save(self.COOKIES_FILE_NAME, ignore_discard=False, ignore_expires=False)

                if "limit" in str(soup.title).lower():
                    print(colored("Session Limit Exceeded...", "yellow"))
                    print(colored("Do you want to terminate other sessions [y/n]: ", "yellow"))
                    ans = raw_input()

                    if ans == "y":
                        while "limit" in str(soup.title).lower():
                            try:
                                self.browser.select_form(nr=0)
                                self.browser.form.set_all_readonly(False)

                                radio_value = str()
                                for control in self.browser.form.controls:
                                    if control.type == "radio" and "current" not in str(
                                            [label.text for label in control.items[0].get_labels()]):
                                        radio_value = control.items[0].name
                                        break

                                self.browser.form.set_value([radio_value], name='sid')
                                self.browser.submit()
                                soup = BeautifulSoup(self.browser.response().read(), "lxml")
                            except (mechanize.HTTPError, urllib2.HTTPError) as e:
                                print(colored("Something Went Wrong", "red"))
                                print(colored("Trying Again...", "red"))
                                pass

                    else:
                        exit()

                # for debug
                # self.save_file("login_success.html", self.browser.response().read())

                print(colored("Login Was Successful", "green"))
                return

    def get_languages(self):
        languages = {
            "C++(gcc-4.9.2)": 1,
            "Java(javac 8)": 10,
            "Python(Pypy)": 99
        }
        return languages

    def get_language_input(self):
        languages = self.get_languages()
        print("List Of Languages: ")
        for each_lang in list(languages.keys()):
            print("\t" + each_lang + ": " + str(languages[each_lang]))

        language_value = raw_input(colored("Enter Language Value to Select: ", "blue"))
        try:
            while int(language_value) not in languages.values():
                language_value = raw_input(colored("Enter Language Value to Select: ", "blue"))
        except ValueError:
            print(colored("Please Enter an Integer Value Corresponding to Language", "red"))
            return self.get_language_input()

        return language_value

    def __submit_solution(self, problem_code="", solution_path="", language_value=-1):
        try:
            if not problem_code.strip or not solution_path.strip() or language_value == -1:
                history_file = open(self.HISTORY_FILE_NAME, "r")
                history_dict = pickle.load(history_file)
                if not history_dict["ALL_WENT_WELL"]:
                    resubmit = raw_input(colored("Do you want to resubmit? [Y/N]: ", "blue"))
                    if resubmit == "Y":
                        self.__submit_solution(history_dict["PROBLEM_CODE"], history_dict["SOLUTION_PATH"], history_dict["LANGUAGE_VALUE"])
                        return
        except IOError, e:
            pass

        if not problem_code.strip():
            # get problem code from user
            problem_code = raw_input(colored("Enter Problems Code: ", "blue"))

        if not solution_path.strip():
            solution_path = raw_input(colored("Enter Solution Files Path (with extension): ", "blue"))
            solution_path = os.path.abspath(solution_path)
            if not os.path.isfile(solution_path):
                print(colored("Invalid File Path! Enter Again...", "red"))
                self.__submit_solution(problem_code=problem_code)
                return

        if language_value == -1:
            language_value = self.get_language_input()

        # Saving the current submittion in history
        history_file = open(self.HISTORY_FILE_NAME, "wb")
        history_file.seek(0)
        history_file.truncate()
        history_dict = dict()
        history_dict["PROBLEM_CODE"] = problem_code
        history_dict["SOLUTION_PATH"] = solution_path
        history_dict["LANGUAGE_VALUE"] = language_value
        pickle.dump(history_dict, history_file);
        history_file.close()


        print(colored("\nSubmitting Solution to CodeChef...Wait a Sec", "green"))

        try:
            print(colored("Uploading Solution...", "yellow"))
            self.browser.open("https://www.codechef.com/submit/" + problem_code)

            soup = BeautifulSoup(self.browser.response().read(), "lxml")
            if "error" in str(soup.title).lower():
                p_error = soup.findAll("p", {"class": "err-message"})
                if len(p_error) > 0:
                    print(colored("Error Occurred! " + str(p_error[0].text), "red"))
                    print(colored("Trying Again!", "red"))
                    self.__submit_solution()
                    return

            # debug
            # self.save_file("solution.html", self.browser.response().read())

            self.browser.select_form(nr=0)
            self.browser.form.add_file(open(solution_path), 'text/plain', os.path.basename(solution_path),
                                       name='files[sourcefile]')

            self.browser.form["language"] = [language_value]
            self.browser.submit()

            # debug
            # self.save_file("after_submit.html", self.browser.response().read())

            print(colored("Waiting for the Result...", "yellow"))

            # getting credentials
            credentials_dict = pickle.load(open(self.CREDENTIALS_FILE_NAME, "r"))

            # codechef sometimes takes a lot of time to give the result.
            # so added a delay of 15 seconds to get the correct result
            time.sleep(15)

            found = False

            while not found:
                try:
                    # check if the solution was success
                    self.browser.open("https://www.codechef.com/status/" + problem_code)
                except (mechanize.HTTPError, urllib2.HTTPError) as e:
                    print(colored("Something Went Wrong", "red"))
                    print(colored("Trying Again...", "red"))
                    continue

                # debug
                # self.save_file("status_page.html", self.browser.response().read())

                soup = BeautifulSoup(self.browser.response().read(), "lxml")
                table = soup.find("table", {"class": "dataTable"})
                tbody = table.find("tbody")
                all_tr = tbody.find_all("tr")
                all_tr = all_tr[:3]

                for tr in all_tr:
                    all_td = tr.find_all("td")
                    if str(all_td[2].text).strip() == credentials_dict["username"]:
                        found = True
                        print(colored("\n++++++++++++++Result++++++++++++++","white"))
                        print(colored("\tID: ", "blue") + colored(str(all_td[0].text), "white"))
                        print(colored("\tDate/Time: ", "blue") + colored(str(all_td[1].text), "white"))
                        print(colored("\tUser: ", "blue") + colored(str(all_td[2].text), "white"))

                        all_went_well = True

                        span = all_td[3].find("span")
                        img = span.find("img")
                        if "alert" in str(img["src"]):
                            all_went_well = False
                            print(colored("\tResult: ", "blue") + colored("Compilation Error", "yellow"))
                        elif "clock" in str(img["src"]):
                            all_went_well = False
                            print(colored("\tResult: ", "blue") + colored("Timeout Error", "yellow"))
                        elif "tick" in str(img["src"]):
                            print(colored("\tResult: ", "blue") + colored("Accepted", "green"))
                        elif "runtime" in str(img["src"]):
                            all_went_well = False
                            print(colored("\tResult: ", "blue") + colored("Runtime Error", "red"))
                        elif "cross" in str(img["src"]):
                            all_went_well = False
                            print(colored("\tResult: ", "blue") + colored("Wrong Answer", "red"))

                        print(colored("\tTime: ", "blue") + colored(str(all_td[4].text), "white"))
                        print(colored("\tMemory: ", "blue") + colored(str(all_td[5].text), "white"))
                        print(colored("\tLanguage: ", "blue") + colored(str(all_td[6].text), "white"))
                        

                        history_file = open(self.HISTORY_FILE_NAME, "r+")
                        history_dict = pickle.load(history_file)
                        history_dict["ALL_WENT_WELL"] = all_went_well
                        history_file.seek(0)
                        history_file.truncate()
                        pickle.dump(history_dict, history_file)
                        history_file.close()
                        
                        break

        except (mechanize.HTTPError, urllib2.HTTPError) as e:
            print(colored("Something Went Wrong", "red"))
            print(colored("Trying Again...", "red"))
            self.__submit_solution(problem_code=problem_code, solution_path=solution_path, language_value=language_value)
            return

    def submit(self):
        try:
            self.__login()
            self.__submit_solution()
        except (KeyboardInterrupt, SystemExit):
            print(colored("Exiting...", "yellow"))
