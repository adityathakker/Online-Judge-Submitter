from CodeChef import CodeChef
import mechanize

browser = mechanize.Browser()
browser.set_handle_robots(False)

codechef = CodeChef(browser)
codechef.submit()