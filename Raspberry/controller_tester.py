import time
import threading
import socketio
# from pynput.keyboard import Key, Controller
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
        global cruise_set_spd, begin_test, cruise_set_rpm
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
                    # print(bts_enable_pin.value)

        elif self.thread_name is "comms":
            sio = socketio.Client()
            sio.connect('http://10.31.1.255:3000')
            t = 0
            while True:
                sio.emit('data_update', {
                    'Battery': bat_pct,
                    'Cruise State': is_cruise_on,
                    'Set Speed': cruise_set_spd,
                    'Actual Speed': mph_val,
                    'Current': i_sensor_val,      # TODO: Convert to I measurement
                    'Time': t
                })
                time.sleep(0.2)
                t = t + 0.2

        elif self.thread_name is "throttle":
            while True:
                if not system_stop:
                    adjust_throttle()
                    time.sleep(0.1)

        elif self.thread_name is "control":
            while True:
                if not system_stop:
                    pi_control()
                    # pi_control_static()
                    time.sleep(0.01)

        elif self.thread_name is "test":
            while True:
                if begin_test:
                    f = open("/home/pi/Documents/CCET/dynamic_test_4_22_2021("+str(num_test)+").csv", 'a')
                    f.write("{x:.3f}, {y:.3f}, {z:.3f}, {w:.3f}, {v:.3f}\n".format(x=time.time()-test_start,
                                                                                   y=control_act, z=cruise_set_spd,
                                                                                   w=rpm_val, v=mph_val))
                    f.close()
                    time.sleep(0.01)
        elif self.thread_name is "mph":
            while True:
                if begin_test:
                    time.sleep(10)
                    if cruise_set_spd < 7 and is_cruise_on:
                        cruise_set_spd = cruise_set_spd + 1
                        cruise_set_rpm = cruise_set_rpm + 12.93
                        set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
                        time.sleep(30)
                    # if cruise_set_spd < 7 and is_cruise_on:
                    #     cruise_set_spd = cruise_set_spd + 1
                    #     cruise_set_rpm = cruise_set_rpm + 12.93
                    #     set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
                    #     time.sleep(10)
                    # if cruise_set_spd > 1 and is_cruise_on:
                    #     cruise_set_spd = cruise_set_spd - 2
                    #     cruise_set_rpm = cruise_set_rpm - 25.86
                    #     set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
                    #     time.sleep(10)
                    if is_cruise_on:
                        cruise_set_btn()
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
is_cruise_on = False                        # flag for cruise on/off
magnet_count = 0                            # times magnet has passed hall sensor
deadband_throttle = (1/6)                   # sets the throttle to start reading after 1 Volts
current_sensitivity = 0.066                 # Current sensor sensitivity
rpm_val = 0                                 # latest RPM measurement
prev_rpm_val = 0                            # previous RPM measurement(used for average measurements)
mph_val = 0                                 # actual speed
v_sensor_val = 25                           # value from voltage sensor after conversion
i_sensor_val = 0                            # value from the current sensor after conversion
pwm_duty_cycle = 0                          # stores set value for PWM (ranges from 0 to 1)
start_time = time.time()                    # start time for a fraction of a wheel spin. Used for RPM calculations
end_time = 0                                # end time for a fraction of a wheel spin. Used for RPM calculations
diameter = 26                               # diameter of the system's wheel. Used for RPM-to-MPH conversion
cruise_set_spd = 0                          # speed set by the user for cruising
cruise_set_rpm = 0
cruise_lvl_val = cruise_off_img             # used by the GUI to present whether cruise is on or off
bat_pct = 100                               # battery percentage based on voltage readings. Used for battery indicator
bat_lvl_val = bat_lvl_5                     # used by the GUI to present the battery charge level
bat_blink = False                           # flag for the GUI to blink the battery level indicator on low battery
system_stop = False                         # flag for the kill switch to halt system execution
prev_pwm = 0                                # used as a hold for control equation
control_err = 0                             # difference between set speed and actual speed. Measured currently
prev_control_err = 0                        # difference between set speed and actual speed. Previous measurement
control_act = 0                             # determined output for the controller. Measured currently
prev_control_act = 0                        # determined output for the controller. Previous measurement
control_gain = 0.88                      # controller gain. Preliminary values from C Falero testing
control_zero = 0.988                       # controller zero. Preliminary values from C Falero testing
control_gain_static = 0.04027               # controller gain. Preliminary values from C Ramirez testing
control_zero_static = 0.902                 # controller zero. Preliminary values from C Ramirez testing
bat_measure_sum = 0                         # sum of battery measurements. Used to average battery measurements
bat_measure_cnt = 0                         # count of battery measurements. Used to average battery measurements
begin_test = False
num_test = 4
test_start = 0
# keyboard = Controller()
# ========================================= #

# ==============Enables==================== #
bts_enable_pin.value = 0
# ========================================= #


# Verifies throttle inputs and adjust driver output accordingly.
# Serviced by "throttle" thread.
# PWM/ADC Ratio = (throttle_sens_pin.value - Throttle_min) * (1/((Throttle_max-Throttle_min)/Vref_ADC))
# ============================================= #
def adjust_throttle():
    global throttle_sens_pin, pwm_duty_cycle, is_cruise_on, prev_pwm
    if not is_cruise_on:
        # if is_throttle_active_pin:
        if throttle_sens_pin.value > 0.16:
            bts_enable_pin.value = 1
        else:
            bts_enable_pin.value = 0
        prev_pwm = pwm_duty_cycle
        pwm_duty_cycle = (throttle_sens_pin.value - 0.16) * 1.9737
        if pwm_duty_cycle <= 0:
            pwm_duty_cycle = 0
        elif pwm_duty_cycle > 1:
            pwm_duty_cycle = 1
        # print(throttle_sens_pin.value)
        # print(is_throttle_active_pin.value)
        # print(bts_enable_pin.value)
        pwm_out_pin.value = pwm_duty_cycle
    reduce_to_zero()
# ============================================= #


# TODO: Adjust percentage based on motor operation %
# TODO: Calibrate final implementation
# Uses measured system voltage to adjust battery charge icon in GUI.
# Serviced by "status" thread.
# ============================================= #
def bat_lvl_check():
    global v_sensor_val, bat_lvl_val, bat_blink, bat_pct
    # 25.4V will be considered a system battery of 100%
    # 23.16V will be considered a system battery of 0%
    # (Vmeasured - Vmin) / (Vmax - Vmin)
    bat_pct = ((v_sensor_val - 23.16)/2.24) * 100
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
        # print("low battery")
        # TODO: Determine if charger is connected to automatically close popup
        bat_lvl_val = bat_lvl_0
        battery_info_img.value = bat_lvl_val
        bat_blink = False
        bts_enable_pin.value = 0
        app.warn(title="Warning", text="Low Battery. Please connect to charger.")
    battery_info_img.value = bat_lvl_val
# ============================================= #


# Deactivates cruise control when braking if cruise is engaged.
# Serviced by main thread via interrupts
# ============================================= #
def brake_press():
    global is_cruise_on
    if is_cruise_on:
        stop_cruise()
# ============================================= #


# Proportional Integral Controller implementation.
# Uses measured mph and set mph to automatically adjust driver output.
# Serviced by "control" thread
# ============================================= #
def pi_control():
    global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm, control_err, control_act, \
        control_gain, prev_control_act, prev_control_err, control_zero, cruise_set_rpm
    if is_cruise_on:
        prev_pwm = pwm_duty_cycle
        if not bts_enable_pin.value:
            bts_enable_pin.value = 1
        control_err = cruise_set_rpm - rpm_val
        control_act = (control_err * control_gain) - (prev_control_err * control_gain *
                                                      control_zero) + prev_control_act
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
# def pi_control_static():
#     global cruise_set_spd, mph_val, pwm_duty_cycle, is_cruise_on, prev_pwm, control_err, control_act, \
#         control_gain_static, prev_control_act, prev_control_err, control_zero_static, cruise_set_rpm
#     if is_cruise_on:
#         prev_pwm = pwm_duty_cycle
#         if not bts_enable_pin.value:
#             bts_enable_pin.value = 1
#         control_err = cruise_set_rpm - rpm_val
#         control_act = (control_err * control_gain_static) - (prev_control_err * control_gain_static *
#                                                              control_zero_static) + prev_control_act
#         if control_act < 0:
#             control_act = 0
#         elif control_act > 24:
#             control_act = 24
#         pwm_duty_cycle = (control_act/24)
#         if pwm_duty_cycle > 1:
#             pwm_duty_cycle = 1
#         prev_control_err = control_err
#         prev_control_act = control_act
#         pwm_out_pin.value = pwm_duty_cycle
#     else:
#         prev_control_err = rpm_val
#         prev_control_act = prev_pwm * 24
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
        x = x * 5280 * (12/diameter) * (1/3.14) * (1/60)
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
    global cruise_set_spd, is_cruise_on, mph_val, cruise_set_rpm, begin_test, num_test, test_start
    if is_cruise_on:
        begin_test = False
        num_test = num_test + 1
        stop_cruise()
    else:
        if 3 <= mph_val <= 7:    # if less than 3mph, can't activate
            is_cruise_on = True
            cruise_set_spd = mph_val
            cruise_set_rpm = rpm_val
            set_spd.value = "{x:.1f} mph".format(x=cruise_set_spd)
            f = open("/home/pi/Documents/CCET/dynamic_test_4_22_2021("+str(num_test)+").csv", 'w')
            f.write("Time(s), Control Action, Set Speed(mph), RPM Out, MPH Out\n")
            f.close()
            test_start = time.time()
            begin_test = True
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


# TODO: Set enable back to 1 upon kill switch deactivation
# TODO: Verify wait_for_inactive()
# Kills the system in case of emergency. Shows popup warning until disengaged.
# Serviced by main thread via interrupts.
# ============================================= #
def kill_btn():
    global pwm_duty_cycle, cruise_set_spd, system_stop
    stop_cruise()
    system_stop = True
    print("murio")
    app.warn(title="Warning", text="Emergency stop triggered. Release safety switch to continue.")
    btn_kill_pin.wait_for_inactive()
    # keyboard.press(Key.enter)
    # keyboard.release(Key.enter)
    print("revivio")
    system_stop = False
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
    global is_throttle_active_pin, mph_val, start_time, cruise_set_spd
    # print(time.time()-start_time)
    if time.time()-start_time > 1:
        while mph_val > 0:
            if throttle_sens_pin.value > 0.16 or mph_val < cruise_set_spd:
                break
            mph_val = mph_val - 0.1
            if mph_val < 0:
                mph_val = 0
            cur_spd.value = "{x:.1f} mph".format(x=mph_val)
            time.sleep(0.05)
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
    print('Cruise Stopped')
    pwm_duty_cycle = 0
    pwm_out_pin.value = pwm_duty_cycle
# ============================================= #


# Measures system current (which is used on the webpage graph).
# Serviced by "status" thread.
# ============================================= #
def sys_current_check():
    global i_sensor_val
    i_sensor_val = (((curr_sens_pin.value + (curr_sens_pin.value*0.015)) * 6)-2.47) / current_sensitivity
    # print("System Current: {x:.4f}A".format(x=i_sensor_val))
# ============================================= #


# Measures system voltage (which translates to battery charge).
# Serviced by "status" thread.
# ============================================= #
def sys_voltage_check():
    global v_sensor_val, motor_volt_sens_pin, bat_measure_sum, bat_measure_cnt
    bat_measure_cnt = bat_measure_cnt + 1
    bat_measure_sum = bat_measure_sum + (volt_sens_pin.value * 6 * 5)  # +-1%
    if bat_measure_cnt >= 60:
        v_sensor_val = bat_measure_sum/bat_measure_cnt
        bat_measure_cnt = 0
        bat_measure_sum = 0
        # print("Battery Voltage: {x:.1f}V".format(x=v_sensor_val))
    # mv_sensor_val = motor_volt_sens_pin.value * 6 * 5
    # print("Battery Voltage: {x:.1f}V".format(x=v_sensor_val))
    # print("Motor Voltage: {y:.2f}V".format(y=mv_sensor_val))
# ============================================= #


# Calculates RPM and MPH based on the time both magnets took to trigger the hall-effect sensor.
# Serviced by main thread upon invocation.
# rpm_val = ((magnet_count * 60) / (end_time - start_time)) / (# magnet groups on wheel * # magnets per group)
# ============================================= #
def update_rpm():
    global end_time, rpm_val, start_time, mph_val, magnet_count, prev_rpm_val
    end_time = time.time()
    rpm_val = ((magnet_count * 60) / (end_time - start_time)) / 9
    rpm_val = (rpm_val + prev_rpm_val) / 2
    prev_rpm_val = rpm_val
    mph_val = ((diameter / 12) * 3.14 * rpm_val * 60) / 5280
    start_time = end_time
    magnet_count = 0
# ============================================= #


# GUI Initialization and components instantiation
# ===================GUI===================== #
app = App(title="Cruise Control Exhibition Tricycle", bg="#363636")

header_box = Box(app, width="fill", align="top", border=False)
header_text = Text(header_box, text="Cruise Control Exhibition Tricycle", color="white", height=2, size=24)

info_box = Box(app, width="fill", align="bottom", border=False)

cruise_info_box = Box(info_box, height="fill", width="fill", align="left", border=False)
cruise_info_img_padding = Text(cruise_info_box, text="    ", color="white", size=24, height=2, align='right')
cruise_info_img = Picture(cruise_info_box, image=cruise_lvl_val, width=70,
                          height=70, align="right")
cruise_info_text = Text(cruise_info_box, text="Cruise Control:", color="white", size=24, height=2)

# TODO: Add controller mode (static/dynamic)
battery_info_box = Box(info_box, height="fill", width="fill", align="right", border=False)
battery_info_img_padding = Text(battery_info_box, text=" ", color="white", size=24, height=2, align='right')
battery_info_img = Picture(battery_info_box, image=bat_lvl_val, width=120,
                           height=60, align="right")
battery_info_text = Text(battery_info_box, text="Battery:", color="white", size=24, height=2)

set_spd_box = Box(app, width="fill", height="fill", align="left", border=True)
set_spd_txt_padding = Text(set_spd_box, text=" ", color="white", size=35, height=1, align='top')
set_spd_text = Text(set_spd_box, text="Set Speed", height=2, color="white", size=32)
set_spd = Text(set_spd_box, text=str(cruise_set_spd)+" mph", color="white", size=40)

cur_spd_box = Box(app, width="fill", height="fill", align="right", border=True)
cur_spd_txt_padding = Text(cur_spd_box, text=" ", color="white", size=24, height=1, align='top')
cur_spd_text = Text(cur_spd_box, text="Current Speed", height=2, color="yellow", size=36)
cur_spd = Text(cur_spd_box, text=str(mph_val)+" mph", color="yellow", size=60)

app.set_full_screen('Esc')
# =========================================== #

# ================Manage Threads============= #
# threadLock = threading.Lock()
status_thread = PiThread(1, "status")
control_thread = PiThread(2, "control")
comms_thread = PiThread(3, "comms")
throttle_thread = PiThread(4, "throttle")
test_thread = PiThread(5, "test")
mph_thread = PiThread(6, "mph")

status_thread.start()
control_thread.start()
comms_thread.start()
throttle_thread.start()
test_thread.start()
# mph_thread.start()
# =========================================== #

# =================Interrupts============== #
btn_inc_pin.when_pressed = inc_speed_btn
btn_dec_pin.when_pressed = dec_speed_btn
btn_set_pin.when_pressed = cruise_set_btn
btn_kill_pin.when_activated = kill_btn
hall_pin.when_activated = rpm_count
brake_sensor.when_deactivated = brake_press
# ========================================= #

app.display()

