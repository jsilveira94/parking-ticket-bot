import base64
import time
from pathlib import Path
from configparser import ConfigParser


import paho.mqtt.client as mqtt
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
# password = base64.b64decode(parser.get("config", "password")).decode()
password = parser.get("config", "password")
plate = parser.get("config", "plate")
broker_mqtt_ip = parser.get("config", "broker_mqtt_ip")


def send_ticket_notification(msg="ticket_detected"):
    client = mqtt.Client("P1")
    client.connect(broker_mqtt_ip) 
    client.publish(f"parking_ticket_bot/{plate}",msg)


# Initiate the browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
browser  = webdriver.Chrome(options=chrome_options)


browser.get("https://customer.easypark.net/auth?country=ES&lang=es")




try:
    element = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, "userName"))
    )

    browser.find_element_by_id("userName").send_keys(user)
    browser.find_element_by_id("password").send_keys(password)

    browser.find_element_by_id("buttonLogin").click()

    time.sleep(10)
    browser.get("https://customer.easypark.net/ESparkingfine/es?action=hide")


    time.sleep(10)
    print("mandando a coruña como sitio...")
    element = browser.find_element_by_css_selector("#content > div > div > div > div.jss57 > div > div").click()
    element = browser.find_element_by_css_selector("#content > div > div > div > div.jss57 > div > div > input")
    element.send_keys("A Coruña")

    # elemnent = WebDriverWait(browser, 30).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div > div > div > button > span.MuiButton-label"))
    # )

    browser.find_element_by_css_selector("#content > div > div > div > button > span.MuiButton-label").click()
    time.sleep(5)

    print("sending plate to the web...")
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div > div > div > div.MuiFormControl-root.MuiTextField-root.jss80 > div > input"))
    ).send_keys(plate)

    print("click en consultar")

    browser.find_element_by_css_selector("#content > div > div > div > a > button > span.MuiButton-label").click()
    browser.find_element_by_css_selector("#content > div > div > div > button > span.MuiButton-label").click()


    result = WebDriverWait(browser, 1000).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.MuiDialog-root > div.MuiDialog-container.MuiDialog-scrollPaper > div > div > p.jss119"))
    )

    if result.text == "El sistema del operador de parking, que emite las sanciones, no encuentra sanciones anulables en este momento. Por favor, acude al parquímetro más cercano para verificarlo. Matrícula":
        print("No hay multas")
        send_ticket_notification(msg="no_ticket_detected")
    else:
        print("Multas")
        send_ticket_notification()
    browser.quit()


except Exception as e:
    print(f"Error: {e}")
    send_ticket_notification()
    browser.quit()
