import ipaddress
import socket
from socket import socket as Socket
import random
import time
from pygame import Vector2

from logic.goal_manager import GoalManager
from logic.physics_system import PhysicsSystem

from tools import game_tools
from tools.networking_tools import send_server_message, send_server_quit_message
from values import game_settings, networking_settings

player1 = game_tools.create_player_1()

player2 = game_tools.create_player_2()

ball = game_tools.create_ball()

terrain_lines = game_tools.VISUAL_create_terrain_lines()

# Walls Setup
wall_top = game_tools.create_top_wall()
wall_bottom = game_tools.create_bottom_wall()

# This will decide where the ball goes to at first
last_goal_player_id = random.randint(1, 2)


def on_goal(last_goal_id: int):
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
    # If we use start_game and the ball direction is 0,0, we assume we want to start the next round
    if ball.direction == Vector2(0, 0):
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
    try:
        # We ask the User for the server Address
        host = input(" Server IP (or \"q\" to quit) -> ").lower()
        if host == "q":
            print("Quitting...")
            server_socket.close()
            quit()
        # We Check if the IP is valid (ValueError thrown otherwise)
        ipaddress.ip_address(host)
        port = int(input(" Port -> "))
        server = (host, port)
        server_socket.bind(server)
    except ValueError:
        print("An invalid address was provided")
        continue
    except OSError:
        print("The address provided is not valid in its context")
        continue

    print("Server has Started")
    server_started = True

player1_address = None
player2_address = None

game_ready = False
player1_joined = False
while not game_ready:
    # waiting for players to join
    if not player1_joined:
        try:
            data, player1_address = server_socket.recvfrom(1024)
            data = data.decode()
            if data == "J":
                server_socket.sendto(str(1).encode(), player1_address)
                player1_joined = True
        except ConnectionResetError:
            print("A Player has left the game")
            break
    else:
        try:
            data, player2_address = server_socket.recvfrom(1024)
            data = data.decode()
            if data == "J":
                server_socket.sendto(str(2).encode(), player2_address)
                game_ready = True
            elif data == "Q":
                # If Player 1 leaves, we have to wait for a Player 1 again
                player1_joined = False
        except ConnectionResetError:
            print("A Player has left the game")
            # If Player 1 leaves, we have to wait for a Player 1 again
            player1_joined = False
            break

# We should NOT wait for packages for the game to look smooth
server_socket.setblocking(False)

packet_number_p1 = 0
packet_number_p2 = 0

packet_number_server = 0
latest_server_message = None

time_since_last_player1_packet = 0
time_since_last_player2_packet = 0

# IPS -> Iterations Per Second
target_ips = 60
iteration_time = 1 / target_ips
last_time = time.perf_counter()

running = True
is_paused = False
time_since_pause = 0

#############
# GAME PHASE
#############
pause_game()
while running:
    start_time = time.perf_counter()

    delta_time = start_time - last_time
    last_time = start_time

    latest_player1_position_message = None
    latest_player2_position_message = None
    # We drain the buffer and get only the latest package
    while True:
        # Server Packet Handling
        try:
            # Receives from Client: player_id|player_position_x,player_position_y|packet_number
            client_message, address = server_socket.recvfrom(1024)
            client_message = client_message.decode()

            if client_message == "Q":
                # We Stop the game if "Q" is received, since a Player left
                send_server_quit_message(
                    server_socket, player1_address, player2_address, goal_manager.get_player_scores())
                running = False
                break
            elif client_message == "J":
                refuse_message = "N"
                server_socket.sendto(refuse_message.encode(),address)
                continue

            client_message_list = client_message.split("|")

            player_id = int(client_message_list[0])
            client_packet_number = int(client_message[2])

            if player_id == 1 and (not latest_player1_position_message or client_packet_number > packet_number_p1):
                latest_player1_position_message = client_message_list[1]
                packet_number_p1 = client_packet_number
            elif player_id == 2 and (not latest_player2_position_message or client_packet_number > packet_number_p2):
                latest_player2_position_message = client_message_list[1]
                packet_number_p2 = client_packet_number
        except BlockingIOError:
            break
        except ConnectionResetError:
            # We Stop the game since one of the players left
            send_server_quit_message(
                server_socket, player1_address, player2_address, goal_manager.get_player_scores())
            running = False
            break

    time_since_last_player1_packet += delta_time
    time_since_last_player2_packet += delta_time

    if latest_player1_position_message:
        time_since_last_player1_packet = 0
        latest_player1_message_x = float(
            latest_player1_position_message.split(",")[0])
        latest_player1_message_y = float(
            latest_player1_position_message.split(",")[1])
        player1_position = Vector2(
            latest_player1_message_x, latest_player1_message_y)
        player1.set_position(player1_position)
    elif time_since_last_player1_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_PAUSE:
        # If we reach here, it means that Player 1 is having some possible connection issues
        if not is_paused:
            pause_game()
    elif time_since_last_player1_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST:
        # If we reach here, we assume Player 1 has lost it's connection to the Server
        send_server_quit_message(
            server_socket,
            player1_address,
            player2_address,
            goal_manager.get_player_scores()
        )
        running = False
        break
    
    # Same Thing as above, but with Player 2
    if latest_player2_position_message:
        time_since_last_player2_packet = 0
        latest_player2_message_x = float(
            latest_player2_position_message.split(",")[0])
        latest_player2_message_y = float(
            latest_player2_position_message.split(",")[1])
        player2_position = Vector2(
            latest_player2_message_x, latest_player2_message_y)
        player2.set_position(player2_position)
    elif time_since_last_player2_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_PAUSE:
        if not is_paused:
            pause_game()
    elif time_since_last_player2_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST:
        # We Stop the game
        send_server_quit_message(
            server_socket,
            player1_address,
            player2_address,
            goal_manager.get_player_scores()
        )
        running = False
        break

    if is_paused:
        time_since_pause += delta_time
        if time_since_pause >= game_settings.PAUSE_TIME:
            time_since_pause = 0
            start_game()
    else:
        physics_system.handle_physics()

    send_server_message(
        server_socket,
        player1_address,
        player2_address,
        ball.shape.get_position(),
        ball.direction,
        player1.get_position(),
        player2.get_position(),
        goal_manager.get_player_scores(),
        packet_number_server
    )
    packet_number_server += 1

    elapsed = time.perf_counter() - start_time
    sleep_time = iteration_time - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)

server_socket.close()