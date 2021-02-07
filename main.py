import machine
import display
import network
import utime
from linuxcncrsh import Linuxcncrsh

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

tft.line(0, 60, 134, 60, 0xFFFFFF - tft.WHITE)

tft.text(0,65, "Feed:{:.0f}%".format(50), 0xFFFFFF - tft.WHITE)
tft.text(0,85, "Spindle:{:.0f}%".format(150), 0xFFFFFF - tft.WHITE)
tft.text(0,105, "Tool# {}".format(11), 0xFFFFFF - tft.WHITE)
tft.text(0,125, "Probe: {}".format("open"), 0xFFFFFF - tft.WHITE)

tft.text(tft.CENTER, 170, "G53", 0xFFFFFF - tft.WHITE)

tft.rect(0, 210, 134, 40, 0xFFFFFF - tft.RED, 0xFFFFFF - tft.RED)
tft.font(tft.FONT_DejaVu18, transparent=True)
tft.text(tft.CENTER, 220, "ESTOP", 0xFFFFFF - tft.WHITE)

while True:
    tft.font(tft.FONT_DejaVu18, transparent=False)
    pos = cnc.get_pos("rel_act_pos")
    tft.text(0,0, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - tft.WHITE)
    tft.text(0,20, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - tft.WHITE)
    tft.text(0,40, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - tft.WHITE)

    volt = adc_battery.read() * 2 / 1000
    tft.text(tft.CENTER, 190, "Bat: {:.2f}V".format(volt), 0xFFFFFF - tft.WHITE)

#tft.line(0, 0, 0, 239)
#tft.line(0, 0, 134, 0)
#tft.line(134,0,134,239)
#tft.line(0,239,134,239)
