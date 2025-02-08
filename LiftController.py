from MotorController import MotorController
import Constants
from typing import Union

class LiftController:
    vertical_motors: list[MotorController]
    horizontal_motor: MotorController

    rotation: int # clockwise increases
    floor: int

    def __init__(self,
                 horizontal_motor: Union[MotorController, None] = None,
                 vertical_motors: Union[list[MotorController], None] = None):
        if not horizontal_motor:
            horizontal_motor = MotorController(
                Constants.MOTOR_HORIZONTAL_DIRECTION,
                Constants.MOTOR_HORIZONTAL_PULSE,
                Constants.DELAY_HORIZONTAL
            )
        if not vertical_motors:
            vertical_motors = [
                MotorController(
                    Constants.MOTOR_VERTICAL1_DIRECTION,
                    Constants.MOTOR_VERTICAL1_PULSE,
                    Constants.DELAY_VERTICAL
                ),
                MotorController(
                    Constants.MOTOR_VERTICAL2_DIRECTION,
                    Constants.MOTOR_VERTICAL2_PULSE,
                    Constants.DELAY_VERTICAL
                ),
                MotorController(
                    Constants.MOTOR_VERTICAL3_DIRECTION,
                    Constants.MOTOR_VERTICAL3_PULSE,
                    Constants.DELAY_VERTICAL
                ),
            ]
            
        self.vertical_motors = vertical_motors
        self.horizontal_motor = horizontal_motor

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
        
        tasks = [motor.run_go_steps(-rel_floor * Constants.MICROSTEPS_IN_FLOOR) for motor in self.vertical_motors]

        self.horizontal_motor.go_steps(rel_rot * Constants.MICROSTEPS_IN_QUATER_ROTATION)

        for i in tasks:
            i.join()
        
        self.floor = floor
        self.rotation = rotation

    def clean_up(self):
        self.horizontal_motor.clean_up()
        for motor in self.vertical_motors:
            motor.clean_up()



if __name__ == "__main__":
    lift = LiftController()
    while True:
        s = input().split()
        lift.move_to(int(s[0]), int(s[1]))
