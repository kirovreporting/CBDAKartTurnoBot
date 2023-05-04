from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os.path
import requests
import json
from pytz import timezone
from datetime import datetime, timedelta


def composeMessage(dates):

    timeZone = timezone('America/Argentina/Buenos_Aires')
    now = datetime.now(timeZone)
    messageText = ""
    oldDaysDump = []
    newDays = []

    try:

        fileModDate = datetime.fromtimestamp(os.path.getmtime(
            "days.txt"), timeZone).replace(hour=0, minute=0, second=0, microsecond=0)

        with open('days.txt', 'r') as oldDaysFile:
            oldDaysDump = json.load(oldDaysFile)
            oldDaysGone = oldDaysDump.copy()

        for date in dates:
            date = date.split(' ', 1)[-1][:-9]
            if date in oldDaysGone:
                oldDaysGone.remove(date)
            else:
                newDays.append(date)

        if not oldDaysGone == []:
            messageText = messageText + "Закрылись даты:\n"
            for goneDay in oldDaysGone:
                messageText = messageText + goneDay + "\n"
                oldDaysDump.remove(goneDay)

        if oldDaysDump == []:
            os.remove("days.txt")

        else:
            nowDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if nowDate - fileModDate == timedelta(days=1):
                messageText = messageText + "Всё ещё доступны для записи:\n"
                for day in oldDaysDump:
                    messageText = messageText + day + "\n"

    except FileNotFoundError:

        for date in dates:

            date = date.split(' ', 1)[-1][:-9]
            newDays.append(date)

    if not newDays == []:

        messageText = messageText + "Новые свободные даты для записи:\n"

        for day in newDays:

            messageText = messageText + day + "\n"

        with open('days.txt', 'w') as oldDaysFile:

            oldDaysDump = oldDaysDump + newDays
            json.dump(oldDaysDump, oldDaysFile)

    if not messageText == "":
        messageText = messageText + \
            "https://www.clubargentinodekart.com.ar/alquiler-de-karting/"

    return messageText


def sendMessage(messageText, token, chat_id):

    method = "sendMessage"
    url = f"https://api.telegram.org/bot{token}/{method}"

    if messageText != "":
        data = {
            'chat_id': chat_id,
            'text': messageText,
        }
        requests.post(url, data=data, stream=True)


try:

    with open('bot.config', 'r') as configFile:
        config = json.load(configFile)

except FileNotFoundError:

    print("Config file not found")
    exit()

# Settings to never touch
url = "https://www.turnonet.com/2010-club-argentino-de-karting-ac"
timeZone = timezone('America/Argentina/Buenos_Aires')
now = datetime.now(timeZone)
dates = []
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=chrome_options)

# checking if we are allowed to send message
if now.hour < config["sleepBefore"] or now.hour > config["sleepAfter"]:
    exit()

# getting current month page
driver.get(url)
WebDriverWait(driver, 30, poll_frequency=1).until(EC.invisibility_of_element_located(
    (By.ID, "prevloader")), 'Timed out waiting for calendar')
soup = BeautifulSoup(driver.page_source, 'html.parser')
freeDatesCurrentMonth = soup.findAll('div', class_='cal_dia')

# getting next month page
driver.find_element(By.CLASS_NAME, 'arrow-next').click()
WebDriverWait(driver, 30, poll_frequency=1).until(EC.invisibility_of_element_located(
    (By.ID, "prevloader")), 'Timed out waiting for calendar')
soup = BeautifulSoup(driver.page_source, 'html.parser')
freeDatesNextMonth = soup.findAll('div', class_='cal_dia')

for freeDate in freeDatesCurrentMonth:
    dates.append(freeDate.find(
        'div', class_='circlegreen ng-binding')['title'])

for freeDate in freeDatesNextMonth:
    dates.append(freeDate.find(
        'div', class_='circlegreen ng-binding')['title'])

sendMessage(composeMessage(dates), config["token"], config["chatID"])
