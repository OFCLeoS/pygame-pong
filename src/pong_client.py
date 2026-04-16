import socket
from socket import socket as Socket
import random
import pygame
from pygame import Vector2

from logic.goal_manager import GoalManager
from logic.shape_controller import ShapeController
from logic.physics_system import PhysicsSystem

from tools import game_tools
from tools.game_tools import draw_game
from tools.networking_tools import handle_server_connection_lost, process_server_message, send_client_message
from values import game_settings
from values import networking_settings

pygame.init()
text_font = pygame.font.SysFont("Courier New", game_settings.SCORE_SIZE)
clock = pygame.time.Clock()
delta_time = 0
pygame.display.quit()

player1 = game_tools.create_player_1()

player2 = game_tools.create_player_2()

ball = game_tools.create_ball()

terrain_lines = game_tools.VISUAL_create_terrain_lines()

# Walls Setup
wall_top = game_tools.create_top_wall()
wall_bottom = game_tools.create_bottom_wall()

time_since_different_ball_dir = 0


def recenter_game():
    ball.shape.set_position(game_settings.BALL_STARTING_POS)
    player1.set_position(game_settings.PLAYER1_STARTING_POS)
    player2.set_position(game_settings.PLAYER2_STARTING_POS)


# Goals Setup (No collisions)
goal_manager = GoalManager(
    [game_settings.PLAYER1_ID, game_settings.PLAYER2_ID],
    recenter_game)

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
        # Goals are decided by the Server!
        # goal_left.collider,
        # goal_right.collider
    ],
    [ball])

client_socket = Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def handle_join_phase():
    global joined_game, server, packet_number, player, player_id, player_controller
    joined_game = False

    client_socket.setblocking(True)
    server = None
    while not joined_game:
        # We ask the User for the server Address
        host = input(" Server IP (or \"q\" to quit) -> ")
        if host == "q":
            print("Quitting...")
            client_socket.close()
            quit()
        try:
            port = int(input(" Port -> "))
            server = (host, port)
        except ValueError:
            print("Invalid port was provided")
            continue

        # We send a Join Request (J) to the Server
        message = "J"
        client_socket.sendto(message.encode(), server)
        try:
            data, _ = client_socket.recvfrom(1024)
            data = data.decode()
            if data == "N":
                print("This Server is Full.")
            # We should have gotten an ID back at this point
            elif data == "1":
                player_id = 1
                player = player1
                joined_game = True
            elif data == "2":
                player_id = 2
                player = player2
                joined_game = True
            else:
                print(f"Invalid Packet Received: {data}")
                continue
        except ConnectionResetError:
            print("ConnectionResetError (Server was probably not found)")
            continue

    packet_number = 0

    player_controller = ShapeController(
        player,
        {
            pygame.K_w: Vector2(0, -game_settings.PLAYER_SPEED),
            pygame.K_s: Vector2(0, game_settings.PLAYER_SPEED)
        },
        game_settings.PLAYER_MIN_Y_POS,
        game_settings.PLAYER_MAX_Y_POS)

    # We should NOT wait for packages for the game to look smooth
    client_socket.setblocking(False)

    # Game Setup
    global running, screen, time_since_last_packet
    pygame.display.init()
    screen = pygame.display.set_mode((
        game_settings.SCREEN_WIDTH,
        game_settings.SCREEN_HEIGHT
    ))
    running = True
    time_since_last_packet = 0
    # TODO: READY MESSAGE


#############
# GAME PHASE
#############
handle_join_phase()  # Just to be 100% sure this runs atleast onece
while running:
    if not joined_game:
        # We first dump all packets that we may have received
        while True:
            try:
                client_socket.recvfrom(1024)
            except BlockingIOError:
                break
        handle_join_phase()
    # Main Game Loop
    else:
        latest_server_message_values = []
        time_since_last_packet += delta_time  # type: ignore
        # We drain the buffer and get only the latest package
        while True:
            try:
                server_message, _ = client_socket.recvfrom(1024)
                message_values = server_message.decode().split("|")

                # Index 5 is packet num
                if not latest_server_message_values or message_values[5] > latest_server_message_values[5]:
                    latest_server_message_values = message_values
            except BlockingIOError:
                break

        # If we received a package during this tick, process it
        if latest_server_message_values:
            time_since_last_packet = 0

            ball_direction_values = latest_server_message_values[1].split(",")
            ball_direction = Vector2(
                float(ball_direction_values[0]), float(ball_direction_values[1]))

            if ball_direction != ball.direction:
                time_since_different_ball_dir += delta_time
            else:
                time_since_different_ball_dir = 0

            process_server_message(
                latest_server_message_values,
                player_id,
                player1,
                player2,
                ball,
                time_since_different_ball_dir,
                goal_manager
            )

        elif time_since_last_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_ACTION:
            handle_server_connection_lost()

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with the colour black, wipes everything from last frame away
        screen.fill("black")

        keys = pygame.key.get_pressed()
        player_controller.handle_movement(keys)

        if keys[pygame.K_q]:
            if keys[pygame.K_LCTRL]:
                running = False
            joined_game = False
            pygame.display.quit()
            quit_message = "Q"
            client_socket.sendto(quit_message.encode(), server)  # type: ignore
            continue

        draw_game(
            screen,
            player1,
            player2,
            ball,
            terrain_lines,
            wall_top,
            wall_bottom,
            goal_left,
            goal_right,
            0, 0,  # TODO: SCORE
            text_font)

        physics_system.handle_physics()

        player_position = player.get_position()  # type: ignore
        send_client_message(
            client_socket,
            server,
            player_id,
            player_position.x,
            player_position.y,
            packet_number)
        packet_number += 1

        # Update the contents of the entire display
        pygame.display.flip()

        # Limits FPS to 60
        delta_time = clock.tick(60) / 1000

pygame.quit()
client_socket.close()

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
##############################
