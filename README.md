# parking-ticket-bot
Easypark A Coruña parking ticket bot. Checks if your car has been fined.

Each time the script is executed sends a MQTT message topic `parking_ticket_bot/{CAR_PLATE}` with payload:
* ticket_detected
* no_ticket_detected
* error_checking_ticket


# Installation
```bash
pip3 install -r requirements.txt
```

# Usage

Modify values in the example config file:

```conf
[config]
user = {username}
password = {password}
plate = {plate_number}
broker_mqtt_ip = {broker_mqtt_ip}
town = A Coruña
```

Execute:
```bash
python3 ticket_bot.py configs/example.conf
```
