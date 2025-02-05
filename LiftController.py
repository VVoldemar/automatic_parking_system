from MotorController import MotorController
import Constants
from typing import Union

class LiftController:
    rotation_motor: MotorController
    lifting_motor: MotorController

    rotation: int # clockwise increases
    floor: int

    def __init__(self,
                 rotation_motor: Union[MotorController, None] = None, liffting_motor: Union[MotorController, None] = None):
        if not rotation_motor:
            rotation_motor = MotorController(Constants.PIN_ROTATION_DIRECTION, Constants.PIN_ROTATION_PULSE)
        if not liffting_motor:
            liffting_motor = MotorController(Constants.PIN_LIFTING_DIRECTION, Constants.PIN_LIFTING_PULSE)
        
        self.lifting_motor = liffting_motor
        self.rotation_motor = rotation_motor

        self.floor = 0
        self.rotation = 0

    def move_to(self, floor: int, rotation: int):
        if not 0 <= floor < 3:
            return

        rel_floor = floor - self.floor

        rel_rot = rotation - self.rotation
        rel_rot %= 4
        if rel_rot > 2:
            rel_rot -= 4
        
        self.lifting_motor.go_steps(rel_floor * Constants.STEPS_IN_FLOOR)
        self.rotation_motor.go_steps(rel_rot * Constants.STEPS_IN_QUATER_ROTATION)
        
        self.floor = floor
        self.rotation = rotation

    def clean_up(self):
        self.lifting_motor.clean_up()
        self.rotation_motor.clean_up()



if __name__ == "__main__":
    lift = LiftController()
    while True:
        s = input().split()
        lift.move_to(int(s[0]), int(s[1]))
