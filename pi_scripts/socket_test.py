import sys
import socket

tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsocket.connect( ('10.0.0.7', 8000) )

while True:
        temp = open("/sys/bus/w1/devices/28-00000a005906/w1_slave","r")  # temp sensor output
        string = temp.read()
	print string[-6:]  # just temp
        tcpsocket.send(string[-6:])

