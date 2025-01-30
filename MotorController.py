import RPi.GPIO as GPIO
from time import sleep

class MotorController:
    _direction_pin: int
    _pulse_pin: int
    
    possition: int

    def __init__(self, direction_pin: int, pulse_pin: int):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(direction_pin, GPIO.OUT)
        GPIO.setup(pulse_pin, GPIO.OUT)

        self._direction_pin = direction_pin
        self._pulse_pin = pulse_pin

    def go_steps(self, steps_num: int) -> None:
        is_clockwise = steps_num >= 0
        steps_num = abs(steps_num)

        for _ in range(steps_num):
            self.pulse(is_clockwise)

    def pulse(self, is_clockwise: bool, delay: float = 0.0005):
        GPIO.output(self._direction_pin, not is_clockwise)
        
        GPIO.output(self._pulse_pin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(self._pulse_pin, GPIO.LOW)
        sleep(delay)

        self.possition += 1 if is_clockwise else -1