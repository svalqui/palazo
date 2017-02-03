import socket


class TcpIp:
    def __init__(self):
        self.socket_s = ""
        self.connect_error = 0
        self.ip_address = ""
        self.port_number = 0

    def query_port(self, ip="", port_number=0):
        self.ip_address = ip
        self.port_number = port_number
        self.socket_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_error = self.socket_s.connect_ex((self.ip_address, self.port_number))
        if self.connect_error == 0:
            print("OPEN, Port ", self.port_number, " on IP ", self.ip_address)
        else:
            print("Error ", self.connect_error, " Opening port ", self.port_number, " on IP ", self.ip_address)
