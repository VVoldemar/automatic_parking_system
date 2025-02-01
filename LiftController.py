from MotorController import MotorController
import Constants

class LiftController:
    rotation_motor: MotorController
    lifting_motor: MotorController

    rotation: int # clockwise increases
    floor: int



    def __init__(self, rotation_motor: MotorController = None, liffting_motor: MotorController = None):
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