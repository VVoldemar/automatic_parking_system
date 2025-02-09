from re import S
import sys
from paho.mqtt.client import Client, MQTTMessage
from enum import Enum, auto
from datetime import datetime, timezone, timedelta
from threading import Thread
from time import sleep
import subprocess
import logging

import Constants

class MachineStates(Enum):
    Disconnected = auto()
    Ready = auto()
    Moving_forward = auto()
    Moving_backward = auto()
    Wait_ok__config = auto()
    Wait_ok_forward = auto()
    Wait_ok_backward = auto()


class MQTTServer:
    _broker: str
    _subscription_topic: str
    _publishing_topic: str
    _client: Client

    listen_thread: Thread
    machine_state: MachineStates
    last_packet: datetime

    def __init__(self, broker = "localhost", sub = "esp", pub = "rasp"):
        self._broker = broker
        self._publishing_topic = pub
        self._subscription_topic = sub
        self.machine_state = MachineStates.Disconnected

        # subprocess.run(["mosquitto", "-d", "-c", "mosquitto.conf"], capture_output=True)
        # print("mosquitto started")

        client = self._client = Client()
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect

        client.connect(self._broker, 1883, 60)

        self.listen_thread = Thread(target=self._loop_forever)
        self.listen_thread.start()

        self.last_packet = datetime.now(timezone.utc)

    def is_alive(self):
        alive = self.last_packet + timedelta(minutes=2, seconds=30) > datetime.now(timezone.utc)
        logging.debug(f"MQTTServer is_alive: {alive}")
        return alive

    def move_machine_forward(self):
        # thread unsafe code :D
        # D:
        
        if self.machine_state != MachineStates.Ready:
            return
        
        self._publish("forward")
        self.machine_state = MachineStates.Wait_ok_forward

    def move_machine_backward(self):
        if self.machine_state != MachineStates.Ready:
            return
        
        self._publish("backward")
        self.machine_state = MachineStates.Wait_ok_backward

    def wait_for(self, state: MachineStates) -> bool:
        while self.is_alive():
            if self.machine_state == state:
                return True

            sleep(0.005)
        self.machine_state = MachineStates.Disconnected
        return False

    def _on_connect(self, client: Client, userdata, flags, rc):
        logging.info(f"Connected to mqtt broker with result code {rc}")
        client.subscribe(self._subscription_topic)
        
    def _on_message(self, client: Client, userdata, msg: MQTTMessage):
        data = msg.payload.decode()
        if data == "hello":
            self._publish(f"configF {Constants.FORWARD_STOP_DISTANCE}")
            self._publish(f"configB {Constants.BACKWARD_STOP_DISTANCE}")
            self._publish(f"configL {Constants.LEFT_MOTOR_SPEED}")
            self._publish(f"configR {Constants.RIGHT_MOTOR_SPEED}")
            self.machine_state = MachineStates.Wait_ok__config
        elif data == "ok config" and self.machine_state == MachineStates.Wait_ok__config:
            self.machine_state = MachineStates.Ready
        elif data == "ok forward" and self.machine_state == MachineStates.Wait_ok_forward:
            self.machine_state = MachineStates.Moving_forward
        elif data == "done forward" and self.machine_state == MachineStates.Moving_forward:
            self.machine_state = MachineStates.Ready
        elif data == "ok backward" and self.machine_state == MachineStates.Wait_ok_backward:
            self.machine_state = MachineStates.Moving_backward
        elif data == "done backward" and self.machine_state == MachineStates.Moving_backward:
            self.machine_state = MachineStates.Ready
        elif self.machine_state == MachineStates.Disconnected:
            self.machine_state = MachineStates.Ready

        logging.info(f"recived message in {msg.topic}: {data}, machine state: {self.machine_state}")

        self.last_packet = datetime.now(timezone.utc)
    
    def _on_disconnect(self, client: Client, userdata, *args):
        print(f"disconnected {userdata}")


    def _publish(self, msg: str):
        logging.info(f"sending message: {msg}")
        self._client.publish(self._publishing_topic, msg)

    def _loop_forever(self):
        logging.info("start mqtt loop")
        self._client.loop_forever()
        logging.info("end mqtt loop")
    
    def clean_up(self):
        # subprocess.run(["killall", "mosquitto"], capture_output=True)
        # print("mosquitto killed")
        ...

if __name__ == "__main__":
    server: MQTTServer | None = None
    try:
        server = MQTTServer()
        server.listen_thread.join()
    finally:
        if server:
            server.clean_up()