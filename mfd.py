import display

class Jog:
    def __init__(self, tft, cnc):
        self.tft = tft
        self.cnc = cnc

    def render(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.text(0,0, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,20, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,40, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - self.tft.WHITE)

class Info:
    def __init__(self, tft, adc):
        self.tft = tft
        self.adc = adc

    def render(self):
        volt = self.adc.read() * 2 / 1000
        self.tft.text(self.tft.CENTER, 190, "Bat: {:.2f}V".format(volt), 0xFFFFFF - self.tft.WHITE)

