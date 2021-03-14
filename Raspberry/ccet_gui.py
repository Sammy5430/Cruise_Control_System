from guizero import App, Text, Box, PushButton, Picture
from gpiozero import MCP3008, Button, PWMOutputDevice, DigitalOutputDevice, DigitalInputDevice
import time

# ================Remote=================== #
import os
os.environ.__setitem__('DISPLAY', ':0.0')
# ================Control================== #

# ==================Files================== #
bat_lvl_5 = "/home/pi/Documents/CCET/Battery/battery5.png"
bat_lvl_4 = "/home/pi/Documents/CCET/Battery/battery4.png"
bat_lvl_3 = "/home/pi/Documents/CCET/Battery/battery3.png"
bat_lvl_2 = "/home/pi/Documents/CCET/Battery/battery2.png"
bat_lvl_1 = "/home/pi/Documents/CCET/Battery/battery1.png"
bat_lvl_0 = "/home/pi/Documents/CCET/Battery/battery0.png"

cruise_on_img = '/home/pi/Documents/CCET/Cruise/CruiseON.png'
cruise_off_img = '/home/pi/Documents/CCET/Cruise/CruiseOFF.png'
# ========================================= #

# ================GPIO Pins================ #
btn_kill_pin = Button(6)
btn_inc_pin = Button(4)
btn_dec_pin = Button(5)
btn_set_pin = Button(25)

pwm_out_pin = PWMOutputDevice(13)
bts_enable_pin = DigitalOutputDevice(12)
hall_pin = DigitalInputDevice(17)
brake_sensor = DigitalInputDevice(26)

#volt_sens_pin = MCP3008(channel=0)
#curr_sens_pin = MCP3008(channel=1)
# ========================================= #

# ===============Variables================= #
is_cruise_on = True
magnet_count = 0
rpm_val = 0
mph_val = 0     # curr speed
v_sensor_val = 99
i_sensor_val = 0
pwm_duty_cycle = 0
start_time = time.time()
end_time = 0
diameter = 26
cruise_set_spd = 5
cruise_lvl_val = cruise_off_img
# ========================================= #

# ==============Enables==================== #
bts_enable_pin.value = 0
# ========================================= #

def killBtn():
    bts_enable_pin.value = 0
    globals()['pwm_duty_cycle'] = 0
    print(globals()['pwm_duty_cycle'])
    pwm_out_pin.value = pwm_duty_cycle


def brakeBtn():
    if globals()['is_cruise_on']:
        globals()['is_cruise_on'] = False
        globals()['cruise_set_spd'] = 0
        set_spd.value = str(cruise_set_spd) + "mph"
        print('brake stopped cruise control')

# TODO: Ensure only 1 decimal place is printed
def incSpeedBtn():
    if globals()['cruise_set_spd'] <=6:
        globals()['cruise_set_spd'] = globals()['cruise_set_spd']+1
        set_spd.value = str(cruise_set_spd) + "mph"

# TODO: Ensure only 1 decimal place is printed
def decSpeedBtn():
    if globals()['cruise_set_spd'] >= 4:
        globals()['cruise_set_spd'] = globals()['cruise_set_spd']-1
        set_spd.value = str(cruise_set_spd) + "mph"


def cruiseSetBtn():
    if is_cruise_on:
        globals()['cruise_set_spd'] = 0
        globals()['is_cruise_on'] = False
    else:
        if globals()['mph_val'] >= 3 or globals()['mph_val'] <= 7:    # if less than 3mph, can't activate
            globals()['cruise_set_spd'] = globals()['mph_val']
            globals()['is_cruise_on'] = True


def rpmCount():
    globals()['magnet_count'] = globals()['magnet_count'] + 1
    if magnet_count >= 2:
        updateRPM()

# TODO: Ensure only 1 decimal place is printed
def updateRPM():
    globals()['end_time'] = time.time()
    globals()['rpm_val'] = ((magnet_count * 60) / (globals()['end_time'] - globals()['start_time'])) / 2
    globals()['mph_val'] = ((diameter / 12) * 3.14 * globals()['rpm_val'] * 60) / 5280
    globals()['start_time'] = globals()['end_time']
    globals()['magnet_count'] = 0
    cur_spd.value = str(globals()['mph_val'])[0:3] + "mph"
    print("RPM: " + str(globals()['rpm_val']) + "\nMPH: " + str(globals()['mph_val']))


def control():
    x = (globals()['cruise_set_spd'] - globals()['mph_val']) * 2 #gain = 2(arbitrario) , set val in RPM
    print(x)
    if x < 0:
        x = 0
    elif x > 12:
        x = 12
    globals()['pwm_duty_cycle'] = x / 12


def inc_pwm():
    if pwm_duty_cycle < 1:
        bts_enable_pin.value = 1
        globals()['pwm_duty_cycle'] = globals()['pwm_duty_cycle'] + 0.05  #0.05 = ~1.3 +- .1
        if globals()['pwm_duty_cycle'] > 1:
            globals()['pwm_duty_cycle'] = 1
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle


def dec_pwm():
    if pwm_duty_cycle > 0:
        globals()['pwm_duty_cycle'] = globals()['pwm_duty_cycle'] - 0.05
        if globals()['pwm_duty_cycle'] < 0:
            globals()['pwm_duty_cycle'] = 0
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle

# TODO: Add voltage sensor input
def bat_lvl_check():
    if v_sensor_val > 80:
        battery_info_img.value = bat_lvl_5
    elif v_sensor_val > 60:
        battery_info_img.value = bat_lvl_4
    elif v_sensor_val > 40:
        battery_info_img.value = bat_lvl_3
    elif v_sensor_val > 20:
        battery_info_img.value = bat_lvl_2
    elif v_sensor_val > 10:
        battery_info_img.value = bat_lvl_1
    elif v_sensor_val > 5:
        battery_info_img.value = bat_lvl_1  # And trigger blink anim
    elif v_sensor_val > 0:
        battery_info_img.value = bat_lvl_0  # And trigger blink anim
    else:
        print("out of battery")

# =================Interrupts============== #
btn_inc_pin.wait_for_press = incSpeedBtn
btn_dec_pin.when_pressed = decSpeedBtn
btn_set_pin.when_pressed = cruiseSetBtn
btn_kill_pin.when_pressed = killBtn
hall_pin.when_activated = rpmCount
brake_sensor.when_deactivated = brakeBtn
# ========================================= #

# ===================GUI=================== #
app = App(title="Cruise Control Exhibition Tricycle", bg="#363636")

header_box = Box(app, width="fill", align="top", border=False)
header_text = Text(header_box, text="Cruise Control Exhibition Tricycle", color="white", height=2, size=24)
# emergency_btn_gui = PushButton(header_box, text="Emergency Stop", height=20, width=500, command=killBtn)
# emergency_btn_gui.bg = "red"

info_box = Box(app, width="fill", align="bottom", border=False)

cruise_info_box = Box(info_box, height="fill", width="fill", align="left", border=False)
cruise_info_img_padding = Text(cruise_info_box, text="    ", color="white", size=24, height=2, align='right')
cruise_info_img = Picture(cruise_info_box, image=cruise_lvl_val, width=70,
                          height=70, align="right")
cruise_info_text = Text(cruise_info_box, text="Cruise Control:", color="white", size=24, height=2)

battery_info_box = Box(info_box, height="fill", width="fill", align="right", border=False)
battery_info_img_padding = Text(battery_info_box, text=" ", color="white", size=24, height=2, align='right')
battery_info_img = Picture(battery_info_box, image=bat_lvl_5, width=120,
                           height=60, align="right")
battery_info_text = Text(battery_info_box, text="Battery:", color="white", size=24, height=2)

set_spd_box = Box(app, width="fill", height="fill", align="left", border=True)
set_spd_txt_padding = Text(set_spd_box, text=" ", color="white", size=35, height=1, align='top')
set_spd_text = Text(set_spd_box, text="Set Speed", height=2, color="white", size=32)
set_spd = Text(set_spd_box, text=str(globals()['cruise_set_spd'])+"mph", color="white", size=40)
# dec_btn_gui = PushButton(set_spd_box, text="Speed -", height=20, width=20, command=dec_pwm)
# dec_btn_gui.bg = "white"

cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(globals()['mph_val'])+"mph", color="yellow", size=60)
# inc_btn_gui = PushButton(cur_spd_box, text="Speed +", height=20, width=20, command=inc_pwm)
# inc_btn_gui.bg = "white"

app.set_full_screen()
# =========================================== #

# =================System==================== #
# if magnet_count >= 2:
#     updateRPM()
# if is_cruise_on:
#     control()
# =========================================== #
bat_lvl_check()

app.display()

# TODO: Add watchdog timer to lower mph to 0 upon stopping
# TODO: Determine GUI behavior when battery is at 0%
