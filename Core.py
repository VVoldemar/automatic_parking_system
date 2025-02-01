from Camera import Camera
from LiftController import LiftController
from MQTTServer import MQTTServer, MachineStates
from threading import Thread

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

    def _goooo(self):
        while True:
            qr = self.camera.get_detection()
            if qr in self.machines.keys():
                self.unload_machine(qr)
            else:
                self.load_machine(qr)


    def load_machine(self, machine_id: str):
        floor = None
        rotation = None
        
        for i in range(8):
            if (i // 4, i % 4) not in self.machines.values():
                floor = i // 4
                rotation = i % 4
        
        if floor == None or rotation == None:
            return
        
        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return
        
        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_forward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return
        
        self.machines[machine_id] = (floor, rotation)


    def unload_machine(self, machine_id: str):
        if machine_id not in self.machines.keys():
            return
        floor, rotation = self.machines[machine_id]

        self.lift.move_to(floor, rotation)

        self.mqtt.move_machine_backward()
        if not self.mqtt.wait_for(MachineStates.Ready):
            return
        
        self.lift.move_to(0, 0)
        
        self.mqtt.move_machine_backward()
        self.machines[machine_id] = (-1, 0)

        if not self.mqtt.wait_for(MachineStates.Ready):
            return

