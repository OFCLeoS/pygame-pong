import socket
host = input(" host -> ")
port = int(input(" port -> "))
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.bind((host, port))
print("Server Started")
while True:
    data, address = server_socket.recvfrom(1024)
    data = data.decode('utf-8')
    if not data:
        break
    print("Message from: " + str(address))
    print("Received : ")
    print(data)
    data = data.upper()
    print("Sending: ")
    print(data)
    server_socket.sendto(data.encode('utf-8'), address)
server_socket.close()

# NETWORKING ARCHITECTURE
# UDP
# - Timestamped packages
# Server-Client Structure
# - One player's machine is the Structure
# Server sends players
# - Ball Position -> THIS SHOULD BE CALCULATED IN THE CLIENT?
# - Ball Direction
# - Player Position
# - Score
# Players send to Server
# - Player ID
# - Desired Movement Direction
# Server stops receiving packets for x time -> timeout
