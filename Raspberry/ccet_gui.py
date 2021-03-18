from guizero import App, Text, Box, PushButton, Picture
from gpiozero import MCP3008, Button, PWMOutputDevice, DigitalOutputDevice, DigitalInputDevice
import time
import threading

# ================Remote=================== #
import os
os.environ.__setitem__('DISPLAY', ':0.0')
# ================Control================== #


class piThread (threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        if self.threadName is "battery":
            while True:
                if bat_blink:
                    battery_info_img.value = bat_lvl_1
                    time.sleep(1)
                    battery_info_img.value = bat_lvl_0
                    time.sleep(1)
                else:
                    time.sleep(1)
                threadLock.acquire()
                bat_lvl_check()
                battery_info_img.value = bat_lvl_val
                threadLock.release()
        else:
            while True:
                threadLock.acquire()
                thread_tester2()
                threadLock.release()
                time.sleep(1)


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
brake_sensor = DigitalInputDevice(18)

#volt_sens_pin = MCP3008(channel=0)
#curr_sens_pin = MCP3008(channel=1)
# ========================================= #

# ===============Variables================= #
is_cruise_on = False
magnet_count = 0
rpm_val = 0
mph_val = 0     # actual  speed
v_sensor_val = 99
i_sensor_val = 0
pwm_duty_cycle = 0
start_time = time.time()
end_time = 0
diameter = 26
cruise_set_spd = 5
cruise_lvl_val = cruise_off_img
bat_lvl_val = bat_lvl_5
bat_blink = False
# ========================================= #

# ==============Enables==================== #
bts_enable_pin.value = 0
# ========================================= #


# TODO: Display kill switch popup using wait_for_press on kill Button
def killBtn():
    global pwm_duty_cycle
    bts_enable_pin.value = 0
    pwm_duty_cycle = 0
    print(pwm_duty_cycle)
    pwm_out_pin.value = pwm_duty_cycle


def brakeBtn():
    global is_cruise_on, cruise_set_spd
    if is_cruise_on:
        is_cruise_on = False
        cruise_set_spd = 0
        set_spd.value = str(cruise_set_spd) + " mph"
        print('brake stopped cruise control')


# TODO: Ensure only 1 decimal place is printed
def incSpeedBtn():
    global cruise_set_spd
    if cruise_set_spd <= 6:
        cruise_set_spd = cruise_set_spd + 1
        set_spd.value = str(cruise_set_spd) + " mph"

# TODO: Ensure only 1 decimal place is printed
def decSpeedBtn():
    global cruise_set_spd
    if cruise_set_spd >= 4:
        cruise_set_spd = cruise_set_spd - 1
        set_spd.value = str(cruise_set_spd) + " mph"


def cruiseSetBtn():
    global cruise_set_spd, is_cruise_on, mph_val
    if is_cruise_on:
        cruise_set_spd = 0
        is_cruise_on = False
    else:
        if mph_val >= 3 or mph_val <= 7:    # if less than 3mph, can't activate
            cruise_set_spd = mph_val
            is_cruise_on = True


# TODO: In a worst case scenario, use this to measure other pins
def rpmCount():
    global magnet_count
    magnet_count = magnet_count + 1
    if magnet_count >= 2:
        updateRPM()


# TODO: Ensure only 1 decimal place is printed
def updateRPM():
    global end_time, rpm_val, start_time, mph_val, magnet_count
    end_time = time.time()
    rpm_val = ((magnet_count * 60) / end_time - start_time) / 2
    mph_val = ((diameter / 12) * 3.14 * rpm_val * 60) / 5280
    start_time = end_time
    magnet_count = 0
    cur_spd.value = str(mph_val)[0:3] + " mph"
    print("RPM: " + str(rpm_val) + "\nMPH: " + str(mph_val))


def control():
    global cruise_set_spd, mph_val, pwm_duty_cycle
    x = (cruise_set_spd - mph_val) * 2  # gain = 2(arbitrary), set val in RPM
    print(x)
    if x < 0:
        x = 0
    elif x > 12:
        x = 12
    pwm_duty_cycle = x / 12


def inc_pwm():
    global pwm_duty_cycle
    if pwm_duty_cycle < 1:
        bts_enable_pin.value = 1
        pwm_duty_cycle = pwm_duty_cycle + 0.05  # 0.05PWM = ~1.3V +- .1
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle


def dec_pwm():
    global pwm_duty_cycle
    if pwm_duty_cycle > 0:
        pwm_duty_cycle = pwm_duty_cycle - 0.05
        if pwm_duty_cycle < 0:
            pwm_duty_cycle = 0
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle


# TODO: Add voltage sensor input
# TODO: determine what voltage represents what percentage %
# TODO: Disable BTS Driver when battery is too low
def bat_lvl_check():
    global v_sensor_val, bat_lvl_val, bat_blink
    if v_sensor_val > 80:
        bat_lvl_val = bat_lvl_5
        bat_blink = False
    elif v_sensor_val > 60:
        bat_lvl_val = bat_lvl_4
        bat_blink = False
    elif v_sensor_val > 40:
        bat_lvl_val = bat_lvl_3
        bat_blink = False
    elif v_sensor_val > 20:
        bat_lvl_val = bat_lvl_2
        bat_blink = False
    elif v_sensor_val > 10:
        bat_lvl_val = bat_lvl_1
        bat_blink = False
    elif v_sensor_val > 0:
        bat_lvl_val = bat_lvl_1
        bat_blink = True
    else:
        # TODO: Present Out of Battery Popup at 0%
        # bat_lvl_val = bat_lvl_0
        # bat_blink = False
        print("out of battery")


def cruise_status_check():
    if is_cruise_on:
        cruise_info_img.value = cruise_on_img
    else:
        cruise_info_img.value = cruise_off_img


def thread_tester1():
    global cur_spd
    i = 0
    while True:
        i = i + 1
        cur_spd.value = str(i) + " mph"
        time.sleep(3)


def thread_tester2():
    global v_sensor_val
    v_sensor_val = v_sensor_val - 1
    print(v_sensor_val)
    # time.sleep(1)


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
battery_info_img = Picture(battery_info_box, image=bat_lvl_val, width=120,
                           height=60, align="right")
battery_info_text = Text(battery_info_box, text="Battery:", color="white", size=24, height=2)

set_spd_box = Box(app, width="fill", height="fill", align="left", border=True)
set_spd_txt_padding = Text(set_spd_box, text=" ", color="white", size=35, height=1, align='top')
set_spd_text = Text(set_spd_box, text="Set Speed", height=2, color="white", size=32)
set_spd = Text(set_spd_box, text=str(cruise_set_spd)+" mph", color="white", size=40)
# dec_btn_gui = PushButton(set_spd_box, text="Speed -", height=20, width=20, command=dec_pwm)
# dec_btn_gui.bg = "white"

cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(mph_val)+" mph", color="yellow", size=60)
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
# bat_lvl_check()
cruise_status_check()


threadLock = threading.Lock()
battery_thread = piThread(1, "battery")
test_thread = piThread(2, "test")
battery_thread.start()
test_thread.start()
app.display()

# TODO: Add watchdog timer to lower mph to 0 upon stopping


