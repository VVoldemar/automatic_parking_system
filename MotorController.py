import RPi.GPIO as GPIO
from time import sleep
import Constants
from threading import Thread

class MotorController:
    _direction_pin: int
    _pulse_pin: int

    delay: float
    possition: int

    def __init__(self, direction_pin: int, pulse_pin: int, delay: float):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(direction_pin, GPIO.OUT)
        GPIO.setup(pulse_pin, GPIO.OUT)

        self._direction_pin = direction_pin
        self._pulse_pin = pulse_pin
        self.delay = delay

        self.possition = 0

    def run_go_steps(self, steps_num: int) -> Thread:
        thread = Thread(target=self.go_steps, args=[steps_num])
        thread.start()
        return thread

    def go_steps(self, steps_num: int) -> None:
        is_clockwise = steps_num >= 0
        steps_num = abs(steps_num)

        print(f"rotating {steps_num} steps on {self._pulse_pin} pin")
        for _ in range(steps_num):
            self.pulse(is_clockwise)
        print("rotated")

    def pulse(self, is_clockwise: bool):
        GPIO.output(self._direction_pin, not is_clockwise)
        
        GPIO.output(self._pulse_pin, GPIO.HIGH)
        sleep(self.delay)
        GPIO.output(self._pulse_pin, GPIO.LOW)
        sleep(self.delay)

        self.possition += 1 if is_clockwise else -1

    def clean_up(self):
        GPIO.cleanup(self._direction_pin)
        GPIO.cleanup(self._pulse_pin)