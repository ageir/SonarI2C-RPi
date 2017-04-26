# SonarI2C-RPi
Raspberry Pi Python library for the Octosonar by Alastair Young, @arielnh56

Alastair's Original Arduino library: [github.com](https://github.com/arielnh56/SonarI2C)<br>
Alastair's Blog: [redhunter.com](http://redhunter.com/blog/2016/04/28/sonari2c-multiple-hc-sr04-sensors-on-arduino-i2c/)<br>
Alastair's Hackaday: [hackaday.io](https://hackaday.io/project/19950-hc-sr04-i2c-octopus-octosonar)<br>
Buy it on Tindie: [tindie.com](https://www.tindie.com/products/arielnh56/octosonar-connect-8-x-hc-sr04-to-arduino/)<br>

## Summary

This is a Raspberry Pi python library for the Octosonar by Alastair Young. (@arielnh56)

The Octosonar is a breakout board for connecting eight ultrasonic sensors (HC-SR04) to a microcontroller (Arduino). This library adds support for the Raspberry Pi as well. It's connected via I2C and only needs three pins (SCL/SDA and INT) on the Pi.

Will aslo work with a PCF8574 expander and a NOR gate. See Alastair's links above for more information on how to set that up.

## Supported Platforms

Raspberry Pi (any model) with Python. Tested with Python 2.7.9 and Python 3.4.2

## Getting Started

### Hardware Set Up

<b>Warning:
The Octosonar is a 5V device. You will need an I2C capable logic level converter or you WILL damage your Raspberry Pi!

Do NOT connect the Octosonar directly to the Raspberry Pi!</b>

It has been tested with this level converter from Adafruit.
[https://www.adafruit.com/product/757](https://www.adafruit.com/product/757)

SparkFun aslo has one.
[https://www.sparkfun.com/products/12009](https://www.sparkfun.com/products/12009)

It should work with any I2C capable logic level converter.


### Software Requirements

This library requires the pigpio library. You can download it here:
[http://abyz.co.uk/rpi/pigpio/](http://abyz.co.uk/rpi/pigpio/)<br>

or install it with pip.

Python 2.x
```c
pip install pigpio
```

Python 3.x
```c
pip3 install pigpio
```

### Example Code

SonarI2C_test.py
```c
from SonarI2C import SonarI2C
import pigpio
import time

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
```

## Class Definitions

### Class SonarI2C

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

Example: ```c octosonar = SonarI2C(pi, int_gpio, bus=1, addr=0x3d, max_range_cm=400) ```

### SonarI2C.read()

        Takes a measurement on a port on the Octosonar.
        Not adjusted for round trip. This is the number of
        microseconds that the INT pin is high.

        Arguments:
        port    -- port on the Octosonar, Valid values: 0-7
        Returns: Distance in microseconds. False if timed out.

Example: ```c octosonar.read(0)```

### SonarI2C.read_cm()

        Takes a measurement on a port on the Octosonar.
        Adjusted for round trip. Returns real distance to
        the object.

        Arguments:
        
        port    -- port on the Octosonar, Valid values: 0-7
        Returns: Distance in centimeters. False if timed out.

Example: ```c octosonar.read_cm(0)```

### SonarI2C.read_inch()

        Takes a measurement on a port on the Octosonar.
        Adjusted for round trip. Returns real distance to
        the object.

        Arguments:
        
        port    -- port on the Octosonar, Valid values: 0-7
        Returns: Distance in inches. False if timed out.

Example: ```c octosonar.read_inch(0)```

### SonarI2C.cancel()

        Cancels the Octosonar and cleans up resources.

Example: ```c octosonar.cancel()```
