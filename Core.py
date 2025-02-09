from MQTTServer import MQTTServer, MachineStates
from LiftController import LiftController
from datetime import timedelta
from threading import Thread
from Camera import Camera
from typing import Union
from time import sleep
import logging

class Core:
    lift: LiftController
    camera: Camera
    mqtt: MQTTServer

    machines: dict[str, tuple[int, int]]
    is_active: bool
    thread: Thread
    should_shutdown: bool

    def __init__(self, camera: Camera, lift: LiftController, mqtt: MQTTServer):
        self.camera = camera
        self.lift = lift
        self.mqtt = mqtt

        self.is_active = False
        self.should_shutdown = False

        self.thread = Thread(target=self._goooo)
        self.thread.start()

        self.machines = {}

    def _goooo(self):
        while not self.should_shutdown:
            if not self.is_active:
                sleep(1)
                continue
            qr = self.camera.get_detection(timedelta(seconds=1))
            if qr == None:
                continue

                
            logging.info(f"Processing machine with qr: {qr}")

            if qr not in self.machines.keys():
                logging.info(f"Starting loading machine {qr}")

                code = self.load_machine(qr)
            
                if code == 0:
                    logging.info("Loaded machine")
                else:
                    logging.error(f"Failed to load machine, {code=}")
            else:
                logging.info(f"Starting unloading machine {qr}")
                
                code = self.unload_machine(qr)
            
                if code == 0:
                    logging.info("Unloaded machine")
                else:
                    logging.error(f"Failed to unload machine, {code=}")
            
            self.camera.last_detection = None

    def load_machine(self, machine_id: str) -> int:
        floor = None
        rotation = None
        
        if self.mqtt.machine_state == MachineStates.Disconnected:
            return 4

        # print(self.machines)
        for i in range(4):
            for j in range(1, 3):
                # print(i, j, not ((j, i) in self.machines.values()))
                if not ((j, i) in self.machines.values()):
                    floor = j
                    rotation = i
                    break
            else:
                continue
            break
        
        logging.info(f"Loading to {floor=} {rotation=}")
        if floor == None or rotation == None:
            return 1
        
        
        if self.lift.floor != 0 or self.lift.rotation != 0:
            self.lift.move_to(0, 0)
        
        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 2
        
        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_backward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 3
        
        self.machines[machine_id] = (floor, rotation)

        return 0

    def unload_machine(self, machine_id: str) -> int:

        if machine_id not in self.machines.keys():
            return 1
        floor, rotation = self.machines[machine_id]

        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 2
        
        self.lift.move_to(0, 0)
        
        self.mqtt.move_machine_backward()
        
        self.machines.pop(machine_id)

        if not self.mqtt.wait_for(MachineStates.Ready):
            return 3
        
        return 0
