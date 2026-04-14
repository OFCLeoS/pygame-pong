import socket
import math
import random
import pygame
from pygame import Rect, Vector2, Color

from geometry.circle import Circle
from geometry.colliders.ball_collider import BallCollider
from geometry.colliders.goal_collider import GoalCollider
from geometry.colliders.paddle_collider import PaddleCollider
from geometry.colliders.wall_collider import WallCollider
from geometry.rectangle import Rectangle

from logic.goal_manager import GoalManager
from logic.shape_controller import ShapeController
from logic.physics_system import PhysicsSystem
from logic.shape_game_physics_object import ShapeGamePhysicsObject

from tools import game_tools
from values import game_settings


# pygame setup
pygame.init()
text_font = pygame.font.SysFont("Courier New", game_settings.SCORE_SIZE)
screen = pygame.display.set_mode(
    (game_settings.SCREEN_WIDTH, game_settings.SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
delta_time = 0

is_paused = False
time_since_pause = 0


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

def draw_game():
    # Draw Terrain
    for line in terrain_lines:
        pygame.draw.rect(screen, game_settings.TERRAIN_COLOUR, line)
    # Draw Score
    player1_score = str(
        goal_manager.get_player_score(game_settings.PLAYER1_ID))
    player2_score = str(
        goal_manager.get_player_score(game_settings.PLAYER2_ID))

    game_tools.draw_text(
        screen,
        player1_score,
        text_font, screen.get_width()/3.9,
        screen.get_height()/15)

    game_tools.draw_text(
        screen,
        player2_score,
        text_font,
        (screen.get_width()-(text_font.size(player2_score)
         [0])) - (screen.get_width()/3.9),
        screen.get_height()/15)

    # Draw Walls
    pygame.draw.rect(screen, wall_top.colour, wall_top.rect_like)
    pygame.draw.rect(screen, wall_bottom.colour, wall_bottom.rect_like)
    # Draw Goals
    pygame.draw.rect(screen, goal_left.colour, goal_left.rect_like)
    pygame.draw.rect(screen, goal_right.colour, goal_right.rect_like)
    # Draw Ball
    pygame.draw.circle(
        screen,
        ball.shape.colour,
        ball.shape.get_position(),
        ball.shape.collider.extents.x)

    # Draw Players
    pygame.draw.rect(screen, player1.colour, player1.rect_like)
    pygame.draw.rect(screen, player2.colour, player2.rect_like)


client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

################
# PROGRAM START
################

################
## JOINING PHASE
################
joined_game = False
while not joined_game:
    # We ask the User for the server
    host = input(" host -> ")
    port = int(input(" port -> "))
    server = (host, port)

    # We send a Join Request (JR) to the Server
    message = "JR"
    client_socket.sendto(message.encode(), server)
    data, addr = client_socket.recvfrom(1024)
    data = data.decode()

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


def send_client_message():
    global player_id
    global player
    global packet_number

    player_position = player.get_position()  # type: ignore
    message = f"{player_id}|{player_position.x},{player_position.y}|{packet_number}"
    client_socket.sendto(message.encode(), server)

    packet_number += 1


def process_server_message(message):
    """
        Processes the server message and acts accordingly:
            - Sets the other player's position
            - Updates the ball position if there is a big difference between the local and server position
            - When a score change is detected -> recenter the game
            - If the direction has been different for too long, change the direction as well as the ball position to the server's
        Args:
            The packet received by the server
    """

    # Message is formatted as follows: BALL_POS|BALL_DIR|PLAYER1_POS|PLAYER2_POS|SCORE|PACKET_NUM
    message_values = message.split("|")

    ball_position_values = message_values[0].split(",")
    ball_position = Vector2(
        float(ball_position_values[0]), float(ball_position_values[1]))

    ball_direction_values = message_values[1].split(",")
    ball_direction = Vector2(
        float(ball_direction_values[0]), float(ball_direction_values[1]))

    if player_id == 1:
        player2_pos_values = message_values[3].split(",")
        player2_pos = Vector2(
            float(player2_pos_values[0]), float(player2_pos_values[1]))
        player2.set_position(player2_pos)
    else:
        player1_pos_values = message_values[2].split(",")
        player1_pos = Vector2(
            float(player1_pos_values[0]), float(player1_pos_values[1]))
        player1.set_position(player1_pos)

    # TODO: HANDLE SCORE AND PACKET_NUM


# We should NOT wait for packages for the game to look smooth
client_socket.setblocking(False)

while running:

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

    latest_server_message = None
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
        process_server_message(latest_server_message)

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

    draw_game()

    physics_system.handle_physics()

    send_client_message()

    # Update the contents of the entire display
    pygame.display.flip()

    # Limits FPS to 60
    delta_time = clock.tick(60) / 1000

client_socket.close()
pygame.quit()
