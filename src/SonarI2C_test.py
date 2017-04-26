"""
Octosonar test for the Raspberry Pi.
Copyright (c) 2017 Goran Lundberg

Licenced under the MIT Licence.

Octosonar by Alastair Young
https://hackaday.io/project/19950-hc-sr04-i2c-octopus-octosonar

Requires the pigpio library
http://abyz.co.uk/rpi/pigpio/

"""

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
