"""
Octosonar library for the Raspberry Pi.
Copyright (c) 2017 Goran Lundberg

Licenced under the MIT Licence.

Octosonar by Alastair Young
https://hackaday.io/project/19950-hc-sr04-i2c-octopus-octosonar

Requires the pigpio library
http://abyz.co.uk/rpi/pigpio/

"""

import pigpio
import time


class SonarI2C(object):
    def __init__(self, pi, int_gpio, bus=1, addr=0x3d, max_range_cm=400):
        """
        OctoSonarI2C, class for the Octosonar by Alastair Young

        Arguments:
        pi          -- pigpio instance
        int_gpio    -- the GPIO connected to the octosonars INT pin.
                       BCM numbering.
        bus         -- The i2c bus number, set 0 for the first Raspberry Pi
                       model with 256MB ram, else 1.
                       default: 1
        addr        -- i2c address of the octosonar.
                       default: 0x3d
        max_range_cm-- Maximum range for the sonars in centimeters.
                       default: 400
        """

        self.pi = pi
        self.addr = addr
        self.int_gpio = int_gpio

        self.SPEED_OF_SOUND = 340.29  # metres per second
        self.SPEED_OF_SOUND_INCH = 13397.244094  # inches per second
        self.max_range_cm = max_range_cm
        self._timeout = (2.0 * self.max_range_cm / 100.0) / self.SPEED_OF_SOUND

        # Initiate i2c connection
        self._i2c_handle = self.pi.i2c_open(bus, addr)
        # The PCF8574 pins are set to high on power on. Set all pins to low.
        self.pi.i2c_write_byte(self._i2c_handle, 0x00)
        # Set the INT GPIO pin to input
        self.pi.set_mode(self.int_gpio, pigpio.INPUT)

        # Callback variables
        self._tick = None
        self._edge = 3
        self._micros = 0
        self._reading = False

        # Set up callback function for the INT GPIO pin
        self._callback = self.pi.callback(self.int_gpio, pigpio.EITHER_EDGE,
                                          self._callbackfun)

    def _callbackfun(self, gpio, level, tick):
        """
        Callback function. Either edge on the INT pin triggers the callback
        and this function calculates the time between the edges.
        """
        if self._edge == 1:
            self._tick = tick
        elif self._edge == 2:
            diff = pigpio.tickDiff(self._tick, tick)
            self._micros = diff
            self._reading = True
        self._edge += 1

    def cancel(self):
        """
        Cancels the Octosonar.
        """
        self.pi.i2c_close(self._i2c_handle)
        if self._callback is not None:
            self._callback.cancel()

    def read(self, port):
        """
        Takes a measurement on a port on the Octosonar.
        Not adjusted for round trip. This is the number of
        microseconds that the INT pin is high.

        Arguments:
        port    -- port on the Octosonar, Valid values: 0-7

        Returns: Distance in microseconds. False if timed out.
        """
        if self.int_gpio is not None:

            self._edge = 1
            self._reading = False
            # trigger the sonar
            self.pi.i2c_zip(self._i2c_handle, [4, self.addr,
                                               7, 1, (1 << port),
                                               7, 1, 0x00,
                                               0])
            timeout = time.time() + self._timeout
            while not self._reading:
                if time.time() > timeout:
                    return False
                time.sleep(0.001)
            return self._micros

    def read_cm(self, port):
        """
        Takes a measurement on a port on the Octosonar.
        Adjusted for round trip. Returns real distance to
        the object.

        Arguments:
        port    -- port on the Octosonar, Valid values: 0-7

        Returns: Distance in centimeters.
        """
        self.read(port)
        return self._micros * (self.SPEED_OF_SOUND / 20000.0)

    def read_inch(self, port):
        """
        Takes a measurement on a port on the Octosonar.
        Adjusted for round trip. Returns real distance to
        the object.

        Arguments:
        port    -- port on the Octosonar, 0-7

        Returns: Distance in inches.
        """
        self.read(port)
        return self._micros * (self.SPEED_OF_SOUND_INCH / 2000000.0)


if __name__ == "__main__":
    print("Press CTRL-C to cancel.")
    pi = pigpio.pi()
    if not pi.connected:
        exit(0)
    try:
        octosonar = SonarI2C(pi, int_gpio=25)
        result_list = []
        while True:
            for i in range(8):
                sonar_result = octosonar.read_cm(i)
                time.sleep(0.01)
                if sonar_result is False:
                    result_list.append("Timed out")
                else:
                    result_list.append(round(sonar_result, 1))
            print(result_list)
            result_list = []

    except KeyboardInterrupt:
        print("\nCTRL-C pressed. Cleaning up and exiting.")
    finally:
        octosonar.cancel()
        pi.stop()
