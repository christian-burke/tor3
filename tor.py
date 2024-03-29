import socket
import struct
import re


class CommandParser(object):
    def __init__(self, __status, __info, __response):
        self.status = __status
        self.info = __info
        self.response = __response


class TorControl(object):
    def __init__(self, proxy_host, proxy_control_port):
        self.proxy_host = proxy_host
        self.proxy_control_port = int(proxy_control_port)

    def authenticate(self, password):
        self.password = str(password)
        try:
            TorControlSocket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
            TorControlSocket.connect((self.proxy_host,
                                      self.proxy_control_port))
            self.proxy_control_session = TorControlSocket
            self.proxy_control_session.send(
                f'AUTHENTICATE "{self.password}\"\r\n'.encode())
            status = self.proxy_control_session.recv(50)
            if "250" not in str(status):
                raise SystemError("Incorrect Password For Tor Control")
                return False
            return True
        except socket.error:
            raise RuntimeError("Error Connecting To Tor Server @ %s:%d" %
                               (self.proxy_host, self.proxy_control_port))

    def new_identity(self):
        try:
            self.proxy_control_session.send("SIGNAL NEWNYM\r\n".encode())
            id_status = self.proxy_control_session.recv(50)
            if "250" not in str(id_status):
                raise SystemError("Error Fetching New Identity... \
                                  Are You Authenticated?")
                return False
            return True
        except socket.error:
            raise SystemError("Error Sending/Receiving Command... \
                              Are You Authenticated?")
            return False

    def command(self, command):
        try:
            command = str(command)
            self.proxy_control_session.send(command+"\r\n")
            rec = self.proxy_control_session.recv(100)
            temp_status_info = rec.split(" ")
            try:
                status = int(temp_status_info[0])
            except:
                status = temp_status_info[0]
            info = str(" ".join(temp_status_info[1:]))
            status_info = CommandParser(status, info, str(rec))
            return status_info
        except socket.error:
            raise SystemError("Error Sending/Receiving Command... \
                              Are You Authenticated?")


class Tor(object):
    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port)
        try:
            TorSessionSocket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
            TorSessionSocket.connect((self.proxy_host,
                                      self.proxy_port))
            self.proxy_session = TorSessionSocket
        except socket.error:
            raise RuntimeError("Error Connecting To Tor Server @ %s:%d" %
                               (proxy_host, int(proxy_port)))

    def initialize(self):
        req1 = b"\x05\x01\x00"  # SOCKS5, ONE AUTH, NO AUTHENTICATION
        self.proxy_session.send(req1)
        resp1 = self.proxy_session.recv(2)
        if resp1[1] != 0:
            raise RuntimeError
        return True

    def connect(self, host, port):
        req2 = b"\x05\x01\x00\x03"  # SOCKS5, CONNECT, FULLY RESERVED DOM, DOM
        req2 += struct.pack("b", len(str(host)))
        req2 += host.encode()
        req2 += struct.pack("h", socket.htons(int(port)))
        self.proxy_session.send(req2)
        resp2 = self.proxy_session.recv(10)
        if resp2[1] != 0:
            raise RuntimeError("Error Connecting To %s:%d" % (host, port))
        return True

    def send(self, data):
        try:
            self.proxy_session.send(data)
            rec = self.proxy_session.recv(65535)
            return rec
        except:
            raise RuntimeError("Error Sending/Receiving Data Via Tor")

    def get_request(self):
        try:
            self.proxy_session.send(b"GET / HTTP/1.0\r\n\r\n")
            rec = self.proxy_session.recv(65535)
            f = re.search("\r\n\r\n", rec.decode())
            rec = rec[f.start()+4:]
            return rec
        except socket.error:
            raise RuntimeError("Error Sending/Receiving Request")
