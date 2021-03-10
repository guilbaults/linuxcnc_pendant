import usocket
import ure

class Linuxcncrsh():
    def __init__(self, host, port):
        addr_info = usocket.getaddrinfo(host, port)
        addr = addr_info[0][-1]
        self.s = usocket.socket()
        self.s.connect(addr)

    def login(self, clientname, password, enable):
        self.s.write("hello {} {} 1.1\r\n".format(password, clientname))
        if self.readline() != "HELLO ACK EMCNETSVR 1.1":
            raise RuntimeError("Wrong password")
        self.s.write("set enable {}\r\n".format(enable))
        self.readline()
        self.s.write("set echo off\r\n")
        self.readline()
        self.s.write("set verbose on\r\n")
        if self.readline() != "SET VERBOSE ACK":
            raise RuntimeError("Verbose failed")

    def readline(self):
        line = self.s.readline().decode("utf-8") 
        return line.strip()

    def valid(self):
        line = self.readline()
        if "NACK" in line:
            return False
        else:
            return True

    def get_onoff(self, param):
        self.s.write("get {}\r\n".format(param))
        line = self.readline()
        if "ON" in line:
            return True
        else:
            return False

    def get(self, param):
        self.s.write("get {}\r\n".format(param))
        return self.readline()


    def set_onoff(self, param, value):
        if value is True:
            self.s.write("set {} ON\r\n".format(param))
        else:
            self.s.write("set {} OFF\r\n".format(param))
        return self.valid()

    def set(self, value):
        self.s.write("set {}\r\n".format(value))
        return self.valid()

    def get_pos(self, pos_type):
        self.s.write("get {}\r\n".format(pos_type))
        pos = self.readline().split()
        try:
            return (float(pos[1]), float(pos[2]), float(pos[3]))
        except:
            print(pos)
            raise

if __name__ == "__main__":
    import time
    config = dict()
    with open("config", "r") as f:
        for line in f:
            config_line = line.split("=")
            key = config_line[0].strip()
            value = config_line[1].strip()
            config[key] = value

    cnc = Linuxcncrsh(config["host"], config["port"])

    cnc.login(config["login"], config["password"], config["enable"])

    print("get estop", cnc.get_onoff("estop"))
    cnc.set_onoff("estop", True)
    time.sleep(0.1)
    print("get estop", cnc.get_onoff("estop"))
    cnc.set_onoff("estop", False)
    time.sleep(0.1)
    print("get estop", cnc.get_onoff("estop"))

    cnc.set_onoff("machine", True)

    print(cnc.get_pos("rel_act_pos"))
