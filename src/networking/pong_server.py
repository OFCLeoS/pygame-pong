import socket
host = input(" host -> ")
port = int(input(" port -> "))
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.bind((host, port))
print("Server Started")

player1_joined = False
player2_joined = False
num = 0

player1_pos = "100,100"
player2_pos = "100,100"

player1_address = None
player2_address = None

while True:
    data, address = server_socket.recvfrom(1024)
    data = data.decode()
    if not data:
        break
    if not player1_joined:
        if data == "JR":
            data = "1"
            print("Sending: ")
            print(data)
            player1_address = address
            server_socket.sendto(data.encode(), address)
        player1_joined = True
    elif not player2_joined:
        if data == "JR":
            data = "2"
            print("Sending: ")
            print(data)
            player2_address = address
            server_socket.sendto(data.encode(), address)
        player2_joined = True
    else:
        
        if num == 0:
            print("Message from: " + str(address))
            print("Received : ")
            print(data)
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
