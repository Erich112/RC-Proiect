# echo server
import random
import socket
import time
import threading
import psutil  # For CPU usage
from ajutoare import *

print("Initializing Server...")

# Server Configuration
SERVICE_NAME = "MyServerService"
PORT = 8080

# mDNS Multicast Group
MDNS_MULTICAST_GROUP = '224.0.69.250'
MDNS_PORT = 5353

# Create a UDP socket for service announcements
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', MDNS_PORT))

# Add the socket to the multicast group
mreq = socket.inet_aton(MDNS_MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


# Function to get server CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_temperature():
    temperature = psutil.sensors_temperatures().get('coretemp', [])
    return temperature[0].current

# Function to get server time
def get_server_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def extract_option(option):
    while option == 0:
        data, addr = server_socket.recvfrom(1024)
        if data.decode().isnumeric():
            option = data.decode()

    server_socket.sendto(("SELECT-OPTION" + option).encode(), (MDNS_MULTICAST_GROUP, MDNS_PORT))
    return option

resource="none=True"

# Function to announce service with dynamic data (CPU usage or server time)
def announce_service(display_cpu_usage):
    while True:
        # Get dynamic data
        # 1 - CPU usage
        # 2 - server time
        # Send mDNS-like announcement
        announcement = f"\nHTTP/1.1 200 OK\nCACHE-CONTROL: max-age=60\nST: {SERVICE_NAME}\n"
        if int(display_cpu_usage) == 1:
            announcement = announcement + "CPU USAGE: "
            dynamic_data = get_cpu_usage()
            resource = "CPU="+str(dynamic_data)
        elif int(display_cpu_usage) == 2:
            announcement = announcement + "SERVER TIME: "
            dynamic_data = get_server_time()
            resource = "TIME=" + str(dynamic_data)
        elif int(display_cpu_usage) == 3:
            announcement = announcement + "TEMPERATURE: "
            dynamic_data = get_temperature()
            resource = "TEMPERATURE="+str(dynamic_data)
        else:
            announcement = announcement + "N/A: "
            dynamic_data = "N/A"
            
        data, addr = server_socket.recvfrom(1024)
        print(addr, ": are ", resource)
        #announcement = announcement + str(dynamic_data)
        #server_socket.sendto(announcement.encode(), (MDNS_MULTICAST_GROUP, MDNS_PORT))
        time.sleep(5)

# Extract the option
option = 0
option = extract_option(option)
time.sleep(1)

# Start a thread for service announcements
announcement_thread = threading.Thread(target=announce_service, args=(option,))
announcement_thread.start()

# Your server logic goes here
while True:
    # Perform server operations as needed
    server_socket.sendto(DNSpack(1, resource, addr).encode(), (MDNS_MULTICAST_GROUP, MDNS_PORT))
    time.sleep(1)
