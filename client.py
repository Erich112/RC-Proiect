# echo client
import socket
import time

from ajutoare import *

print("Initializing Client...")

# Client Configuration
DISCOVERY_PORT = 5353

# mDNS Multicast Group
MDNS_MULTICAST_GROUP = '224.0.69.250'

# Create a UDP socket for service discovery
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.bind(('0.0.0.0', DISCOVERY_PORT))

# Add the socket to the multicast group
mreq = socket.inet_aton(MDNS_MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Send an mDNS-like query
message = "M-SEARCH"
client_socket.sendto(message.encode(), (MDNS_MULTICAST_GROUP, DISCOVERY_PORT))
data, addr = client_socket.recvfrom(1024)
print("Connected Successfully:", data.decode())

# Chose which resource to watch
print("Which resource would you like to see?")
print("1. CPU Usage")
print("2. Server Time")
print("3. Temperature")
option = input(":")
client_socket.sendto(option.encode(), (MDNS_MULTICAST_GROUP, DISCOVERY_PORT))
data, addr = client_socket.recvfrom(1024)
print("Received response:", data.decode())
# Receive and display responses
while True:
    data, addr = client_socket.recvfrom(1024)
    data, addr = client_socket.recvfrom(1024)
    unpackDNS(data)
