import st7789 as display
import utime
import machine

class Jog:
    def __init__(self, tft, cnc):
        self.tft = tft
        self.cnc = cnc
        self.selected_axis = 0
        self.axis_name = ["X", "Y", "Z"]

    def switch(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 0, "Jog", 0xFFFFFF - self.tft.WHITE)
        self.tft.line(0, 22, 134, 22, 0xFFFFFF - self.tft.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(0,25, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,45, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,65, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - self.tft.WHITE)


        self.tft.font(self.tft.FONT_Comic, transparent=False)
        self.tft.text(self.tft.CENTER, 120, "{}".format(self.axis_name[self.selected_axis]), 0xFFFFFF - self.tft.WHITE)
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 160, "Inc: {:.2f}".format(0.01), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(self.tft.CENTER, 180, "Speed:{}".format(1000), 0xFFFFFF - self.tft.WHITE)
        #jog_incr {0|1|2|...} <speed> <incr>

class Touchoff:
    def __init__(self, tft, cnc):
        self.tft = tft
        self.cnc = cnc
        self.selected_axis = 0
        self.axis_name = ["X", "Y", "Z"]

    def switch(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 0, "Touch-off", 0xFFFFFF - self.tft.WHITE)
        self.tft.line(0, 22, 134, 22, 0xFFFFFF - self.tft.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(0,25, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,45, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,65, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - self.tft.WHITE)

        self.tft.font(self.tft.FONT_Comic, transparent=False)
        self.tft.text(self.tft.CENTER, 120, "{}".format(self.axis_name[self.selected_axis]), 0xFFFFFF - self.tft.WHITE)
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 160, "Offset: {:.2f}".format(6.35), 0xFFFFFF - self.tft.WHITE)
        # send touch off command, should look like G10 P0 L20 X0 Y0

class Execute:
    def __init__(self, tft, cnc):
        self.tft = tft
        self.cnc = cnc
        self.last_state = None

    def switch(self):
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(self.tft.CENTER, 0, "Execute", 0xFFFFFF - self.tft.WHITE)
        self.tft.line(0, 22, 134, 22, 0xFFFFFF - self.tft.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.font(self.tft.FONT_DejaVu18, transparent=False)
        self.tft.text(0,25, "X: {:9.2f}".format(pos[0]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,45, "Y: {:9.2f}".format(pos[1]), 0xFFFFFF - self.tft.WHITE)
        self.tft.text(0,65, "Z: {:9.2f}".format(pos[2]), 0xFFFFFF - self.tft.WHITE)

        if self.cnc.get_onoff("estop") is True:
            self.tft.font(self.tft.FONT_DejaVu18, transparent=True)
            if self.last_state != "ESTOP":
                self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.RED, 0xFFFFFF - self.tft.RED)
                self.tft.text(self.tft.CENTER, 210, "ESTOP", 0xFFFFFF - self.tft.WHITE)
            self.last_state = "ESTOP"
            return

        if self.cnc.get_onoff("machine") is True:
            feed = self.cnc.get("feed_override").split()[1]
            # spindle_override segfault linuxcncrsh
            #spindle = self.cnc.get("spindle_override").split()[1]
            self.tft.text(0,100, "Feed: {:4}".format(feed), 0xFFFFFF - self.tft.WHITE)
            #self.tft.text(0,120, "Spindle: {}".format(spindle), 0xFFFFFF - self.tft.WHITE)

            status = self.cnc.get("program_status").split()[1]
            if status == "RUNNING":
                self.tft.font(self.tft.FONT_DejaVu18, transparent=True)
                if self.last_state != "RUNNING":
                    self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.YELLOW, 0xFFFFFF - self.tft.YELLOW)
                    self.tft.text(self.tft.CENTER, 210, "RUNNING", 0xFFFFFF - self.tft.BLACK)
                self.last_state = "RUNNING"
                return

            if status == "PAUSED":
                self.tft.font(self.tft.FONT_DejaVu18, transparent=True)
                if self.last_state != "PAUSED":
                    self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.YELLOW, 0xFFFFFF - self.tft.YELLOW)
                    self.tft.text(self.tft.CENTER, 210, "PAUSED", 0xFFFFFF - self.tft.BLACK)
                self.last_state = "PAUSED"
                return

            if status == "IDLE":
                self.tft.font(self.tft.FONT_DejaVu18, transparent=True)
                if self.last_state != "IDLE":
                    self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.GREEN, 0xFFFFFF - self.tft.GREEN)
                    self.tft.text(self.tft.CENTER, 210, "IDLE", 0xFFFFFF - self.tft.BLACK)
                self.last_state = "IDLE"
                return

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
        self.adc.collect(1000, len=100, wait=True)
        volt = self.adc.collected()[3] * 2 /1000
        self.tft.text(self.tft.CENTER, 219, "Bat: {:.2f}V".format(volt), 0xFFFFFF - self.tft.WHITE)

class Sleep:
    """
    Currently use 1.5mA
    """
    def __init__(self, tft):
        self.tft = tft

    def switch(self):
        self.count = 6

    def render(self):
        self.count -= 1
        self.tft.text(self.tft.CENTER, 100, "Sleep in {}".format(self.count), 0xFFFFFF - self.tft.WHITE)
        utime.sleep(1)
        if self.count <= 0:
            rtc = machine.RTC()
            rtc.wake_on_ext0(0, 0)
            #to save battery, PWR_EN=0 to disable the LDO
            ldo = machine.Pin(14, mode=machine.Pin.OUT)
            ldo.value(0)
            machine.deepsleep(0)

