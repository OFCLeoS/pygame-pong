import socket
from socket import socket as Socket
import random
import time
from pygame import Vector2

from logic.goal_manager import GoalManager
from logic.shape_controller import ShapeController
from logic.physics_system import PhysicsSystem

from tools import game_tools
from tools.networking_tools import send_server_message
from values import game_settings

player1 = game_tools.create_player_1()

player2 = game_tools.create_player_2()

ball = game_tools.create_ball()

terrain_lines = game_tools.VISUAL_create_terrain_lines()

# Walls Setup
wall_top = game_tools.create_top_wall()
wall_bottom = game_tools.create_bottom_wall()

last_goal_player_id = random.randint(1,2)

def on_goal(last_goal_id: int):
    # TODO: MODIFY THIS FOR CLIENT
    global last_goal_player_id
    last_goal_player_id = last_goal_id
    ball.shape.set_position(game_settings.BALL_STARTING_POS)
    player1.set_position(game_settings.PLAYER1_STARTING_POS)
    player2.set_position(game_settings.PLAYER2_STARTING_POS)
    pause_game()


def pause_game():
    global is_paused
    is_paused = True
    ball.direction.x = 0
    ball.direction.y = 0


def start_game():
    global is_paused
    is_paused = False
    coefficient = random.uniform(-1, 1)
    ball.direction.x = game_settings.BALL_STARTING_X_SPEED if last_goal_player_id % 2 != 0 else - \
        game_settings.BALL_STARTING_X_SPEED
    ball.direction.y = game_settings.BALL_STARTING_Y_SPEED * coefficient

# Goals Setup
goal_manager = GoalManager(
    [game_settings.PLAYER1_ID, game_settings.PLAYER2_ID],
    on_goal)

goal_left = game_tools.create_left_goal(goal_manager)
goal_right = game_tools.create_right_goal(goal_manager)

# PHYSICS SYSTEM
physics_system = PhysicsSystem(
    [
        player1.collider,
        player2.collider,
        ball.shape.collider,
        wall_top.collider,
        wall_bottom.collider,
        goal_left.collider,
        goal_right.collider
    ],
    [ball])

################
# SERVER START
################
server_socket = Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_started = False  
server = None
while not server_started:
    # We ask the User for the server Address
    host = input(" host -> ")
    try:
        port = int(input(" port -> "))
    except ValueError:
        print("Invalid port was provided")
        continue
    
    server = (host, port)
    server_socket.bind(server)
    print("Server started")
    #TODO: CHECK VALID IP
    server_started=True

player1_address=None
player2_address=None

game_ready=False
player1_joined=False
while not game_ready:
# waiting for players to join
    if not player1_joined:
        data, player1_address = server_socket.recvfrom(1024)
        data=data.decode()
        if data=="J":
            server_socket.sendto(str(1).encode(),player1_address )
            player1_joined=True
    else:
        data, player2_address = server_socket.recvfrom(1024)
        data=data.decode()
        if data=="J":
            server_socket.sendto(str(2).encode(),player2_address )
            game_ready=True

packet_number_p1 = 0
packet_number_p2 = 0
packet_number_server=0

# We should NOT wait for packages for the game to look smooth
server_socket.setblocking(False)

target_fps = 60
frame_time = 1 / target_fps
last_time = time.perf_counter()

running = True
is_paused = False
time_since_pause = 0

#############
# GAME PHASE
#############
latest_server_message = None
pause_game()
while running:
    start_time = time.perf_counter()

    delta_time = start_time - last_time
    last_time = start_time
    
    latest_player1_position_message=""
    latest_player2_position_message=""
    # We drain the buffer and get only the latest package
    while True:
        try:
            # recieves from client: player_id|player_position_x,player_position_y|packet_number
            client_message, adress = server_socket.recvfrom(1024)
            client_message=client_message.decode()
            client_message_list=client_message.split("|")
            player_id=int(client_message_list[0])
            player_position=client_message_list[1]
            client_packet_number=int(client_message[2])
            old_packet_number_p1=0
            old_packet_number_p2=0
            
            if player_id==1 and  client_packet_number > old_packet_number_p1 :
                latest_player1_position_message = client_message_list[1]
                old_packet_number_p1=client_packet_number
            
            if player_id==2 and  client_packet_number > old_packet_number_p2 :
                latest_player2_position_message = client_message_list[1]
                old_packet_number_p2=client_packet_number

        except BlockingIOError:
            break
    
    if latest_player1_position_message:
        latest_player1_message_x=float(latest_player1_position_message.split(",")[0])
        latest_player1_message_y=float(latest_player1_position_message.split(",")[1])
        player1_position=Vector2(latest_player1_message_x,latest_player1_message_y)
        player1.set_position(player1_position)
    if latest_player2_position_message:
        latest_player2_message_x=float(latest_player2_position_message.split(",")[0])
        latest_player2_message_y=float(latest_player2_position_message.split(",")[1])
        player2_position=Vector2(latest_player2_message_x,latest_player2_message_y)
        player2.set_position(player2_position)

    if is_paused:
        time_since_pause += delta_time
        if time_since_pause >= game_settings.PAUSE_TIME:
            time_since_pause = 0
            start_game()
    else: physics_system.handle_physics()
    
    send_server_message(server_socket,player1_address,player2_address,ball.shape.get_position(),ball.direction,player1.get_position(),player2.get_position(),goal_manager.get_player_scores(),packet_number_server)
    packet_number_server+=1
    print(packet_number_server)
    
    elapsed = time.perf_counter() - start_time
    sleep_time = frame_time - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)
    
server_socket.close()