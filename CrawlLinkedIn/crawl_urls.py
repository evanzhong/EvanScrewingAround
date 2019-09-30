# Setting the encoding of the file to utf-8
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Package import
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import getpass
import time
import random
import re

# Variable declaration
linkedinBase = ""
url = ""

inputContents = open('in.txt', 'r').readlines()
o = open('output.txt', 'w+')

def exporter(l_handle, l):
    o.write(l_handle + "    " + l + "\n")

def wait():
    waitTime = random.randint(0,9) * 0.1 + random.randint(0,9) * 0.01 #+ random.randint(0,1)
    print "waiting: " + str(waitTime) + " secs"
    time.sleep(waitTime)
    return

def passAuth():
    global driver
    wait()
    driver.find_element_by_xpath("""//*[@id="login-email"]""").send_keys(email)
    wait()
    driver.find_element_by_xpath("""//*[@id="login-password"]""").send_keys(password)
    wait()
    driver.find_element_by_xpath("""//*[@id="login-submit"]""").click()
    return

# Asking for creds through terminal
email = str(raw_input("Enter email address: "))
password = getpass.getpass('Enter your password:')

# Change path to chromedriver as needed
chrome_path = './chromedriver'
driver = webdriver.Chrome(chrome_path)

driver.get("https://www.linkedin.com")
driver.implicitly_wait(2)
search = WebDriverWait(driver, 1)

# Logging in with previously provided credential
passAuth()

# Main loop
for line in inputContents:
    print "\n"
    linkedinBase = line.rstrip()
    print linkedinBase

    # Opening of newly generated url
    try:
        driver.get("https://www.linkedin.com/sales/gmail/profile/proxy/" + linkedinBase)
    except:
        print "Page Loading Error"
        o.write(linkedinBase + ",Page error1\n")
        continue

    try:
        contents = driver.find_element_by_css_selector("#experience-section > ul")
    except NoSuchElementException:
        print "Element not found"
        o.write(linkedinBase + ",Page error2\n")
        continue
    
    url = driver.current_url
    o.write(linkedinBase + "," + url +"\n")
    wait()
    
end = raw_input("Press any key to end: ")
driver.close()
