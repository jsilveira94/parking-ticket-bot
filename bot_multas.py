import requests
from MqttClient import MqttClient
from configparser import ConfigParser
from pathlib import Path
from configparser import ConfigParser
import argparse

LOGIN_URL = "https://customer.easypark.net/api/web-auth/login/auth"
FINE_CHECK_URL = "https://customer.easypark.net/api/b2c/parking/finesbylicenseplate"
INTEGRATION_TYPE = "Epark_15" # I don't know what is this :)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('cfg', help='cfg path')
args = arg_parser.parse_args()


config_path = args.cfg
if not Path(config_path).exists():
    raise Exception(f"Config file {config_path} not found")

parser = ConfigParser()
parser.read(config_path)


user = parser.get("config", "user")
password = parser.get("config", "password")
plate = parser.get("config", "plate")
broker_mqtt_ip = parser.get("config", "broker_mqtt_ip")
town = parser.get("config", "town")

mqtt_client = MqttClient("client1", broker_mqtt_ip)

auth_payload = {
  "userName": user,
  "password": password
}

with requests.Session() as s:

    p = s.post(LOGIN_URL, data=auth_payload)   
    
    if p.status_code is not 200:
        print("Error login in!")
        mqtt_client.send_error_notification(plate)
        exit()

    login_info = p.json()
    user_id = login_info["user"]["id"]
    payload_fine_request = {
        "parkingUserId": user_id,
        "integrationType": INTEGRATION_TYPE,
        "licensePlate": plate
    }

    r = s.post(FINE_CHECK_URL, data=payload_fine_request)
    if r.status_code is not 200:
        print("Error on fine request!")
        mqtt_client.send_error_notification(plate)
        exit()

    fines_info = r.json()
    if len(fines_info["parkingFines"]) > 0:
        mqtt_client.send_ticket_notification(plate)
    else:
        mqtt_client.send_no_ticket_notification(plate)