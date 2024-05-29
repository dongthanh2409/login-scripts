import json
import logging
import smtplib
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(filename="newfile1.log",
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

        driver.execute_script("window.open('');")

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[1])

        # Open the second URL in the new tab
        driver.get('https://visas-de.tlscontact.com/services/customerservice/api/tls/appointment/gb/gbLON2de/table'
                   '?client=de&formGroupId=2443099&appointmentType=Short_Stay_Tourism&appointmentStage=appointment')

        time.sleep(5)

        count = 0
        while count < 100:
            time.sleep(5)
            driver.refresh()
            count += 1
            try:
                page_source = driver.page_source
                start = page_source.find('<pre>') + len('<pre>')
                end = page_source.find('</pre>')
                json_data = page_source[start:end]
                data = json.loads(json_data)
                elements_with_value_1 = find_elements_with_value_1(data)
                print(json.dumps(elements_with_value_1, indent=4))
                if len(elements_with_value_1) > 0:
                    notify_all("Found available slots")
                else:
                    logger.info('No available slot')
            except Exception as e:
                logger.info("Something went wrong")
        driver.quit()
        check()

    except Exception as e:
        logger.info("Something else went wrong")


def find_elements_with_value_1(json_obj):
    elements_with_value_1 = {}
    for date, times in json_obj.items():
        for time, value in times.items():
            if value == 1:
                if date not in elements_with_value_1:
                    elements_with_value_1[date] = []
                elements_with_value_1[date].append(time)
    return elements_with_value_1


def notify_one():
    send_email(['dongthanh.2409@gmail.com'], "Manual check required!!!")


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


def notify_all(message):
    send_email(all_receivers, message)


check()

# schedule.every(interval_in_seconds).seconds.do(check)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
