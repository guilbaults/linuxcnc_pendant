import machine
import display
import network
import utime
from linuxcncrsh import Linuxcncrsh
import mfd
import micropython
micropython.alloc_emergency_exception_buf(100)

class Encoder:
    def __init__(self, pinA, pinB):
        self.position = 0
        self.state = 0
        self.pinA = machine.Pin(pinA, machine.Pin.IN, handler=self.callback, trigger=machine.Pin.IRQ_ANYEDGE, debounce=100, acttime=100)
        self.pinB = machine.Pin(pinB, machine.Pin.IN, handler=self.callback, trigger=machine.Pin.IRQ_ANYEDGE, debounce=100, acttime=100)
        self.state_matrix = [0,-1,1,None,1,0,None,-1,-1,None,0,1,None,1,-1,0]
        self.count = 0

    def callback(self, pin):
        #irq_state = machine.disable_irq()
        new = self.pinA.irqvalue() *2 + self.pinB.irqvalue()
        out = self.state_matrix[self.state*4 + new]
        if out is None:
            out = 0
        self.state = new
        self.position += out
        #machine.enable_irq(irq_state)
        self.count+=1

    def read(self):
        return self.position
    def count(self):
        return self.count

encoder = Encoder(26, 27)

while True:
    print(encoder.read(), encoder.count)
    i = 0
    for i in range(10000):
        i += 1

row1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
row2 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
row3 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
col1 = machine.Pin(25, machine.Pin.OUT_OD, value = 1)
col2 = machine.Pin(32, machine.Pin.OUT_OD, value = 1)
col3 = machine.Pin(33, machine.Pin.OUT_OD, value = 1)

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

tft.clear()
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

