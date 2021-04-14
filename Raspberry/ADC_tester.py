import time
from gpiozero import MCP3008

vref = 6
volt_conversion_factor = 5.0
curr_conversion_factor = 66.0

curr_sens_pin = MCP3008(channel=0, differential=False, max_voltage=vref)
motor_volt_sens_pin = MCP3008(channel=1, differential=False, max_voltage=vref)

while True:
    voltage_value = motor_volt_sens_pin.value * vref * volt_conversion_factor
    current_value = (curr_sens_pin.value * vref) / 66
    print("Voltage Output: " + str(voltage_value))
    print("Current Output: " + str(current_value))
    time.sleep(1)

