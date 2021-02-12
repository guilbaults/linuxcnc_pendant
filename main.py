import machine
import display
import network
import utime
from linuxcncrsh import Linuxcncrsh
import mfd

config = dict()
with open("config", "r") as f:
    for line in f:
        config_line = line.split("=")
        key = config_line[0].strip()
        value = config_line[1].strip()
        config[key] = value

# battery ADC is reading half the battery voltage (resistor divider)
try:
    adc_battery = machine.ADC(34)
except ValueError:
    # Ignore if the pin is already a ADC pin
    pass
adc_battery.atten(adc_battery.ATTN_11DB) # 3.9 V

# ldo is disabled when sleeping, enabling it now after boot
ldo = machine.Pin(14, mode=machine.Pin.OUT)
ldo.value(1)

tft = display.TFT()
tft.init(tft.ST7789, bgr=False, miso=17, backl_pin=4,
        backl_on=1, mosi=19, clk=18, cs=5, dc=16, splash=False)

tft.setwin(53, 40, 53+134, 40+239)
tft.set_bg(0xFFFFFF - tft.BLACK)

tft.clear()

wifi=network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect(config["wifi_ap"], config["wifi_password"])

tft.text(tft.CENTER, 0, "Connecting", 0xFFFFFF - tft.WHITE)

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

left_btn = machine.Pin(35, mode=machine.Pin.IN, debounce=1000)
right_btn = machine.Pin(0, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP, debounce=1000)

tft.clear()
mfd_pages[0].switch()

while True:
    old_mfd_page = mfd_page
    if left_btn.value() == 0:
        # go left
        mfd_page -= 1
        mfd_page = mfd_page % len(mfd_pages)
        while left_btn.value() == 0:
            utime.sleep_ms(10)

    if right_btn.value() == 0:
        # go right
        mfd_page +=1
        mfd_page = mfd_page % len(mfd_pages)
        while right_btn.value() == 0:
            utime.sleep_ms(10)

    if old_mfd_page != mfd_page:
        tft.clear()
        mfd_pages[mfd_page].switch()

    mfd_pages[mfd_page].render()
    utime.sleep_us(1)

