import socket
host = input(" host -> ")
port = int(input(" port -> "))
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.bind((host, port))
print("Server Started")

num = 0
while True:
    data, address = server_socket.recvfrom(1024)
    data = data.decode()
    if not data:
        break
    if num == 0:
        print("Message from: " + str(address))
        print("Received : ")
        print(data)
        if data == "JR":
            data = "1"
            print("Sending: ")
            print(data)
            server_socket.sendto(data.encode(), address)
    num = (num+1)%100
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
