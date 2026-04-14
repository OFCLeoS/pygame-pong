import socket


screen.fill("black")
if is_paused:
    time_since_pause += delta_time
    if time_since_pause >= PAUSE_TIME:
        time_since_pause = 0
        start_game()

keys = pygame.key.get_pressed()
player1_controller.handle_movement(keys)
player2_controller.handle_movement(keys)

draw_game()

    
physics_system.handle_physics()





host = input(" host -> ") 
port = int(input(" port -> "))   # socket server port number
server = (host,port)
client_socket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)  
message = input(" -> ")  # take input
test = input(" -> ")  # take input
while message.lower().strip() != 'bye':
    client_socket.sendto(message.encode(),server)  
    client_socket.sendto(test.encode(),server) 
    data,addr = client_socket.recvfrom(1024)
    data=data.decode()  # receive response
    print('Received from server: ') 
    print(data)  # show in terminal
    message = input(" -> ")  # again take input
    test = input(" -> ")  # again take input
client_socket.close()  # close the connection
