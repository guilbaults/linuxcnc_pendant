import st7789 as display
import utime
import machine
import vga1_8x16 as font

class Jog:
    def __init__(self, tft, cnc, keys, encoder):
        self.tft = tft
        self.cnc = cnc
        self.keys = keys
        self.encoder = encoder
        self.encoder_position = 0
        self.position = 0
        self.selected_axis = 0
        self.increment_state = 0
        self.increments = [0.001, 0.01, 0.1, 1, 10]
        self.speed_state = 3
        self.speeds = [100, 1000, 10000, 20000]
        self.key_was_pressed = False

    def switch(self):
        self.encoder.clear()
        self.encoder_offset = 0
        self.tft.text(font, "Jog", 0, 0)
        self.tft.hline(0, 20, 135, display.WHITE)

    def encoder_position_usable(self):
        # return the number of physical ticks on the jogwheel
        if self.encoder.count() > 10000 or self.encoder.count() < -10000:
            # need to reset it before it overflow
            self.encoder_offset += self.encoder.count()
            self.encoder.clear()
        self.encoder_position = self.encoder_offset + self.encoder.count()
        return self.encoder_position//4

    def delta_encoder(self):
        delta = self.encoder_position_usable() - self.position
        self.position += delta
        return delta

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.text(font, "X: {:9.2f}".format(pos[0]), 0, 25)
        self.tft.text(font, "Y: {:9.2f}".format(pos[1]), 0, 45)
        self.tft.text(font, "Z: {:9.2f}".format(pos[2]), 0, 65)
        keys = self.keys.get_keys()

        if self.key_was_pressed:
            # prevent holding the key down
            if keys[(1, 0)] == 0 and keys[(1, 2)] == 0:
                # no key currently pressed
                self.key_was_pressed = False
        else:
            # new key pressed
            if keys[(1, 0)]:
                # increase increment
                self.increment_state += 1
                if self.increment_state >= len(self.increments):
                    self.increment_state = 0
            elif keys[(1, 2)]:
                # decrease increment
                self.increment_state -= 1
                if self.increment_state < 0:
                    self.increment_state = len(self.increments) - 1
            self.key_was_pressed = True

        increment = self.increments[self.increment_state]
        speed = self.speeds[self.speed_state]

        if keys[(0,0)]:
            axis = 'X'
        elif keys[(0,1)]:
            axis = 'Y'
        elif keys[(0,2)]:
            axis = 'Z'
        else:
            axis = None

        if axis is None:
            self.tft.text(font, " ", 0, 120)
        else:
            self.tft.text(font, "{}".format(axis), 0, 120)
            delta = self.delta_encoder()
            if delta != 0:
                self.cnc.set("jog_incr {} {} {}".format(
                    axis,
                    speed,
                    increment * delta
                ))

        self.tft.text(font, "Inc: {:.3f}".format(increment), 0, 160)
        self.tft.text(font, "Speed:{}".format(speed), 0, 180)


class Touchoff:
    def __init__(self, tft, cnc, keys):
        self.tft = tft
        self.cnc = cnc
        self.selected_axis = 0
        self.axis_name = ["X", "Y", "Z"]

    def switch(self):
        self.tft.text(font, "Touch-off", 0, 0)
        self.tft.hline(0, 20, 135, display.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.text(font, "X: {:9.2f}".format(pos[0]), 0, 25)
        self.tft.text(font, "Y: {:9.2f}".format(pos[1]), 0, 45)
        self.tft.text(font, "Z: {:9.2f}".format(pos[2]), 0, 65)

        self.tft.text(font, "{}".format(self.axis_name[self.selected_axis]), 0, 120)
        self.tft.text(font, "Offset: {:.2f}".format(6.35), 0, 160)
        # send touch off command, should look like G10 P0 L20 X0 Y0

class Execute:
    def __init__(self, tft, cnc, keys):
        self.tft = tft
        self.cnc = cnc
        self.last_state = None

    def switch(self):
        self.tft.text(font, "Execute", 0, 0)
        self.tft.hline(0, 20, 135, display.WHITE)

    def render(self):
        pos = self.cnc.get_pos("rel_act_pos")
        self.tft.text(font, "X: {:9.2f}".format(pos[0]), 0, 25)
        self.tft.text(font, "Y: {:9.2f}".format(pos[1]), 0, 45)
        self.tft.text(font, "Z: {:9.2f}".format(pos[2]), 0, 65)

        if self.cnc.get_onoff("estop") is True:
            if self.last_state != "ESTOP":
                #self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.RED, 0xFFFFFF - self.tft.RED)
                self.tft.text(font, "ESTOP", 0, 210)
            self.last_state = "ESTOP"
            return

        if self.cnc.get_onoff("machine") is True:
            feed = self.cnc.get("feed_override").split()[1]
            # spindle_override segfault linuxcncrsh
            #spindle = self.cnc.get("spindle_override").split()[1]
            self.tft.text(font, "Feed: {:4}".format(feed), 0, 100)
            #self.tft.text(0,120, "Spindle: {}".format(spindle), 0xFFFFFF - self.tft.WHITE)

            status = self.cnc.get("program_status").split()[1]
            if status == "RUNNING":
                if self.last_state != "RUNNING":
                    #self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.YELLOW, 0xFFFFFF - self.tft.YELLOW)
                    self.tft.text(font, "RUNNING", 0, 210)
                self.last_state = "RUNNING"
                return

            if status == "PAUSED":
                if self.last_state != "PAUSED":
                    #self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.YELLOW, 0xFFFFFF - self.tft.YELLOW)
                    self.tft.text(font, "PAUSED", 0, 210)
                self.last_state = "PAUSED"
                return

            if status == "IDLE":
                if self.last_state != "IDLE":
                    #self.tft.rect(0, 200, 134, 239, 0xFFFFFF - self.tft.GREEN, 0xFFFFFF - self.tft.GREEN)
                    self.tft.text(font, "IDLE", 0, 210)
                self.last_state = "IDLE"
                return

class Info:
    def __init__(self, tft, adc, wifi, keys):
        self.tft = tft
        self.adc = adc
        self.wifi = wifi

    def switch(self):
        self.tft.text(font, "Info", 0, 0)
        self.tft.hline(0, 20, 135, display.WHITE)

        ifconfig = self.wifi.ifconfig()
        self.tft.text(font, "IP addr", 0, 25)
        self.tft.text(font, ifconfig[0], 0, 45)
        self.tft.text(font, "Netmask", 0, 65)
        self.tft.text(font, ifconfig[1], 0, 85)
        self.tft.text(font, "Gateway", 0, 105)
        self.tft.text(font, ifconfig[2], 0, 125)

    def render(self):
        volt = self.adc.read()/4096 * 3.6 * 2
        self.tft.text(font, "Bat: {:.2f}V".format(volt), 0, 219)

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
        self.tft.text(font, "Sleep in {}".format(self.count), 0, 100)
        utime.sleep(1)
        if self.count <= 0:
            rtc = machine.RTC()
            rtc.wake_on_ext0(0, 0)
            #to save battery, PWR_EN=0 to disable the LDO
            ldo = machine.Pin(14, mode=machine.Pin.OUT)
            ldo.value(0)
            machine.deepsleep(0)

