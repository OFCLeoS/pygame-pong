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


player1 = game_tools.create_player_1()

player2 = game_tools.create_player_2()

ball = game_tools.create_ball()

terrain_lines = game_tools.VISUAL_create_terrain_lines()

# Walls Setup
wall_top = game_tools.create_top_wall()
wall_bottom = game_tools.create_bottom_wall()


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


def recenter_game():
    ball.shape.set_position(game_settings.BALL_STARTING_POS)
    player1.set_position(game_settings.PLAYER1_STARTING_POS)
    player2.set_position(game_settings.PLAYER2_STARTING_POS)


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


client_socket = Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

################
# GAME START
################

################
# JOINING PHASE
################
server = None
joined_game = False
while not joined_game:
    # We ask the User for the server Address
    host = input(" host -> ")
    try:
        port = int(input(" port -> "))
        server = (host, port)
    except ValueError:
        print("Invalid port was provided")
        continue

    # We send a Join Request (J) to the Server
    join_request = "J"
    client_socket.sendto(join_request.encode(), server)
    try:
        data, addr = client_socket.recvfrom(1024)
        data = data.decode()
    except ConnectionResetError:
        print("ConnectionResetError (Server was probably not found)")
        continue

    # If the game is
    if data == "N":
        print("This Server is Full.")
    else:
        joined_game = True

packet_number = 0

# We should have gotten an ID back at this point
player = None
player_id = 0
if data == "1":
    player_id = 1
    player = player1
else:
    player_id = 2
    player = player2

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

# pygame setup
pygame.init()
text_font = pygame.font.SysFont("Courier New", game_settings.SCORE_SIZE)
screen = pygame.display.set_mode(
    (game_settings.SCREEN_WIDTH,
     game_settings.SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
delta_time = 0

time_since_last_packet = 0

#############
# GAME PHASE
#############
latest_server_message_values: list[str] = []
while running:
    time_since_last_packet += delta_time

    # We drain the buffer and get only the latest package
    while True:
        try:
            server_message, _ = client_socket.recvfrom(1024)
            message_values = server_message.decode().split("|")

            # Index 5 is packet num
            if message_values[5] > latest_server_message_values[5]:
                latest_server_message_values = message_values
        except BlockingIOError:
            break

    # If we received a package during this tick, process it
    if latest_server_message_values:
        time_since_last_packet = 0
        process_server_message(
            latest_server_message_values,
            player_id,
            player1,
            player2)
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

    player_position = player.get_position()
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

client_socket.close()
pygame.quit()

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
