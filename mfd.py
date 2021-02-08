import display

class Jog:
    def __init__(self, tft, cnc):
        self.tft = tft
        self.cnc = cnc

    def switch(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 0, "Jog", 0xFFFFFF - self.tft.WHITE)
        self.tft.line(0, 22, 134, 22, 0xFFFFFF - self.tft.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.text(0,25, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,45, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,65, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - self.tft.WHITE)

class Info:
    def __init__(self, tft, adc, wifi):
        self.tft = tft
        self.adc = adc
        self.wifi = wifi

    def switch(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 0, "Info", 0xFFFFFF - self.tft.WHITE)
        self.tft.line(0, 22, 134, 22, 0xFFFFFF - self.tft.WHITE)
        ifconfig = self.wifi.ifconfig()
        self.tft.font(self.tft.FONT_Default, transparent=False)
        self.tft.text(self.tft.CENTER, 25, "IP addr", 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 45, ifconfig[0], 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 65, "Netmask", 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 85, ifconfig[1], 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 105, "Gateway", 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 125, ifconfig[2], 0xFFFFFF - self.tft.WHITE)

        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)

    def render(self):
        volt = self.adc.read() * 2 / 1000
        self.tft.text(self.tft.CENTER, 219, "Bat: {:.2f}V".format(volt), 0xFFFFFF - self.tft.WHITE)

