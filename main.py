import machine
import display
import network

wifi=network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect("changeme","changeme")

#utime.sleep_ms(3000)
#network.telnet.start(user="changeme",password="changeme")

tft = display.TFT()
tft.init(tft.ST7789, bgr=False, miso=17, backl_pin=4,
        backl_on=1, mosi=19, clk=18, cs=5, dc=16, splash=False)

tft.setwin(53, 40, 53+134, 40+239)
tft.set_bg(0xFFFFFF - tft.BLACK)

tft.clear()
tft.font(tft.FONT_DejaVu18)

i = -9999.99
tft.text(0,0, "X: {:9.2f}".format(i), 0xFFFFFF - tft.WHITE)
tft.text(0,20, "Y: {:9.2f}".format(i), 0xFFFFFF - tft.WHITE)
tft.text(0,40, "Z: {:9.2f}".format(i), 0xFFFFFF - tft.WHITE)

tft.line(0, 60, 134, 60, 0xFFFFFF - tft.WHITE)

tft.text(0,65, "Feed:{:.0f}%".format(50), 0xFFFFFF - tft.WHITE)
tft.text(0,85, "Spindle:{:.0f}%".format(150), 0xFFFFFF - tft.WHITE)
tft.text(0,105, "Tool# {}".format(11), 0xFFFFFF - tft.WHITE)
tft.text(0,125, "Probe: {}".format("open"), 0xFFFFFF - tft.WHITE)

tft.text(tft.CENTER, 170, "G53", 0xFFFFFF - tft.WHITE)
tft.text(tft.CENTER, 190, "Battery:{:.0f}%".format(95), 0xFFFFFF - tft.WHITE)

tft.rect(0, 210, 134, 40, 0xFFFFFF - tft.RED, 0xFFFFFF - tft.RED)
tft.font(tft.FONT_DejaVu18, transparent=True)
tft.text(tft.CENTER, 220, "ESTOP", 0xFFFFFF - tft.WHITE)

#tft.line(0, 0, 0, 239)
#tft.line(0, 0, 134, 0)
#tft.line(134,0,134,239)
#tft.line(0,239,134,239)
