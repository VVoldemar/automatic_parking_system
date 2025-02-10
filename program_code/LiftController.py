from MotorController import MotorController
from program_code import Constants
from typing import Union
import logging

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

        logging.info("LiftController initialized")

    def move_to(self, floor: int, rotation: int):
        if not 0 <= floor < 3:
            logging.error(f"Invalid floor: {floor}")
            return

        rel_floor = floor - self.floor

        rel_rot = rotation - self.rotation
        rel_rot %= 4
        if rel_rot > 2:
            rel_rot -= 4
        
        vert_steps = 0
        if rel_floor == 2:
            vert_steps = Constants.STEPS_IN_BOTH_FLOORS
        elif rel_floor == -2:
            vert_steps = -Constants.STEPS_IN_BOTH_FLOORS
        elif rel_floor == 1:
            if self.floor == 0:
                vert_steps = Constants.STEPS_IN_FLOOR1
            elif self.floor == 1:
                vert_steps = Constants.STEPS_IN_FLOOR2
        elif rel_floor == -1:
            if self.floor == 2:
                vert_steps = -Constants.STEPS_IN_FLOOR2
            elif self.floor == 1:
                vert_steps = -Constants.STEPS_IN_FLOOR1
        # print(self.floor, rel_floor, vert_steps)
        
        tasks = [motor.run_go_steps(vert_steps // 2) for motor in self.vertical_motors]
        for i in tasks:
            i.join()

        self.horizontal_motor.go_steps(rel_rot * Constants.STEPS_IN_QUATER_ROTATION)

        tasks = [motor.run_go_steps(vert_steps // 2) for motor in self.vertical_motors]
        for i in tasks:
            i.join()
        
        self.floor = floor
        self.rotation = rotation

        logging.info(f"Moved to floor: {floor}, rotation: {rotation}")

    def clean_up(self):
        self.horizontal_motor.clean_up()
        for motor in self.vertical_motors:
            motor.clean_up()
        logging.info("LiftController cleaned up")

if __name__ == "__main__":
    lift = LiftController()
    while True:
        s = input().split()
        lift.move_to(int(s[0]), int(s[1]))
