import ipaddress
import socket
from socket import socket as Socket
import pygame
from pygame import Vector2

from logic.goal_manager import GoalManager
from logic.shape_controller import ShapeController
from logic.physics_system import PhysicsSystem

from tools import game_tools
from tools.game_tools import display_game_result, draw_game, print_game_result
from tools.networking_tools import process_server_message, send_client_message
from values import game_settings
from values import networking_settings

pygame.init()
text_font = pygame.font.SysFont("Courier New", game_settings.SCORE_SIZE)
clock = pygame.time.Clock()
delta_time = 0
pygame.display.quit()

player1 = game_tools.create_player_1()
player2 = game_tools.create_player_2()

player1_score = 0
player2_score = 0

ball = game_tools.create_ball()

terrain_lines = game_tools.VISUAL_create_terrain_lines()

# Walls Setup
wall_top = game_tools.create_top_wall()
wall_bottom = game_tools.create_bottom_wall()


time_since_different_ball_dir = 0
"""
    How long it has been that the Client has had a different Ball Direction than the Server
"""


def CLIENT_on_goal():
    ball.direction = Vector2(0, 0)
    ball.shape.set_position(game_settings.BALL_STARTING_POS)
    player1.set_position(game_settings.PLAYER1_STARTING_POS)
    player2.set_position(game_settings.PLAYER2_STARTING_POS)

    global goal_manager, player1_score, player2_score

    scores = goal_manager.get_player_scores()
    player1_score = int(scores.x)
    player2_score = int(scores.y)


# Goals Setup (No collisions)
goal_manager = GoalManager(
    [game_settings.PLAYER1_ID, game_settings.PLAYER2_ID],
    CLIENT_on_goal)

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
    """
        Handles joining a Server.
    """
    global joined_game, server, packet_number, player, player_id, player_controller

    client_socket.setblocking(True)
    server = None
    joined_game = False
    while not joined_game:
        try:
            # We ask the User for the server Address
            host = input(" Server IP (or \"q\" to quit) -> ").lower()
            if host == "q":
                print("Quitting...")
                client_socket.close()
                quit()
            # We Check if the IP is valid (ValueError thrown otherwise)
            ipaddress.ip_address(host)
            port = int(input(" Port -> "))
            server = (host, port)
        except ValueError:
            print("An invalid port was provided")
            continue

        number_of_tries = 0
        # We will wait 1 second per recvfrom to await a response from the Server
        client_socket.settimeout(1)
        # We send a Join Request (J) to the Server
        message = "J"
        message = message.encode()
        while number_of_tries <= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST and not joined_game:
            number_of_tries += 1
            client_socket.sendto(message, server)
            try:
                data, _ = client_socket.recvfrom(1024)
                data = data.decode()
                if data == "N":
                    print("This Server is Full.")
                    break
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
                    break
            except ConnectionResetError:
                print("ConnectionResetError (Server was probably not found)")
                break
            except socket.timeout:
                continue
        if number_of_tries > networking_settings.TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST:
            print("Connection to the Server could not be established")

    client_socket.settimeout(None)
    packet_number = 0

    # Once we have received our player ID, we now know who to control
    player_controller = ShapeController(
        player,
        {
            pygame.K_w: Vector2(0, -game_settings.PLAYER_SPEED),
            pygame.K_s: Vector2(0, game_settings.PLAYER_SPEED)
        },
        game_settings.PLAYER_MIN_Y_POS,
        game_settings.PLAYER_MAX_Y_POS)

    global player1_score, player2_score
    player1_score = 0
    player2_score = 0

    # Game View Setup
    global running, screen, time_since_last_packet
    pygame.display.init()
    screen = pygame.display.set_mode((
        game_settings.SCREEN_WIDTH,
        game_settings.SCREEN_HEIGHT
    ))
    running = True
    
    time_since_last_packet = 0
    
    # The game will not have started until we start receiving packets, so we just wait for one
    client_socket.recvfrom(1024)
    # We should NOT wait for packages for the game to look smooth
    client_socket.setblocking(False)


#############
# GAME PHASE
#############
handle_join_phase()  # Just to be 100% sure this runs atleast onece
while running:
    # This is here in case we disconnect from a Server
    if not joined_game:
        # We first dump all packets that we may have received
        client_socket.setblocking(True)
        client_socket.settimeout(1.5)
        while True:
            try:
                client_socket.recvfrom(1024)
            except TimeoutError:
                break
        client_socket.settimeout(None)
        handle_join_phase()
    # Main Game Loop
    else:
        latest_server_message_values = []
        time_since_last_packet += delta_time
        # We drain the buffer and get only the latest package (or Quit if we receive "Q")
        while True:
            try:
                server_message, _ = client_socket.recvfrom(1024)
                message_values = server_message.decode().split("|")

                if message_values and message_values[0] == "Q":
                    display_game_result(message_values)
                    joined_game = False
                    pygame.display.quit()
                    break

                # Index 5 is packet num
                if not latest_server_message_values or message_values[5] > latest_server_message_values[5]:
                    latest_server_message_values = message_values
            except BlockingIOError:
                break

        # We could have received a "Q" message
        if not running:
            break

        # If we received a package during this tick, process it
        if latest_server_message_values:
            time_since_last_packet = 0

            # We check if the Client Ball Direction is different from the Server's
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
        # If we go some time without receiving packets, we assume the connection was lost
        elif time_since_last_packet >= networking_settings.TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST:
            joined_game = False
            pygame.display.quit()
            print("Server connection was lost.")
            print_game_result(player1_score, player2_score)
            continue

        if pygame.display.get_active():
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
            print_game_result(player1_score, player2_score)
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
            player1_score, player2_score,
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