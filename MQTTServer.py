from paho.mqtt.client import Client, MQTTMessage
from enum import Enum, auto
from datetime import datetime, timezone
from threading import Thread

class MachineStates(Enum):
    Disconnected = auto()
    Ready = auto()
    Moving_forward = auto()
    Wait_ok__config = auto()
    Wait_ok_forward = auto()


class MQTTServer:
    _broker: str
    _subscription_topic: str
    _publishing_topic: str
    _client: Client

    listen_thread: Thread
    machine_state: MachineStates
    last_packet: datetime

    def __init__(self, broker = "localhost", sub = "esp", pub="rasp"):
        self._broker = broker
        self._publishing_topic = pub
        self._subscription_topic = sub
        self.machine_state = MachineStates.Disconnected

        client = self._client = Client()
        client.on_connect = self._on_connect
        client.on_message = self._on_message

        client.connect(self._broker, 1883, 60)

        self.listen_thread = Thread(target=client.loop_start)
        self.listen_thread.start()

    def move_machine_forward(self):
        # thread unsafe code :D
        # D:
        
        if self.machine_state != MachineStates.Ready:
            return
        
        self._publish("forward")
        self.machine_state = MachineStates.Wait_ok_forward

    def _on_connect(self, client: Client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self._subscription_topic)
        
    def _on_message(self, client: Client, userdata, msg: MQTTMessage):
        print(f"Received message: {msg.topic} {msg.payload.decode()}")
        
        data = msg.payload.decode()
        if data == "hello" and self.machine_state == MachineStates.Disconnected:
            self._publish("config ")
            self.machine_state = MachineStates.Wait_ok__config
        elif data == "ok config" and self.machine_state == MachineStates.Wait_ok__config:
            self.machine_state = MachineStates.Ready
        elif data == "ok forward" and self.machine_state == MachineStates.Wait_ok_forward:
            self.machine_state = MachineStates.Moving_forward
        elif data == "done forward" and self.machine_state == MachineStates.Moving_forward:
            self.machine_state = MachineStates.Ready

        self.last_packet = datetime.now(timezone.utc)

    def _publish(self, msg: str):
        self._client.publish(self._publishing_topic, msg)