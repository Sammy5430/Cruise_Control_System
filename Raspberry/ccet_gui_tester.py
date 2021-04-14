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
                if not system_stop:
                    if bat_blink:
                        battery_info_img.value = bat_lvl_1
                        time.sleep(1)
                        battery_info_img.value = bat_lvl_0
                        time.sleep(1)
                    else:
                        time.sleep(1)
                    # threadLock.acquire()
                    cruise_state_check()
                    sys_voltage_check()
                    sys_current_check()
                    bat_lvl_check()
                    battery_info_img.value = bat_lvl_val
                    # print(rpm_val)
                    # for testing

                    # threadLock.release()
        elif self.thread_name is "mph":
            global pwm_duty_cycle, begin_test
            while True:
                if begin_test:
                    # time.sleep(5)
                    # i = 0
                    # while i < 3:
                    #     pwm_duty_cycle = pwm_duty_cycle + 0.3
                    #     if pwm_duty_cycle > 1:
                    #         pwm_duty_cycle = 1
                    #     pwm_out_pin.value = pwm_duty_cycle
                    #     time.sleep(5)
                    #     i = i+1
                    # while i < 6:
                    #     pwm_duty_cycle = pwm_duty_cycle - 0.3
                    #     if pwm_duty_cycle < 0:
                    #         pwm_duty_cycle = 0
                    #     pwm_out_pin.value = pwm_duty_cycle
                    #     time.sleep(5)
                    #     i = i+1
                    # bts_enable_pin.value = 0
                    # begin_test = False
                    print("Starting Test")
                    pwm_duty_cycle = 0
                    pwm_out_pin.value = pwm_duty_cycle
                    time.sleep(1)
                    pwm_duty_cycle = 0.45
                    pwm_out_pin.value = pwm_duty_cycle
                    time.sleep(49)
                    # pwm_duty_cycle = 0.8
                    # pwm_out_pin.value = pwm_duty_cycle
                    # time.sleep(15)
                    begin_test = False
                    bts_enable_pin.value = 0
                    pwm_duty_cycle = 0
                    print("Ending Test")

        elif self.thread_name is "throttle":
            while True:
                if not system_stop:
                    adjust_throttle()
                    time.sleep(0.1)
        elif self.thread_name is "control":
            while True:
                if not system_stop:
                    control()
                    # time.sleep(1)
        elif self.thread_name is "test":
            f = open("/home/pi/Documents/CCET/test_records_4_11_2021(11).csv", 'w')
            f.write("Begin Test\nTime(s),RPM\n")
            f.close()
            test_start = time.time()

            while True:
                if begin_test:
                    f = open("/home/pi/Documents/CCET/test_records_4_11_2021(11).csv", 'a')
                    f.write("{x:.3f}, {y:.3f}\n".format(x=time.time()-test_start,
                                                        y=rpm_val))
                    f.close()
                    time.sleep(0.01)
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
btn_kill_pin = DigitalInputDevice(21)
btn_inc_pin = Button(4)
btn_dec_pin = Button(5)
btn_set_pin = Button(25)

pwm_out_pin = PWMOutputDevice(13)
bts_enable_pin = DigitalOutputDevice(12)
hall_pin = DigitalInputDevice(17)
brake_sensor = DigitalInputDevice(18)
is_throttle_active_pin = DigitalInputDevice(26)

curr_sens_pin = MCP3008(channel=0, max_voltage=6)
volt_sens_pin = MCP3008(channel=1, max_voltage=6)
throttle_sens_pin = MCP3008(channel=2, max_voltage=6)
motor_volt_sens_pin = MCP3008(channel=3, max_voltage=6)  # used for testing
# ========================================= #

# ===============Variables================= #
is_cruise_on = False            # flag for cruise on/off
magnet_count = 0                # times magnet has passed hall sensor
rpm_val = 0                     # actual RPM
prev_rpm_val = 0                # previous RPM
mph_val = 0                     # actual speed
v_sensor_val = 25.0             #
mv_sensor_val = 0
i_sensor_val = 0
pwm_duty_cycle = 0
start_time = time.time()
end_time = 0
diameter = 26
cruise_set_spd = 0
cruise_lvl_val = cruise_off_img
bat_lvl_val = bat_lvl_5
bat_blink = False
system_stop = False

begin_test = False
prev_pwm = 0                    # used as a hold for control equation
# ========================================= #

# ==============Enables==================== #
bts_enable_pin.value = 0           # start at 0 for testing purposes
# ========================================= #


# Verifies throttle inputs and adjust driver output accordingly.
# Serviced by "throttle" thread.
# ============================================= #
def adjust_throttle():
    global throttle_sens_pin, pwm_duty_cycle, is_cruise_on
    if not is_cruise_on:
        if is_throttle_active_pin:
            bts_enable_pin.value = 1
        else:
            bts_enable_pin.value = 0
        pwm_duty_cycle = (throttle_sens_pin.value - 0.15) * 1.96
        if pwm_duty_cycle <= 0:
            pwm_duty_cycle = 0
        elif pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        # print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
        reduce_to_zero()
# ============================================= #


# Uses measured system voltage to adjust battery charge icon in GUI.
# Serviced by "status" thread.
# ============================================= #
def bat_lvl_check():
    global v_sensor_val, bat_lvl_val, bat_blink
    # 25.5V will be considered a system battery of 100%
    # 23.16V will be considered a system battery of 0%
    # (Vmeasured - Vmin) / (Vmax - Vmin)
    if ((v_sensor_val - 23.16)/2.34) * 100 > 80:
        bat_lvl_val = bat_lvl_5
        bat_blink = False
    elif ((v_sensor_val - 23.16)/2.24) * 100 > 60:
        bat_lvl_val = bat_lvl_4
        bat_blink = False
    elif ((v_sensor_val - 23.16)/2.24) * 100 > 40:
        bat_lvl_val = bat_lvl_3
        bat_blink = False
    elif ((v_sensor_val - 23.16)/2.24) * 100 > 20:
        bat_lvl_val = bat_lvl_2
        bat_blink = False
    elif ((v_sensor_val - 23.16)/2.24) * 100 > 10:
        bat_lvl_val = bat_lvl_1
        bat_blink = False
    elif ((v_sensor_val - 23.16)/2.24) * 100 > 0:
        bat_lvl_val = bat_lvl_1
        bat_blink = True
    else:
        # print("low battery")
        bat_lvl_val = bat_lvl_0
        bat_blink = False
        bts_enable_pin.value = 0
        app.warn(title="Warning", text="Low Battery. Please connect to charger.")
# ============================================= #


# Deactivates cruise control when braking if cruise is engaged.
# Serviced by main thread via interrupts
# ============================================= #
def brake_press():
    global is_cruise_on
    if is_cruise_on:
        stop_cruise()
# ============================================= #


# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by control thread
# ============================================= #
def control():
    global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm
    if is_cruise_on:
        prev_pwm = pwm_duty_cycle
        if not bts_enable_pin.value:
            bts_enable_pin.value = 1
        x = ((cruise_set_spd - mph_val) * 2)   # gain = 2(arbitrary), set val in RPM
        if x < 0:
            x = 0
            # bts_enable_pin.value = 0
        elif x > 24:
            x = 24
        # if x/24 > prev_pwm + 0.05 or x/24 < prev_pwm - 0.05:
        #     pwm_out_pin.value = prev_pwm
        #     time.sleep(0.2)     # Varies according to system sample time
        # else:
        pwm_duty_cycle = (x / 24)+(cruise_set_spd/10)
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        pwm_out_pin.value = pwm_duty_cycle
        # print("Control PWM => {x:.2f}".format(x=pwm_duty_cycle))
            # prev_pwm = pwm_duty_cycle
        # time.sleep(0.2)     # Varies according to system sample time
# ============================================= #


# Sets cruise speed equal to actual speed if actual speed is between 3mph and 7mph.
# If cruise speed was previously set, it will deactivate cruise control function
# Serviced by main thread via interrupts
# ============================================= #
def cruise_set_btn():
    global cruise_set_spd, is_cruise_on, mph_val, bts_enable_pin, begin_test, pwm_duty_cycle
    # TESTING CODE
    if begin_test:
        begin_test = False
        bts_enable_pin.value = 0
        pwm_duty_cycle = 0
    else:
        bts_enable_pin.value = 1
        begin_test = True
        pwm_duty_cycle = 0.0
        pwm_out_pin.value = pwm_duty_cycle
        test_thread.start()

    # correct method implementation
    # if is_cruise_on:
    #     stop_cruise()
    # else:
    #     if mph_val >= 3 or mph_val <= 7:    # if less than 3mph, can't activate
    #         cruise_set_spd = mph_val
    #         set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
    #         # print("Speed was set. Initial PWM => {x:.2f}".format(x=pwm_duty_cycle))
    #         is_cruise_on = True
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


# Decreases set speed in steps of 1mph
# Serviced by main thread via interrupts
# ============================================= #
def dec_speed_btn():
    global cruise_set_spd
    if cruise_set_spd > 3:
        cruise_set_spd = cruise_set_spd - 1
        if cruise_set_spd < 3:
            cruise_set_spd = 3
        set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Increased set speed in steps of 1mph
# Serviced by main thread via interrupts
# ============================================= #
def inc_speed_btn():
    global cruise_set_spd
    if cruise_set_spd < 7:
        cruise_set_spd = cruise_set_spd + 1
        if cruise_set_spd > 7:
            cruise_set_spd = 7
        set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Kills the system in case of emergency. Shows popup warning until disengaged.
# Serviced by main thread via interrupts.
# ============================================= #
def kill_btn():
    global pwm_duty_cycle, bts_enable_pin, cruise_set_spd, system_stop
    stop_cruise()
    system_stop = True
    print("murio")
    btn_kill_pin.wait_for_inactive()
    print("revivio")
    system_stop = False
    # popup
# ============================================= #


# Decreases PWM in controlled steps. Used for testing purposes.
# Serviced by main thread via interrupts.
# ============================================= #
def pwm_dec():
    global pwm_duty_cycle
    if pwm_duty_cycle > 0:
        pwm_duty_cycle = pwm_duty_cycle - 0.05
        if pwm_duty_cycle < 0:
            pwm_duty_cycle = 0
        # print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Increases PWM in controlled steps. Used for testing purposes.
# Serviced by main thread via interrupts.
# ============================================= #
def pwm_inc():
    global pwm_duty_cycle
    if pwm_duty_cycle < 1:
        bts_enable_pin.value = 1
        pwm_duty_cycle = pwm_duty_cycle + 0.05  # 0.05PWM = ~1.3V +- .1
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        # print(pwm_duty_cycle)
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


def reduce_to_zero():
    # None
    global throttle_sens_pin, mph_val, start_time, end_time
    # print(time.time()-start_time)
    if time.time()-start_time > 1:
        while mph_val > 0:
            if is_throttle_active_pin.value:
                break
            decrement = mph_val * 0.1  # (1/mph_val+0.01)
            mph_val = mph_val - decrement
            if mph_val < 0:
                mph_val = 0
            cur_spd.value = "{x:.1f} mph".format(x=mph_val)
            time.sleep(0.15)


# Detects triggering of the hall-effect sensor. Invokes update_rpm after 2 triggers.
# Serviced by main thread via interrupts.
# ============================================= #
def rpm_count():
    global magnet_count
    magnet_count = magnet_count + 1
    # if magnet_count >= 2:
    if magnet_count >= 1:
        update_rpm()
# ============================================= #


# Auxiliary method to stop cruise functionality
# ============================================= #
def stop_cruise():
    global is_cruise_on, cruise_set_spd, pwm_duty_cycle, pwm_out_pin, set_spd
    is_cruise_on = False
    cruise_set_spd = 0
    set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
    bts_enable_pin.value = 0
    pwm_duty_cycle = 0
    pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Measures system current (which is used on the webpage graph).
# Serviced by "status" thread.

# ============================================= #
def sys_current_check():
    global i_sensor_val
    i_sensor_val = (curr_sens_pin.value * 6) / 66
    # print("System Current: {x:.4f}A".format(x=i_sensor_val))
# ============================================= #


# Measures system voltage (which translates to battery charge).
# Serviced by "status" thread.
# ============================================= #
def sys_voltage_check():
    global v_sensor_val, motor_volt_sens_pin
    v_sensor_val = volt_sens_pin.value * 6 * 5  # +-1%
    mv_sensor_val = motor_volt_sens_pin.value * 6 * 5
    print("Battery Voltage: {x:.1f}V".format(x=v_sensor_val))
    # print("Motor Voltage: {y:.2f}V".format(y=mv_sensor_val))
# ============================================= #


# Calculates RPM and MPH based on the time both magnets took to trigger the hall-effect sensor.
# Serviced by main thread via invocation.
# ============================================= #
def update_rpm():
    global end_time, rpm_val, start_time, mph_val, magnet_count, prev_rpm_val
    end_time = time.time()
    rpm_val = ((magnet_count * 60) / (end_time - start_time)) / 9
    # rpm_val = ((magnet_count * 60) / (end_time - start_time)) / 2
    rpm_val = (rpm_val + prev_rpm_val) / 2
    prev_rpm_val = rpm_val
    mph_val = ((diameter / 12) * 3.14 * rpm_val * 60) / 5280
    start_time = end_time
    magnet_count = 0
    cur_spd.value = "{x:.1f} mph".format(x=mph_val)
    # print("RPM: " + str(rpm_val))
    # print("RPM: " + str(rpm_val) + "\nMPH: " + str(mph_val))
    # print("Start: {x}  End: {y}".format(x=start_time, y=end_time))
# ============================================= #


# ============================================= #
def thread_tester2():
    global v_sensor_val
    # v_sensor_val = v_sensor_val - 1
    # print(v_sensor_val)
    # time.sleep(1)
# ============================================= #


# ===================GUI===================== #
app = App(title="Cruise Control Exhibition Tricycle", bg="#363636")

header_box = Box(app, width="fill", align="top", border=False)
header_text = Text(header_box, text="Cruise Control Exhibition Tricycle", color="white", height=2, size=24)
# emergency_btn_gui = PushButton(header_box, text="Emergency Stop", height=20, width=500, command=brake_press)
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
# dec_btn_gui = PushButton(set_spd_box, text="Speed -", height=20, width=20, command=pwm_dec)
# dec_btn_gui.bg = "white"

cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(mph_val)+" mph", color="yellow", size=60)
# inc_btn_gui = PushButton(cur_spd_box, text="Speed +", height=20, width=20, command=pwm_inc)
# inc_btn_gui.bg = "white"

app.set_full_screen()
# =========================================== #

# ================Manage Threads============= #
threadLock = threading.Lock()
status_thread = PiThread(1, "status")
control_thread = PiThread(2, "control")
mph_thread = PiThread(3, "mph")
throttle_thread = PiThread(4, "throttle")
test_thread = PiThread(5, "test")

# throttle_thread.start()
status_thread.start()
# control_thread.start()
mph_thread.start()
# =========================================== #

# =================Interrupts============== #
# btn_inc_pin.when_pressed = inc_speed_btn
btn_inc_pin.when_pressed = pwm_inc
# btn_dec_pin.when_pressed = dec_speed_btn
btn_dec_pin.when_pressed = pwm_dec
btn_set_pin.when_pressed = cruise_set_btn
btn_kill_pin.when_activated = kill_btn
hall_pin.when_activated = rpm_count
brake_sensor.when_deactivated = brake_press
# ========================================= #

app.display()

