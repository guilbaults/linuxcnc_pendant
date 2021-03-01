import machine
import st7789 as display
import network
import utime
import mfd
from linuxcncrsh import Linuxcncrsh
from rotary_irq_esp import RotaryIRQ
import micropython
micropython.alloc_emergency_exception_buf(100)

encoder = RotaryIRQ(pin_num_clk=26, pin_num_dt=27) 

row1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
row2 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
row3 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
col1 = machine.Pin(25, machine.Pin.OPEN_DRAIN, value = 1)
col2 = machine.Pin(32, machine.Pin.OPEN_DRAIN, value = 1)
col3 = machine.Pin(33, machine.Pin.OPEN_DRAIN, value = 1)

keyboard_rows = [row1, row2, row3]
keyboard_cols = [col1, col2, col3]

def scan_keys():
    keys = {}
    for col in range(3):
        # Scan each column by setting one to gnd while floating the other ones
        keyboard_cols[col].value(0)
        for row in range(3):
            if keyboard_rows[row].value() == 1:
                # inverted logic, 1 means button is not pressed
                v = False
            else:
                v = True
            keys[(col, row)] = v
        keyboard_cols[col].value(1)
    return keys

config = dict()
with open("config", "r") as f:
    for line in f:
        config_line = line.split("=")
        key = config_line[0].strip()
        value = config_line[1].strip()
        config[key] = value

# battery ADC is reading half the battery voltage (resistor divider)
#try:
adc_battery = machine.ADC(machine.Pin(34))
#except ValueError:
#    # Ignore if the pin is already a ADC pin
#    pass
#adc_battery.atten(adc_battery.ATTN_11DB) # 3.9 V

# ldo is disabled when sleeping, enabling it now after boot
ldo = machine.Pin(14, mode=machine.Pin.OUT)
ldo.value(1)

tft = display.ST7789(
    machine.SPI(2, baudrate=30000000, polarity=1, phase=1, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(17)),
    135,
    240,
    reset=machine.Pin(23, machine.Pin.OUT),
    cs=machine.Pin(5, machine.Pin.OUT),
    dc=machine.Pin(16, machine.Pin.OUT),
    backlight=machine.Pin(4, machine.Pin.OUT),
    rotation=2)
tft.init()

wifi=network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect(config["wifi_ap"], config["wifi_password"])

import vga1_8x16 as font
tft.text(font, "Connecting", 0, 0)

while wifi.isconnected() is False:
    utime.sleep_ms(10)
try:
    cnc = Linuxcncrsh(config["host"], config["port"])
except OSError:
    tft.clear()
    tft.text(tft.CENTER, 0, "LinuxCNC", 0xFFFFFF - tft.WHITE)
    tft.text(tft.CENTER, 20, "connection failed", 0xFFFFFF - tft.WHITE)
    tft.text(tft.CENTER, 40, "Rebooting", 0xFFFFFF - tft.WHITE)
    utime.sleep(5)
    machine.reset()

cnc.login(config["login"], config["password"], config["enable"])

info = mfd.Info(tft, adc_battery, wifi)
jog = mfd.Jog(tft, cnc)
touchoff = mfd.Touchoff(tft, cnc)
execute = mfd.Execute(tft, cnc)
sleep = mfd.Sleep(tft)

mfd_pages = [info, jog, touchoff, execute, sleep]
mfd_page = 0

#tft.clear()
mfd_pages[0].switch()

while True:
    keys = scan_keys()
    old_mfd_page = mfd_page

    if keys[(0,2)]: # SW7
        # go left
        mfd_page -= 1
        mfd_page = mfd_page % len(mfd_pages)
        while scan_keys()[(0,2)]:
            utime.sleep_ms(10)

    if keys[(2,2)]: # SW9
        # go right
        mfd_page +=1
        mfd_page = mfd_page % len(mfd_pages)
        while scan_keys()[(2,2)]:
            utime.sleep_ms(10)

    if old_mfd_page != mfd_page:
        tft.clear()
        mfd_pages[mfd_page].switch()

    mfd_pages[mfd_page].render()
    utime.sleep_us(1)
