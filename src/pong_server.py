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
from tools.networking_tools import process_server_message, send_client_message
from values import game_settings


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
    #TODO: CHECK VALID IP
    server_started=True

# waiting for players to join
data, player1_address = server_socket.recvfrom(1024)
data=data.decode()
if data=="J":
    server_socket.sendto(str(1).encode(),player1_address )

data, player2_address = server_socket.recvfrom(1024)
data=data.decode()
if data=="J":
    server_socket.sendto(str(2).encode(),player2_address )



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

is_paused = False
time_since_pause = 0


#############
# GAME PHASE
#############
latest_server_message = None
while running:
    # We drain the buffer and get only the latest package
    while True:
        try:
            server_message, _ = client_socket.recvfrom(1024)
            latest_server_message = server_message
        except BlockingIOError:
            break
    # If we received a package during this tick, process it
    if latest_server_message:
        latest_server_message = latest_server_message.decode()  # type: ignore
        process_server_message(
            latest_server_message,
            player_id,
            player1,
            player2)

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with the colour black, wipes everything from last frame away
    screen.fill("black")
    if is_paused:
        pass

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