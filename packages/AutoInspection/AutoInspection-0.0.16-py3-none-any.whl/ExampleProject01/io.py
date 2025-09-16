import time
import hexss
from hexss.raspberrypi.gpio import DigitalInputDevice, DigitalOutputDevice

hexss.check_packages(
    'requests',
    auto_install=True
)
import requests


class GPIOMapping:
    def __init__(self):
        self.rad_tower = DigitalOutputDevice(4, active_high=True)
        self.buzzer = DigitalOutputDevice(17, active_high=True)
        self.yello_tower = DigitalOutputDevice(18, active_high=True)
        self.yello_LED = DigitalOutputDevice(27, active_high=True)
        self.green_tower = DigitalOutputDevice(22, active_high=True)
        self.green_LED = DigitalOutputDevice(23, active_high=True)
        self.o7 = DigitalOutputDevice(24, active_high=True)
        self.o8 = DigitalOutputDevice(25, active_high=True)

        self.i1 = DigitalInputDevice(5, bounce_time=0.1)
        self.yello_button = DigitalInputDevice(6, bounce_time=0.1)
        self.i3 = DigitalInputDevice(12, bounce_time=0.1)
        self.green_button = DigitalInputDevice(13, bounce_time=0.1)
        self.i5 = DigitalInputDevice(16, bounce_time=0.1)
        self.i6 = DigitalInputDevice(19, bounce_time=0.1)
        self.i7 = DigitalInputDevice(20, bounce_time=0.1)
        self.i8 = DigitalInputDevice(21, bounce_time=0.1)

        self._prev_green = self.green_button.value
        self.green_LED.on()

    def update(self):
        url = 'http://192.168.225.137:3000'
        current = self.green_button.value
        if self._prev_green == 0 and current == 1:  # rising edge
            try:
                r = requests.post(url, data={'button': 'Capture&Predict'})
                print("RISING detected:", r.status_code)
                self.green_LED.off()
            except Exception as e:
                print(e)
        self._prev_green = current

        try:
            r = requests.get(f'{url}/data')
            data = r.json()
            res = data['config'].get('res')
            if res == 'OK':
                self.rad_tower.off()
                self.yello_tower.off()
                self.green_tower.on()

                self.green_LED.on()
            elif res == 'NG':
                self.rad_tower.on()
                self.yello_tower.off()
                self.green_tower.off()

                self.green_LED.on()
            else:
                self.rad_tower.off()
                self.yello_tower.on()
                self.green_tower.off()

        except Exception as e:
            print(e)


if __name__ == "__main__":
    gpio = GPIOMapping()

    while True:
        gpio.update()
        time.sleep(0.1)
