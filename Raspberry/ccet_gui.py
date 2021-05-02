import time
import threading
import socketio
# import keyboard
from guizero import App, Text, Box, Picture, Window
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
                        time.sleep(0.25)
                        battery_info_img.value = bat_lvl_0
                        time.sleep(0.25)
                    else:
                        time.sleep(0.5)
                    cruise_state_check()
                    sys_voltage_check()
                    sys_current_check()
                    bat_lvl_check()
                    mph_display()

        elif self.thread_name is "comms":
            sio = socketio.Client(reconnection=True, reconnection_attempts=0)
            sio.connect("http://ccet.ece.uprm.edu")
            t = 0
            while True:
                if not low_battery:
                    sio.emit('data_update', {
                        'Battery': bat_pct,
                        'Cruise State': is_cruise_on,
                        'Set Speed': cruise_set_spd,
                        'Actual Speed': mph_val,
                        'Current': i_sensor_val,
                        'Time': t
                    })
                    time.sleep(0.5)
                    t = t+0.5
                else:
                    t = 0
                    sio.emit('data_update', {
                        'Battery': 0,
                        'Cruise State': False,
                        'Set Speed': 0.0,
                        'Actual Speed': 0.0,
                        'Current': 0,
                        'Time': t
                    })

        elif self.thread_name is "throttle":
            while True:
                if not system_stop:
                    adjust_throttle()
                    time.sleep(0.1)

        elif self.thread_name is "control":
            while True:
                if not system_stop:
                    if controller is 'dynamic':
                        pi_control()
                    else:
                        pi_control_static()
                    time.sleep(0.01)
# ============================================= #


# ==================Files====================== #
bat_lvl_5 = "/home/pi/Documents/CCET/Battery/battery5.png"
bat_lvl_4 = "/home/pi/Documents/CCET/Battery/battery4.png"
bat_lvl_3 = "/home/pi/Documents/CCET/Battery/battery3.png"
bat_lvl_2 = "/home/pi/Documents/CCET/Battery/battery2.png"
bat_lvl_1 = "/home/pi/Documents/CCET/Battery/battery1.png"
bat_lvl_0 = "/home/pi/Documents/CCET/Battery/battery0.png"
bat_low_img = "/home/pi/Documents/CCET/Battery/low_battery.png"
cruise_on_img = '/home/pi/Documents/CCET/Cruise/CruiseON.png'
cruise_off_img = '/home/pi/Documents/CCET/Cruise/CruiseOFF.png'
logo_img = '/home/pi/Documents/CCET/Cruise/Favicon.png'
control_static_img = '/home/pi/Documents/CCET/Controller/static_mode.png'
control_dynamic_img = '/home/pi/Documents/CCET/Controller/dynamic_mode.png'
warning_img = '/home/pi/Documents/CCET/Cruise/Warning.png'
# ============================================= #

# ================GPIO Pins================ #
btn_kill_pin = DigitalInputDevice(6)
btn_inc_pin = Button(4)
btn_dec_pin = Button(5)
btn_set_pin = Button(25)

pwm_out_pin = PWMOutputDevice(13)
pwm_rev_out_pin = PWMOutputDevice(19)
bts_enable_pin = DigitalOutputDevice(12)
hall_pin = DigitalInputDevice(17)
brake_sensor = DigitalInputDevice(18)
ctrl_toggle_pin = DigitalInputDevice(26)

# ADC Pins
curr_sens_pin = MCP3008(channel=0, max_voltage=6)
volt_sens_pin = MCP3008(channel=1, max_voltage=6)
throttle_sens_pin = MCP3008(channel=2, max_voltage=6)
# ========================================= #

# ===============Variables================= #
is_cruise_on = False                        # flag for cruise on/off
magnet_count = 0                            # times magnet has passed hall sensor
THROTTLE_DEADBAND = (1/6)                   # sets the throttle to start reading after 1 Volts
CURR_SENS_SENSITIVITY = 0.066               # Current sensor sensitivity
rpm_val = 0.0                               # latest RPM measurement
prev_rpm_val = 0.0                          # previous RPM measurement(used for average measurements)
mph_val = 0.0                               # actual speed
v_sensor_val = 25                           # value from voltage sensor after conversion
i_sensor_val = 0                            # value from the current sensor after conversion
pwm_duty_cycle = 0                          # stores set value for PWM (ranges from 0 to 1)
start_time = time.time()                    # start time for a fraction of a wheel spin. Used for RPM calculations
end_time = 0                                # end time for a fraction of a wheel spin. Used for RPM calculations
DIAMETER = 26                               # diameter of the system's wheel. Used for RPM-to-MPH conversion
cruise_set_spd = 0.0                        # speed set by the user for cruising. Expressed in mph
cruise_set_rpm = 0.0                        # speed set by the user for cruising. Expressed in rpm
cruise_lvl_val = cruise_off_img             # used by the GUI to present whether cruise is on or off
bat_pct = 100                               # battery percentage based on voltage readings. Used for battery indicator
bat_lvl_val = bat_lvl_5                     # used by the GUI to present the battery charge level
control_img = control_static_img            # used by the GUI to present the type of controller being
bat_blink = False                           # flag for the GUI to blink the battery level indicator on low battery
system_stop = False                         # flag for the kill switch to halt system execution
prev_pwm = 0                                # used as a hold for control equation
control_err = 0                             # difference between set speed and actual speed. Measured currently
prev_control_err = 0                        # difference between set speed and actual speed. Previous measurement
control_act = 0                             # determined output for the controller. Measured currently
prev_control_act = 0                        # determined output for the controller. Previous measurement
CONTROL_GAIN = 0.15078                      # dynamic controller gain.
CONTROL_ZERO = 0.991                        # dynamic controller zero.
CONTROL_GAIN_STATIC = 0.04027               # static controller gain.
CONTROL_ZERO_STATIC = 0.902                 # static controller zero.
bat_measure_sum = 0                         # sum of battery measurements. Used to average battery measurements
bat_measure_cnt = 0                         # count of battery measurements. Used to average battery measurements
THROTTLE_SENS_MIN = 0.9                     # minimum value for throttle sensor. Interpreted as absolute zero throttle
THROTTLE_SENS_MAX = 4                       # maximum value for throttle sensor
REF_V_ADC = 6                               # reference voltage used for the analog-to-digital converter
THROTTLE_CONVERSION = (1/((THROTTLE_SENS_MAX-THROTTLE_SENS_MIN)/REF_V_ADC))  # conversion factor from ADC to PWM
NUM_MAGNETS = 10                            # Amount on magnets on the wheel. Used to calculate RPM
controller = 'static'                       # type of controller used. Should be either 'static' or 'dynamic'
low_battery = False
pwm_rev_out_pin.value = 0
# ========================================= #

# ==============Enables==================== #
bts_enable_pin.value = 0
# ========================================= #


# Verifies throttle inputs and adjust driver output accordingly.
# Serviced by "throttle" thread.
# Sets the throttle deadband depending on the actual speed to prevent motor stopping the momentum of the tricycle
# PWM/ADC Ratio = (throttle_sens_pin.value - Throttle_min) * (1/((Throttle_max/Vref_ADC)-Throttle_min))
# ============================================= #
def adjust_throttle():
    global throttle_sens_pin, pwm_duty_cycle, is_cruise_on, prev_pwm
    if not is_cruise_on:
        # if throttle_sens_pin.value > 0.13:
        print(throttle_sens_pin.value)
        if throttle_sens_pin.value > 0.16:
            bts_enable_pin.value = 1
        else:
            bts_enable_pin.value = 0
        prev_pwm = pwm_duty_cycle
        pwm_duty_cycle = (throttle_sens_pin.value - 0.16) * 1.974
        if (mph_val/10) - pwm_duty_cycle > 0.2:
            pwm_duty_cycle = pwm_duty_cycle + (mph_val/10)
        if pwm_duty_cycle <= 0:
            pwm_duty_cycle = 0
        elif pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        pwm_out_pin.value = pwm_duty_cycle
        # print(pwm_duty_cycle)
    reduce_to_zero()
# ============================================= #


# Uses measured system voltage to adjust battery charge icon in GUI.
# 25.4V will be considered a system battery of 100%
# 23.16V will be considered a system battery of 0%
# Serviced by "status" thread.
# ============================================= #
def bat_lvl_check():
    global v_sensor_val, bat_lvl_val, bat_blink, bat_pct, system_stop, bts_enable_pin, low_battery
    # bat_pct = ((v_sensor_val - 23.16)/2.24) * 100   # (Vmeasured - Vmin) / (Vmax - Vmin)
    bat_pct = 100
    if bat_pct > 80:
        bat_lvl_val = bat_lvl_5
        bat_blink = False
    elif bat_pct > 60:
        bat_lvl_val = bat_lvl_4
        bat_blink = False
    elif bat_pct > 40:
        bat_lvl_val = bat_lvl_3
        bat_blink = False
    elif bat_pct > 20:
        bat_lvl_val = bat_lvl_2
        bat_blink = False
    elif bat_pct > 10:
        bat_lvl_val = bat_lvl_1
        bat_blink = False
    elif bat_pct > 0:
        bat_lvl_val = bat_lvl_1
        bat_blink = True
    else:
        bat_lvl_val = bat_lvl_0
        battery_info_img.value = bat_lvl_val
        bat_blink = False
        system_stop = True
        warning_icon.value = bat_low_img
        warning_icon.width = 120
        warning_text.value = "Low Battery"
        window.show()
        window.focus()
        stop_cruise()
        low_battery = True
    battery_info_img.value = bat_lvl_val
# ============================================= #


# TODO: Ensure brake_sensor.when_deactivated interrupt trigger
# Deactivates cruise control when braking if cruise is engaged.
# Serviced by main thread via interrupts
# ============================================= #
def brake_press():
    global is_cruise_on, bts_enable_pin
    if is_cruise_on:
        stop_cruise()
# ============================================= #


# Verifies button state to determine controller to use
# Serviced by main thread via interrupts
# ============================================= #
def check_controller():
    global controller, control_info_img, control_img, control_dynamic_img, control_static_img
    # if btn_kill_pin.value:
    if mph_val < 0.1:
        if ctrl_toggle_pin.value:
            controller = 'dynamic'
            print('dynamic controller selected')
            control_img = control_dynamic_img
        else:
            controller = 'static'
            print('static controller selected')
            control_img = control_static_img
        control_info_img.value = control_img
# ============================================= #


# Proportional Integral Controller implementation.
# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by "control" thread
# ============================================= #
def pi_control():
    global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm, control_err, control_act,\
        prev_control_act, prev_control_err, cruise_set_rpm, rpm_val
    if is_cruise_on:
        prev_pwm = pwm_duty_cycle
        if not bts_enable_pin.value:
            bts_enable_pin.value = 1
        control_err = cruise_set_rpm - rpm_val
        control_act = (control_err * CONTROL_GAIN) - (prev_control_err * CONTROL_GAIN *
                                                      CONTROL_ZERO) + prev_control_act
        if control_act < 0:
            control_act = 0
        elif control_act > 24:
            control_act = 24
        pwm_duty_cycle = (control_act/24)
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        prev_control_err = control_err
        prev_control_act = control_act
        pwm_out_pin.value = pwm_duty_cycle
    else:
        prev_control_err = rpm_val
        prev_control_act = prev_pwm * 24
# ============================================= #


# Proportional Integral Controller implementation for static demonstrations.
# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by "control" thread
# ============================================= #
def pi_control_static():
    global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm, control_err, control_act,\
        prev_control_act, prev_control_err, cruise_set_rpm
    if is_cruise_on:
        prev_pwm = pwm_duty_cycle
        if not bts_enable_pin.value:
            bts_enable_pin.value = 1
        control_err = cruise_set_rpm - rpm_val
        control_act = (control_err * CONTROL_GAIN_STATIC) - (prev_control_err * CONTROL_GAIN_STATIC *
                                                             CONTROL_ZERO_STATIC) + prev_control_act
        if control_act < 0:
            control_act = 0
        elif control_act > 24:
            control_act = 24
        pwm_duty_cycle = (control_act/24)
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        prev_control_err = control_err
        prev_control_act = control_act
        pwm_out_pin.value = pwm_duty_cycle
    else:
        prev_control_err = rpm_val
        prev_control_act = prev_pwm * 24
# ============================================= #


# Proportional Controller implementation.
# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by "control" thread
# ============================================= #
def p_control():
    global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm
    if is_cruise_on:
        prev_pwm = pwm_duty_cycle
        if not bts_enable_pin.value:
            bts_enable_pin.value = 1
        # x = ((cruise_set_spd - mph_val) * 2)   # gain = 2(arbitrary), set val in RPM
        x = ((cruise_set_spd-mph_val)/9.54929) * 2.5
        x = x * 5280 * (12/DIAMETER) * (1/3.14) * (1/60)
        if x < 0:
            x = 0
            # bts_enable_pin.value = 0
        elif x > 24:
            x = 24
        pwm_duty_cycle = (x / 24)  # + (cruise_set_spd/10)
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Sets cruise speed equal to actual speed if actual speed is between 3mph and 7mph.
# If cruise speed was previously set, it will deactivate cruise control function
# Serviced by main thread via interrupts
# ============================================= #
def cruise_set_btn():
    global cruise_set_spd, is_cruise_on, mph_val, cruise_set_rpm
    if is_cruise_on:
        stop_cruise()
    else:
        if 3 <= mph_val <= 7:    # if less than 3mph, can't activate
            is_cruise_on = True
            cruise_set_spd = mph_val
            cruise_set_rpm = rpm_val
            set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
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
    global cruise_set_spd, is_cruise_on, cruise_set_rpm
    if is_cruise_on:
        if cruise_set_spd > 3:
            cruise_set_spd = cruise_set_spd - 1
            cruise_set_rpm = cruise_set_rpm - 12.93
            if cruise_set_spd < 3:
                cruise_set_spd = 3
            if cruise_set_rpm < 38.8:
                cruise_set_rpm = 38.8
            set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Increased set speed in steps of 1mph
# Serviced by main thread via interrupts
# ============================================= #
def inc_speed_btn():
    global cruise_set_spd, is_cruise_on, cruise_set_rpm
    if is_cruise_on:
        if cruise_set_spd < 7:
            cruise_set_spd = cruise_set_spd + 1
            cruise_set_rpm = cruise_set_rpm + 12.93
            if cruise_set_spd > 7:
                cruise_set_spd = 7
            if cruise_set_rpm > 90.5:
                cruise_set_rpm = 90.5
            set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
# ============================================= #


# Kills the system in case of emergency. Shows popup warning until disengaged.
# Serviced by main thread via interrupts.
# ============================================= #
def kill_btn():
    global pwm_duty_cycle, cruise_set_spd, system_stop, app, mph_val, rpm_val, window
    stop_cruise()
    system_stop = True
    mph_val = 0.0
    rpm_val = 0.0
    mph_display()
    bts_enable_pin.value = 1
    warning_icon.value = warning_img
    warning_icon.width = 100
    warning_text.value = "Emergency stop triggered.\nRelease safety switch to continue."
    window.show()
    window.focus()
# ============================================= #


# Recovers system functionality after emergency stop.
# Serviced by main thread via interrupts.
# ============================================= #
def kill_btn_release():
    global pwm_duty_cycle, cruise_set_spd, system_stop, app, window
    system_stop = False
    window.hide()
    bts_enable_pin.value = 0
# ============================================= #


# Display MPH value on GUI.
# Serviced by "status" thread.
# ============================================= #
def mph_display():
    global cur_spd, mph_val
    cur_spd.value = "{x:.1f} mph".format(x=mph_val)
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
        pwm_out_pin.value = pwm_duty_cycle
# ================================= ============ #


# Increases PWM in controlled steps. Used for testing purposes.
# Serviced by main thread via interrupts.
# ============================================= #
def pwm_inc():
    global pwm_duty_cycle, bts_enable_pin
    if pwm_duty_cycle < 1:
        bts_enable_pin.value = 1
        pwm_duty_cycle = pwm_duty_cycle + 0.05  # 0.05PWM = ~1.3V +- .1
        if pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Reduces MPH measurements to 0 gradually when the sensors stops detecting magnets
# Serviced by "throttle" thread
# ============================================= #
def reduce_to_zero():
    global mph_val, start_time, cruise_set_spd
    if time.time()-start_time > 1:
        while mph_val > 0:
            if throttle_sens_pin.value > THROTTLE_DEADBAND or mph_val < cruise_set_spd:
                break
            mph_val = mph_val - 0.3
            if mph_val < 0:
                mph_val = 0
            cur_spd.value = "{x:.1f} mph".format(x=mph_val)
            time.sleep(0.15)
# ============================================= #


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
    global is_cruise_on, cruise_set_spd, pwm_duty_cycle, pwm_out_pin, set_spd, cruise_set_rpm
    is_cruise_on = False
    bts_enable_pin.value = 0
    time.sleep(0.5)
    cruise_set_spd = 0
    cruise_set_rpm = 0
    set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
    pwm_duty_cycle = 0
    pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Measures system current (which is used on the webpage graph).
# Serviced by "status" thread.
# ============================================= #
def sys_current_check():
    global i_sensor_val
    i_sensor_val = (((curr_sens_pin.value + (curr_sens_pin.value*0.015)) * REF_V_ADC)-2.47) / CURR_SENS_SENSITIVITY
# ============================================= #


# Measures system voltage (which translates to battery charge).
# Serviced by "status" thread.
# ============================================= #
def sys_voltage_check():
    global v_sensor_val, motor_volt_sens_pin, bat_measure_sum, bat_measure_cnt
    bat_measure_cnt = bat_measure_cnt + 1
    bat_measure_sum = bat_measure_sum + (volt_sens_pin.value * REF_V_ADC * 5)  # +-1%
    if bat_measure_cnt >= 60:
        v_sensor_val = bat_measure_sum/bat_measure_cnt
        bat_measure_cnt = 0
        bat_measure_sum = 0
# ============================================= #


# Calculates RPM and MPH based on the time both magnets took to trigger the hall-effect sensor.
# Serviced by main thread upon invocation.
# rpm_val = ((magnet_count * 60) / (end_time - start_time)) / (# magnet groups on wheel * # magnets per group)
# ============================================= #
def update_rpm():
    global end_time, rpm_val, start_time, mph_val, magnet_count, prev_rpm_val
    end_time = time.time()
    rpm_val = ((magnet_count * 60) / (end_time - start_time)) / NUM_MAGNETS
    rpm_val = (rpm_val + prev_rpm_val) / 2
    prev_rpm_val = rpm_val
    mph_val = ((DIAMETER / 12) * 3.14 * rpm_val * 60) / 5280
    start_time = end_time
    magnet_count = 0
# ============================================= #


# GUI Initialization and components instantiation
# ===================GUI===================== #
app = App(title="Cruise Control Exhibition Tricycle", bg="#363636")

header_box = Box(app, width="fill", align="top", border=False)
ccet_logo_box = Box(header_box, height="fill", width="fill", align="left", border=False)
ccet_logo_img_padding = Text(ccet_logo_box, text=" ", color="white", size=24, height=2, align='right')
ccet_logo_img = Picture(ccet_logo_box, image=logo_img, width=60, height=60, align="right")
header_text = Text(header_box, text="CCET       ", color="white", height=1, size=32, width="fill", align="left")

control_info_box = Box(header_box, height="fill", width="fill", align="right", border=False)
control_info_img_padding = Text(control_info_box, text="   ", color="white", size=24, height=2, align='right')
control_info_img = Picture(control_info_box, image=control_img, width=120, height=60, align="right")
control_info_text = Text(control_info_box, text="      Mode:", color="white", size=24, height=2)

info_box = Box(app, width="fill", align="bottom", border=False)

cruise_info_box = Box(info_box, height="fill", width="fill", align="left", border=False)
cruise_info_img_padding = Text(cruise_info_box, text="    ", color="white", size=24, height=2, align='right')
cruise_info_img = Picture(cruise_info_box, image=cruise_lvl_val, width=70, height=70, align="right")
cruise_info_text = Text(cruise_info_box, text="Cruise Control:", color="white", size=24, height=2)

battery_info_box = Box(info_box, height="fill", width="fill", align="right", border=False)
battery_info_img_padding = Text(battery_info_box, text="   ", color="white", size=24, height=2, align='right')
battery_info_img = Picture(battery_info_box, image=bat_lvl_val, width=120, height=60, align="right")
battery_info_text = Text(battery_info_box, text="Battery:", color="white", size=24, height=2)

set_spd_box = Box(app, width="fill", height="fill", align="left", border=True)
set_spd_txt_padding = Text(set_spd_box, text=" ", color="white", size=35, height=1, align='top')
set_spd_text = Text(set_spd_box, text="Set Speed", height=2, color="white", size=32)
set_spd = Text(set_spd_box, text=str(cruise_set_spd)+" mph", color="white", size=40)

cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(mph_val)+" mph", color="yellow", size=60)

app.set_full_screen()

# Window use for system warnings
window = Window(app, bg="red", height=200, visible=False)
warning_icon_box = Box(window, height="fill", width="fill", align="top", border=False)
warning_text_box = Box(window, height="fill", width="fill", align="bottom", border=False)
warning_icon = Picture(warning_icon_box, image=warning_img, width=100, height=100, align="bottom")
warning_text = Text(warning_text_box, text="Emergency stop triggered.\nRelease safety switch to continue.",
                    color="white", size=30, height=2, align="top")
window.set_full_screen()
# =========================================== #

# ================Manage Threads============= #
# threadLock = threading.Lock()
status_thread = PiThread(1, "status")
control_thread = PiThread(2, "control")
comms_thread = PiThread(3, "comms")
throttle_thread = PiThread(4, "throttle")

status_thread.start()
control_thread.start()
comms_thread.start()
throttle_thread.start()
# =========================================== #

# =================Interrupts============== #
btn_inc_pin.when_pressed = inc_speed_btn
btn_dec_pin.when_pressed = dec_speed_btn
btn_set_pin.when_pressed = cruise_set_btn
btn_kill_pin.when_activated = kill_btn
btn_kill_pin.when_deactivated = kill_btn_release
hall_pin.when_activated = rpm_count
brake_sensor.when_deactivated = brake_press
ctrl_toggle_pin.when_activated = check_controller
ctrl_toggle_pin.when_deactivated = check_controller
# ========================================= #

# ==============Initial Checks============= #
if btn_kill_pin.value:
    kill_btn()
check_controller()
# ========================================= #

app.display()
