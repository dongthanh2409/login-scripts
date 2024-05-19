import logging
import smtplib
import time

import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = 'https://visas-de.tlscontact.com/appointment/gb/gbLON2de/2443099'
username = 'ngdieuthuy.ulis@gmail.com'
password = 'Cmt001198001541@@'
# email
sender = 'dongthanh.2409@gmail.com'
receiver = ['dongthanh.24091@gmail.com', 'dongthanh.2409@gmail.com']
interval_in_minutes = 1


def check():
    driver = webdriver.Chrome()
    driver.get(url)
    login(driver)
    slot = find_slot(driver)
    if slot is not None:
        message = build_message(slot)
        send_email(message)
    logger.info('No available slot')
    driver.quit()


def login(driver):
    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="kc-login"]')
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()


def send_email(message):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, "thvt rfhb bmpz wnjp")
    s.sendmail(sender, receiver, "Hello, \n" + message)
    s.quit()
    logger.info('sent email with body ' + message)


def build_message(slot):
    return 'Found available slot: ' + slot.day + ' ' + slot.hour


class Slot:
    def __init__(self, day, hour):
        self.day = day
        self.hour = hour

    def __str__(self):
        return self.day + ' ' + self.hour


def find_slot(driver):
    time_slots = driver.find_elements(By.CSS_SELECTOR, '.tls-time-group--item .-available')
    if time_slots is None or len(time_slots) == 0:
        return None
    time_slot = time_slots[0]
    parent_element = time_slot.find_element(By.XPATH, './ancestor::div[contains(@class, "tls-time-group--slot")]')
    date = parent_element.find_element(By.CLASS_NAME, 'tls-time-group--header-title')
    return Slot(date.text, time_slot.text)


schedule.every(interval_in_minutes).minutes.do(check)

while True:
    schedule.run_pending()
    time.sleep(1)
