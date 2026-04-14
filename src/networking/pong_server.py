import socket
import pygame





host = input(" host -> ")
port = int(input(" port -> "))
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.bind((host, port))
print("Server Started")
while True:
    
    
    data, address = server_socket.recvfrom(1024)
    client_message,address= server_socket.recvfrom(1024)
    data = data.decode('utf-8')
    client_message=str(client_message.decode("utf-8",))
    if not data:
        break
    print("Message from: " + str(address))
    print("Received : ")
    print(data)
    print(client_message)
    data = data.upper()
    client_message_list = client_message.split("|")
    print(client_message_list)
    server_message = str(ball_position) +"|"+str(ball_direction)+"|"+str(player_position)+"|"+str(player_position2)+"|"+str(score)
    
    print("Sending: ")
    print(data)
    print(server_message)
    server_socket.sendto(data.encode('utf-8'), address)
    server_socket.sendto(server_message.encode('utf-8'),address)
    
    
    
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
pygame.init()
screen = pygame.display.set_mode((1500, 900))
screen.fill("black")
