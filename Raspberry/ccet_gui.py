import time
import threading
from guizero import App, Text, Box, Picture
from gpiozero import MCP3008, Button, PWMOutputDevice, DigitalOutputDevice, DigitalInputDevice


# ================Remote=================== #
import os
os.environ.__setitem__('DISPLAY', ':0.0')
# ================Control================== #


# Custom class for threads. Thread behavior is determined by their specified name.
# ============================================= #
class PiThread (threading.Thread):
    def __init__(self, thread_id, thread_name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_name = thread_name

    def run(self):
        if self.thread_name is "status":
            while True:
                if bat_blink:
                    battery_info_img.value = bat_lvl_1
                    time.sleep(1)
                    battery_info_img.value = bat_lvl_0
                    time.sleep(1)
                else:
                    time.sleep(1)
                threadLock.acquire()
                cruise_state_check()
                sys_voltage_check()
                bat_lvl_check()
                battery_info_img.value = bat_lvl_val
                threadLock.release()
        elif self.thread_name is "mph":
            # threadLock.acquire()
            thread_tester1()
            # threadLock.release()
        elif self.thread_name is "throttle":
            while True:
                adjust_throttle()
                time.sleep(0.1)
        else:
            while True:
                threadLock.acquire()
                thread_tester2()
                threadLock.release()
                time.sleep(0.2)
# ============================================= #


# ==================Files====================== #
bat_lvl_5 = "/home/pi/Documents/CCET/Battery/battery5.png"
bat_lvl_4 = "/home/pi/Documents/CCET/Battery/battery4.png"
bat_lvl_3 = "/home/pi/Documents/CCET/Battery/battery3.png"
bat_lvl_2 = "/home/pi/Documents/CCET/Battery/battery2.png"
bat_lvl_1 = "/home/pi/Documents/CCET/Battery/battery1.png"
bat_lvl_0 = "/home/pi/Documents/CCET/Battery/battery0.png"
cruise_on_img = '/home/pi/Documents/CCET/Cruise/CruiseON.png'
cruise_off_img = '/home/pi/Documents/CCET/Cruise/CruiseOFF.png'
# ============================================= #

# ================GPIO Pins================ #
btn_kill_pin = Button(6)
btn_inc_pin = Button(4)
btn_dec_pin = Button(5)
btn_set_pin = Button(25)

pwm_out_pin = PWMOutputDevice(13)
bts_enable_pin = DigitalOutputDevice(12)
hall_pin = DigitalInputDevice(17)
brake_sensor = DigitalInputDevice(18)

curr_sens_pin = MCP3008(channel=0, max_voltage=6)
volt_sens_pin = MCP3008(channel=1, max_voltage=6)
throttle_sens_pin = MCP3008(channel=2, max_voltage=6)
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
bts_enable_pin.value = 1
# ========================================= #


# TODO: Display kill switch popup using wait_for_press on kill Button
# TODO: Set enable back to 1 upon kill switch deactivation
# Kills the system in case of emergency. Shows popup warning until disengaged.
# Serviced by main thread via interrupts.
# ============================================= #
def kill_btn():
    global pwm_duty_cycle, bts_enable_pin, cruise_set_spd
    bts_enable_pin.value = 0
    pwm_duty_cycle = 0
    pwm_out_pin.value = pwm_duty_cycle
    cruise_set_spd = 0
    set_spd.value = str(cruise_set_spd) + " mph"
# ============================================= #


# Deactivates cruise control when braking if cruise is engaged.
# Serviced by main thread via interrupts
# ============================================= #
def brake_press():
    global is_cruise_on, cruise_set_spd, pwm_duty_cycle, pwm_out_pin, set_spd
    # if is_cruise_on:
    is_cruise_on = False
    cruise_set_spd = 0
    set_spd.value = str(cruise_set_spd) + " mph"
    pwm_duty_cycle = 0
    pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Increased set speed in steps of 1mph
# Serviced by main thread via interrupts
# ============================================= #
def inc_speed_btn():
    global cruise_set_spd
    if cruise_set_spd <= 6:
        cruise_set_spd = cruise_set_spd + 1
        set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Decreases set speed in steps of 1mph
# Serviced by main thread via interrupts
# ============================================= #
def dec_speed_btn():
    global cruise_set_spd
    if cruise_set_spd >= 4:
        cruise_set_spd = cruise_set_spd - 1
        set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Sets cruise speed equal to actual speed if actual speed is between 3mph and 7mph.
# If cruise speed was previously set, it will deactivate cruise control function
# Serviced by main thread via interrupts
# ============================================= #
def cruise_set_btn():
    global cruise_set_spd, is_cruise_on, mph_val
    if is_cruise_on:
        cruise_set_spd = 0
        is_cruise_on = False
    else:
        if mph_val >= 3 or mph_val <= 7:    # if less than 3mph, can't activate
            cruise_set_spd = mph_val
            is_cruise_on = True
# ============================================= #


# Detects triggering of the hall-effect sensor. Invokes update_rpm after 2 triggers.
# Serviced by main thread via interrupts.
# ============================================= #
def rpm_count():
    global magnet_count
    magnet_count = magnet_count + 1
    print(magnet_count)
    if magnet_count >= 2:
        update_rpm()
# ============================================= #


# Calculates RPM and MPH based on the time both magnets took to trigger the hall-effect sensor.
# Serviced by main thread via invocation.
# ============================================= #
def update_rpm():
    global end_time, rpm_val, start_time, mph_val, magnet_count
    end_time = time.time()
    rpm_val = ((magnet_count * 60) / (end_time - start_time)) / 2
    mph_val = ((diameter / 12) * 3.14 * rpm_val * 60) / 5280
    start_time = end_time
    magnet_count = 0
    cur_spd.value = "{x:.1f} mph".format(x=mph_val)
    # print("RPM: " + str(rpm_val) + "\nMPH: " + str(mph_val))
    # print("Start: {x}  End: {y}".format(x=start_time, y=end_time))
# ============================================= #


# TODO: Assign to a thread
# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by < >
# ============================================= #
def control():
    global cruise_set_spd, mph_val, pwm_duty_cycle
    x = (cruise_set_spd - mph_val) * 2  # gain = 2(arbitrary), set val in RPM
    print(x)
    if x < 0:
        x = 0
    elif x > 12:
        x = 12
    pwm_duty_cycle = x / 12
# ============================================= #


# TODO: Adjust percentage based on motor operation %
# Uses measured system voltage to adjust battery charge icon in GUI.
# Serviced by "status" thread.
# ============================================= #
def bat_lvl_check():
    global v_sensor_val, bat_lvl_val, bat_blink
    if (v_sensor_val/25) * 100 > 80:
        bat_lvl_val = bat_lvl_5
        bat_blink = False
    elif (v_sensor_val/25) * 100 > 60:
        bat_lvl_val = bat_lvl_4
        bat_blink = False
    elif (v_sensor_val/25) * 100 > 40:
        bat_lvl_val = bat_lvl_3
        bat_blink = False
    elif (v_sensor_val/25) * 100 > 20:
        bat_lvl_val = bat_lvl_2
        bat_blink = False
    elif (v_sensor_val/25) * 100 > 10:
        bat_lvl_val = bat_lvl_1
        bat_blink = False
    elif (v_sensor_val/25) * 100 > 0:
        bat_lvl_val = bat_lvl_1
        bat_blink = True
    else:
        # TODO: Determine if charger is connected to automatically close popup
        # bat_lvl_val = bat_lvl_0
        # bat_blink = False
        # bts_enable_pin.value = 0
        app.warn(title="Warning", text="Low Battery. Please connect to charger.")
# ============================================= #


# Verifies state of cruise control to update GUI.
# Serviced by "status" thread.
# ============================================= #
def cruise_state_check():
    if is_cruise_on:
        cruise_info_img.value = cruise_on_img
    else:
        cruise_info_img.value = cruise_off_img
# ============================================= #


# Measures system voltage (which translates to battery charge).
# Serviced by "status" thread.
# ============================================= #
def sys_voltage_check():
    global v_sensor_val
    v_sensor_val = volt_sens_pin.value * 6 * 5  # +-1%
# ============================================= #


# ============================================= #
def thread_tester1():
    global volt_sens_pin, v_sensor_val, throttle_sens_pin
    while True:
        time.sleep(10)
        # cur_spd.value = "{x:.2f} V".format(x=throttle_sens_pin.value)  # * V(ref) * Conversion
        # time.sleep(0.2)
# ============================================= #


# ============================================= #
def thread_tester2():
    global v_sensor_val
    # v_sensor_val = v_sensor_val - 1
    # print(v_sensor_val)
    # time.sleep(1)
# ============================================= #


# Increases PWM in controlled steps. Used for testing purposes.
# Serviced by main thread via interrupts.
# ============================================= #
def inc_pwm():
    global pwm_duty_cycle
    if pwm_duty_cycle < 1:
        bts_enable_pin.value = 1
        pwm_duty_cycle = pwm_duty_cycle + 0.05  # 0.05PWM = ~1.3V +- .1
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Decreases PWM in controlled steps. Used for testing purposes.
# Serviced by main thread via interrupts.
# ============================================= #
def dec_pwm():
    global pwm_duty_cycle
    if pwm_duty_cycle > 0:
        pwm_duty_cycle = pwm_duty_cycle - 0.05
        if pwm_duty_cycle < 0:
            pwm_duty_cycle = 0
        print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Verifies throttle inputs and adjust driver output accordingly.
# Serviced by "throttle" thread.
# ============================================= #
def adjust_throttle():
    global throttle_sens_pin, pwm_duty_cycle, is_cruise_on
    if not is_cruise_on:
        pwm_duty_cycle = (throttle_sens_pin.value - 0.15) * 1.96
        if pwm_duty_cycle <= 0:
            pwm_duty_cycle = 0
        elif pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        # cur_spd.value = "{x:.2f} PWM".format(x=pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
    else:
        is_cruise_on = False
# ============================================= #


# ===================GUI===================== #
app = App(title="Cruise Control Exhibition Tricycle", bg="#363636")

# noinspection PyTypeChecker
header_box = Box(app, width="fill", align="top", border=False)
header_text = Text(header_box, text="Cruise Control Exhibition Tricycle", color="white", height=2, size=24)
# emergency_btn_gui = PushButton(header_box, text="Emergency Stop", height=20, width=500, command=brake_press)
# emergency_btn_gui.bg = "red"

# noinspection PyTypeChecker
info_box = Box(app, width="fill", align="bottom", border=False)

# noinspection PyTypeChecker
cruise_info_box = Box(info_box, height="fill", width="fill", align="left", border=False)
cruise_info_img_padding = Text(cruise_info_box, text="    ", color="white", size=24, height=2, align='right')
cruise_info_img = Picture(cruise_info_box, image=cruise_lvl_val, width=70,
                          height=70, align="right")
cruise_info_text = Text(cruise_info_box, text="Cruise Control:", color="white", size=24, height=2)

# noinspection PyTypeChecker
battery_info_box = Box(info_box, height="fill", width="fill", align="right", border=False)
battery_info_img_padding = Text(battery_info_box, text=" ", color="white", size=24, height=2, align='right')
battery_info_img = Picture(battery_info_box, image=bat_lvl_val, width=120,
                           height=60, align="right")
battery_info_text = Text(battery_info_box, text="Battery:", color="white", size=24, height=2)

# noinspection PyTypeChecker
set_spd_box = Box(app, width="fill", height="fill", align="left", border=True)
set_spd_txt_padding = Text(set_spd_box, text=" ", color="white", size=35, height=1, align='top')
set_spd_text = Text(set_spd_box, text="Set Speed", height=2, color="white", size=32)
set_spd = Text(set_spd_box, text=str(cruise_set_spd)+" mph", color="white", size=40)
# dec_btn_gui = PushButton(set_spd_box, text="Speed -", height=20, width=20, command=dec_pwm)
# dec_btn_gui.bg = "white"

# noinspection PyTypeChecker
cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(mph_val)+" mph", color="yellow", size=60)
# inc_btn_gui = PushButton(cur_spd_box, text="Speed +", height=20, width=20, command=inc_pwm)
# inc_btn_gui.bg = "white"

app.set_full_screen()
# =========================================== #

# ================Manage Threads============= #
threadLock = threading.Lock()
mph_threadLock = threading.Lock()
battery_thread = PiThread(1, "status")
mph_thread = PiThread(2, "mph")
test_thread = PiThread(3, "test")
throttle_thread = PiThread(4, "throttle")

throttle_thread.start()
battery_thread.start()
mph_thread.start()
test_thread.start()
# =========================================== #

# =================Interrupts============== #
btn_inc_pin.wait_for_press = inc_speed_btn
btn_dec_pin.when_pressed = dec_speed_btn
btn_set_pin.when_pressed = cruise_set_btn
btn_kill_pin.when_pressed = kill_btn
hall_pin.when_activated = rpm_count
brake_sensor.when_deactivated = brake_press
# ========================================= #

app.display()

# TODO: Add watchdog timer to lower mph to 0 upon stopping
# TODO: Change "0mph" on set speed to "None" when cruise control is OFF
