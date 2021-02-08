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
adc_battery.atten(adc_battery.ATTN_6DB) # 0V - 2.5V

wifi=network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect(config["wifi_ap"], config["wifi_password"])

utime.sleep_ms(3000)

cnc = Linuxcncrsh(config["host"], config["port"])
cnc.login(config["login"], config["password"], config["enable"])

tft = display.TFT()
tft.init(tft.ST7789, bgr=False, miso=17, backl_pin=4,
        backl_on=1, mosi=19, clk=18, cs=5, dc=16, splash=False)

tft.setwin(53, 40, 53+134, 40+239)
tft.set_bg(0xFFFFFF - tft.BLACK)

tft.clear()

info = mfd.Info(tft, adc_battery)
jog = mfd.Jog(tft, cnc)
mfd_pages = [jog, info]
mfd_page = 0

left_btn = machine.Pin(35, mode=machine.Pin.IN, debounce=1000)
right_btn = machine.Pin(0, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP, debounce=1000)

while True:
    old_mfd_page = mfd_page
    if left_btn.value() == 0:
        # go left
        mfd_page -= 1
        mfd_page = mfd_page % len(mfd_pages)
        while left_btn.value() == 0:
            pass
    if right_btn.value() == 0:
        # go right
        mfd_page +=1
        mfd_page = mfd_page % len(mfd_pages)
        while right_btn.value() == 0:
            pass

    if old_mfd_page != mfd_page:
        tft.clear()

    mfd_pages[mfd_page].render()

