import base64
import time
from pathlib import Path
from configparser import ConfigParser


from MqttClient import MqttClient
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('cfg', help='cfg path')
args = parser.parse_args()


config_path = args.cfg

if not Path(config_path).exists():
    raise Exception(f"Config file {config_path} not found")

parser = ConfigParser()
parser.read(config_path)

#################
# Configuration #
#################

user = parser.get("config", "user")
# TODO no plain text password :)
# password = base64.b64decode(parser.get("config", "password")).decode()
password = parser.get("config", "password")
plate = parser.get("config", "plate")
broker_mqtt_ip = parser.get("config", "broker_mqtt_ip")
town = parser.get("config", "town")

mqtt_client = MqttClient("client1", broker_mqtt_ip)


try:
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    browser  = webdriver.Chrome(options=chrome_options)

    # Login page
    browser.get("https://customer.easypark.net/auth?country=ES&lang=es")
    element = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, "userName"))
    )

    browser.find_element_by_id("userName").send_keys(user)
    browser.find_element_by_id("password").send_keys(password)
    browser.find_element_by_id("buttonLogin").click()

    time.sleep(10)
    # Ticket check page
    browser.get("https://customer.easypark.net/ESparkingfine/es?action=hide")


    time.sleep(10)
    print(f"Writing {town} as the city")
    element = browser.find_element_by_css_selector("#content > div > div > div > div.jss57 > div > div > input")
    element.send_keys(town)
    time.sleep(5)
    browser.find_element_by_css_selector("#content > div > div > div > button > span.MuiButton-label").click()
    time.sleep(5)

    print("Writing plate in the form...")
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div > div > div > div.MuiFormControl-root.MuiTextField-root.jss80 > div > input"))
    ).send_keys(plate)

    print("Confirm")

    browser.find_element_by_css_selector("#content > div > div > div > a > button > span.MuiButton-label").click()
    browser.find_element_by_css_selector("#content > div > div > div > button > span.MuiButton-label").click()


    result = WebDriverWait(browser, 1000).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.MuiDialog-root > div.MuiDialog-container.MuiDialog-scrollPaper > div > div > p.jss119"))
    )

    if result.text == "El sistema del operador de parking, que emite las sanciones, no encuentra sanciones anulables en este momento. Por favor, acude al parquímetro más cercano para verificarlo. Matrícula":
        print("No tickets detected")
        mqtt_client.send_no_ticker_notification(plate)
    else:
        print("Tickets detected! Sending notification through mqtt")
        mqtt_client.send_ticket_notification(plate)

except Exception as e:
    print(f"Error: {e}")
    mqtt_client.send_error_notification(plate)

finally:
    browser.quit()




