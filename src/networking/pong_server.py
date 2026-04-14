import socket
import time

from pygame import Vector2


def process_client_message(message):
    """
        Processes the client message and acts accordingly:
            TODO SERVER
        Args:
            The packet received by the client
    """
    # Message is formatted as follows: ID|POSITION|PACKET_NUM
    message_values = message.split("|")

    id = int(message_values[0])

    player_position_values = message_values[1].split(",")

    if id == 1:
        global player1_pos
        player1_pos = f"{player_position_values[0]},{player_position_values[1]}"
    else:
        global player2_pos
        player2_pos = f"{player_position_values[0]},{player_position_values[1]}"

    # TODO PACKAGE CHECK

# Message is formatted as follows: BALL_POS|BALL_DIR|PLAYER1_POS|PLAYER2_POS|SCORE|PACKET_NUM


def get_game_state_message() -> str:
    return f"200,200|10,5|{player1_pos}|{player2_pos}|0,0|0"


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

while not player2_joined:
    message, address = server_socket.recvfrom(1024)
    message = message.decode()
    if not message:
        break
    if not player1_joined:
        if message == "JR":
            message = "1"
            print("Sending: ")
            print(message)
            player1_address = address
            server_socket.sendto(message.encode(), address)
            player1_joined = True
    elif not player2_joined:
        if message == "JR":
            message = "2"
            print("Sending: ")
            print(message)
            player2_address = address
            server_socket.sendto(message.encode(), address)
            player2_joined = True

server_socket.setblocking(False)

while True:
    try:
        message, address = server_socket.recvfrom(1024)
        message = message.decode()
        if message:
            process_client_message(message)
    except BlockingIOError:
        pass
    
    game_state_message = get_game_state_message()
    game_state_message = game_state_message.encode()
    server_socket.sendto(game_state_message,player1_address) # type: ignore
    server_socket.sendto(game_state_message,player2_address) # type: ignore
    if num == 0:
        print("Message from: " + str(address))
        print("Received : ")
        print(message)
    num = (num+1) % 100
    time.sleep(1/60)

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