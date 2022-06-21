import paho.mqtt.client as mqtt

class MqttClient:

    def __init__(self, name: str, server_ip: str, channel_name: str = "parking_ticket_bot") -> None:
        try:
            self.client = mqtt.Client(name)
            self.client.connect(server_ip)
            self.channel_name = channel_name
        except Exception as e:
            print("Error trying to connect to mqtt server!")
            print(e)
            raise Exception("Can't connect to mqtt server!")

   
    def send_ticket_notification(self, car_plate: str) -> None:
        """ Sends ticket notification"""
        self.client.publish(f"{self.channel_name}/{car_plate}", "ticket_detected")
    
    def send_no_ticket_notification(self, car_plate: str) -> None:
        """ Sends no ticket notification"""
        self.client.publish(f"{self.channel_name}/{car_plate}", "no_ticket_detected")
    
    def send_error_notification(self, car_plate: str) -> None:
        """ Sends error notification"""
        self.client.publish(f"{self.channel_name}/{car_plate}", "error_checking_ticket")