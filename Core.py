from Camera import Camera
from LiftController import LiftController
from MQTTServer import MQTTServer, MachineStates
from threading import Thread
import logging

class Core:
    lift: LiftController
    camera: Camera
    mqtt: MQTTServer

    machines: dict[str, tuple[int, int]]

    thread: Thread

    def __init__(self, camera: Camera, lift: LiftController, mqtt: MQTTServer):
        self.camera = camera
        self.lift = lift
        self.mqtt = mqtt

        self.thread = Thread(target=self._goooo)
        self.thread.start()

        self.machines = {}

    def _goooo(self):
        while True:
            qr = self.camera.get_detection()
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
        
        for i in range(8):
            if (i // 4, i % 4) not in self.machines.values():
                floor = i // 4
                rotation = i % 4
        
        logging.info(f"Loading to {floor=} {rotation=}")
        if floor == None or rotation == None:
            return 1
        
        if self.lift.floor != 0 or self.lift.rotation != 0:
            self.lift.move_to(0, 0)
        
        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 2
        
        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 3
        
        self.machines[machine_id] = (floor, rotation)

        return 0

    def unload_machine(self, machine_id: str) -> int:

        if machine_id not in self.machines.keys():
            return 1
        floor, rotation = self.machines[machine_id]

        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_backward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return 2
        
        self.lift.move_to(0, 0)
        
        self.mqtt.move_machine_backward()
        
        self.machines.pop(machine_id)

        if not self.mqtt.wait_for(MachineStates.Ready):
            return 3
        
        return 0
