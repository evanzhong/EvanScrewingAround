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
import datetime as dt
import json

# Variable declaration
isWeekday = dt.datetime.today().weekday() <= 4
meals = ['Breakfast', 'Lunch', 'Dinner']
if not isWeekday:
  meals.remove('Breakfast')
diningHalls = ['FeastAtRieber', 'BruinPlate', 'Covel', 'DeNeve']
urlBase = 'http://menu.dining.ucla.edu/Menus'
calsRegex = '(.*) ([0.9]*.*)'
nutritionRegex = '(.*) ([0-9-.m]*g)([0-9- ]+%|)'
o = open('output.txt', 'w+')

def wait():
  waitTime = random.randint(0,9) * 0.1 + random.randint(0,9) * 0.01 + random.randint(0,1)
  print "waiting: " + str(waitTime) + " secs"
  time.sleep(waitTime)
  return

def openNew():
  accumulator = {}
  driverOpener = webdriver.Chrome(chrome_path)
  driverOpener.get(dishHref)

  icons = driverOpener.find_elements_by_class_name('prodwebcode')
  iconsInformation = []
  for icon in icons:
    iconInfo = str(BeautifulSoup(icon.get_attribute('innerHTML'), "html.parser")).split('>')[1].replace("\xc2\xa0", " ").strip()
    iconsInformation.append(iconInfo)
  
  accumulator["specialInfo"] = iconsInformation
  try:
    nutritionFacts = driverOpener.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[2]')
  except:
    errMsg = "No nutritionFacts found"
    print errMsg
    o.write('\t\t\t' + errMsg + "\n")
    return
  
  nfToParse = BeautifulSoup(nutritionFacts.get_attribute('innerHTML'), "html.parser")

  cals = str(nfToParse.find("p", class_="nfcal").getText()).split('Fat')[0].strip()
  fatCals = str(nfToParse.find("span", class_="nffatcal").getText())
  servingSize = str(nfToParse.find("p", class_="nfserv").getText())
  calsMatches = re.search(calsRegex, cals)
  fatCalsMatches = re.search(calsRegex, fatCals)
  servingMatches = re.search(calsRegex, servingSize)
  
  accumulator[str(calsMatches.group(1))] = calsMatches.group(2)
  accumulator[str(fatCalsMatches.group(1))] = fatCalsMatches.group(2)
  accumulator[str(servingMatches.group(1))] = servingMatches.group(2).replace("\xc2\xa0", " ")

  # Process Nutrients
  nutrients = nfToParse.find_all("p", class_="nfnutrient")
  for nutrient in nutrients:
    nutrientInfo = str(nutrient.getText()).strip()
    matches = re.search(nutritionRegex, nutrientInfo)
    try:
      accumulator[str(matches.group(1))] = {
        "amt": str(matches.group(2)),
        "percentDaily": str(matches.group(3)).strip()
      }
    except:
      errMsg = "Something went wrong with the regex for: " + nutrientInfo
      print errMsg
      o.write('\t\t\t' + errMsg + "\n")


  
  # Process Vitamins
  for vitamin in nfToParse.find_all("span", class_="nfvitname"):
    accumulator[str(vitamin.getText())] = str(vitamin.find_next_sibling("span").getText())

  # ingredients = driverOpener.find_element_by_xpath('//*[@id="main-content"]/div[2]/div[3]/p[1]')
  # o.write('\t\t\t' + str(ingredients.getText()) + "\n")

  driverOpener.close()
  print accumulator
  return accumulator

# Change path to chromedriver as needed
chrome_path = './chromedriver'
driver = webdriver.Chrome(chrome_path)
driver.get("http://menu.dining.ucla.edu/")
# driver.implicitly_wait(2)
# search = WebDriverWait(driver, 1)

startTime = time.time()
try:
  # Main loop
  for meal in meals: #Turn into function calls later on a cron basis
    for diningHall in diningHalls:
      driver.get(urlBase + '/' + diningHall + '/' + meal)
      main_window = driver.current_window_handle
      try:
        driver.find_element_by_class_name('menu-block')
        mealObj = {
          "_meal": meal,
          "_diningHall": diningHall
        }
      except:
        errString = 'No Menu block found for ' + meal + ' at ' + diningHall
        print errString
        o.write(errString + "\n")
        continue
      
      sections = driver.find_elements_by_css_selector('li.sect-item')
      for section in sections:
        sectionTitle = str(BeautifulSoup(section.get_attribute('innerHTML'), "html.parser")).split('<ul')[0].strip()
        sectionArr = []
        dishes = section.find_elements_by_css_selector('a.recipelink')
        for dish in dishes:
          dishName = BeautifulSoup(dish.get_attribute('innerHTML'), "html.parser")
          dishHref = dish.get_attribute('href')

          dishObj = {
            "dishName": str(dishName),
            "dishHref": str(dishHref),
            "nutritionFacts": openNew()
          }
          sectionArr.append(dishObj)

        mealObj[sectionTitle] = sectionArr
      o.write(json.dumps(mealObj, sort_keys=True, indent=4) + "\n")
except:
  print 'Some error happened'      
finally:
  print "Process ran in: " + str(startTime - time.time()) + " seconds" 
  end = raw_input("Press any key to end: ")
  driver.close()