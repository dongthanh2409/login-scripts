import logging
import smtplib
import sys
import time

import schedule
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = 'https://visas-de.tlscontact.com/appointment/gb/gbLON2de/2443099'
username = 'ngdieuthuy.ulis@gmail.com'
password = 'Cmt001198001541@@'
# email
sender = 'dongthanh.2409@gmail.com'
all_receivers = ['dongthanh.24091@gmail.com', 'dongthanh.2409@gmail.com', 'ngdieuthuy.ulis@gmail.com']
interval_in_seconds = 60


def check():
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        login(driver)
        driver.implicitly_wait(45)

        confirm_button = find_confirm_button(driver)
        if confirm_button_pop_up(confirm_button):
            click_button(driver, confirm_button)
        else:
            # notify_one()
            return

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(5)
        next_button_1 = find_next_button_1(driver)
        if next_button_1 is not None:
            click_button(driver, next_button_1)

        time.sleep(5)
        next_button_2 = find_next_button_2(driver)
        if next_button_2 is not None:
            click_button(driver, next_button_2)

        if number_of_unavailable_slots_looks_wrong(driver):
            # notify_one()
            return

        slot = find_slot(driver)
        if slot is not None:
            message = build_message(slot)
            notify_all(message)

        logger.info('No available slot')
        driver.quit()
    except Exception as e:
        logger.info("Something  went wrong")


def find_next_button_1(driver):
    return driver.find_element(By.XPATH, '//*[@id="app"]/div[4]/div[2]/div[2]/div[2]/button')


def find_next_button_2(driver):
    return driver.find_element(By.XPATH, '//*[@id="app"]/div[4]/div[2]/div[2]/div[2]/button[2]')


def click_button(driver, button):
    ActionChains(driver).move_to_element(button).click(button).perform()


def notify_all(message):
    send_email(all_receivers, message)


def notify_one():
    send_email(['dongthanh.2409@gmail.com'], "Manual check required!!!")


def find_confirm_button(driver):
    try:
        return driver.find_element(By.XPATH, '//*[@id="app"]/div[4]/div[3]/div[2]/div/div/div[2]/div[4]/div/button')
    except Exception as e:
        return None


def number_of_unavailable_slots_looks_wrong(driver):
    unavailable_time_slots = driver.find_elements(By.CSS_SELECTOR, '.tls-time-group--item .-unavailable')
    unavailable_time_slots_count = len(unavailable_time_slots)
    print(unavailable_time_slots_count)
    return unavailable_time_slots_count % 16 != 0


def confirm_button_pop_up(confirm_button):
    return confirm_button is not None


def login(driver):
    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="kc-login"]')
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()


def send_email(receivers, message):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, "thvt rfhb bmpz wnjp")
    s.sendmail(sender, receivers, "Hello, \n" + message)
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


# check()

schedule.every(interval_in_seconds).seconds.do(check)

while True:
    schedule.run_pending()
    time.sleep(1)
