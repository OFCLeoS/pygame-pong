# Example file showing a circle moving on screen
import math
import random
import pygame
from pygame import Rect, Vector2
from pygame import Color

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

##################
# GAME SETTINGS
##################
BALL_RADIUS = 15
BALL_STARTING_X_SPEED = 10
BALL_STARTING_Y_SPEED = 20

PLAYER1_ID = 1
PLAYER2_ID = 2
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 200
PLAYER_SPEED = 20

TERRAIN_LINE_WIDTH = 9
TERRAIN_LINE_COUNT = 10
TERRAIN_SPACE_BETWEEM_LINES = 20
TERRAIN_COLOUR = Color(155, 155, 155)

WALL_THICKNESS = 15
WALL_COLOUR = Color(100, 100, 100)

SCORE_SIZE = 200
SCORE_COLOUR = Color(255, 255, 255)

PAUSE_TIME = 1.5
##################
#
##################

# pygame setup
pygame.init()
text_font = pygame.font.SysFont("Courier New", SCORE_SIZE)
screen = pygame.display.set_mode((1500, 900))
clock = pygame.time.Clock()
running = True
delta_time = 0

is_paused = False
time_since_pause = 0
last_goal_player_id = 0


def draw_text(text, x, y):
    txt = text_font.render(text, True, SCORE_COLOUR)
    screen.blit(txt, (x, y))

# Game Setup
player_size = Vector2(PLAYER_WIDTH, PLAYER_HEIGHT)

# Player 1 Setup
player1_starting_pos = Vector2(
    screen.get_width() / 15, (screen.get_height() / 2)-(PLAYER_HEIGHT/2))
player1_collider = PaddleCollider(Vector2(player1_starting_pos.x+(player_size.x/2),
                                  player1_starting_pos.y+(player_size.y/2)), Vector2(player_size.x/2, player_size.y/2))

player1 = Rectangle(player_size, player1_starting_pos,
                    Color(255, 255, 255), player1_collider)

# Player 2 Setup
player2_starting_pos = Vector2(screen.get_width(
)-(screen.get_width() / 15)-PLAYER_WIDTH, (screen.get_height() / 2)-(PLAYER_HEIGHT/2))
player2_collider = PaddleCollider(Vector2(player2_starting_pos.x+(player_size.x/2),
                                  player2_starting_pos.y+(player_size.y/2)), Vector2(player_size.x/2, player_size.y/2))

player2 = Rectangle(player_size, player2_starting_pos,
                    Color(255, 255, 255), player2_collider)

# TODO: MOVEMENT CONSTRAINITS?
# Player Controllers
player_min_y_pos = WALL_THICKNESS
player_max_y_pos = int(screen.get_height()-player_size.y - WALL_THICKNESS)

player1_controller = ShapeController(
    player1, {pygame.K_w: Vector2(0, -PLAYER_SPEED), pygame.K_s: Vector2(0, PLAYER_SPEED)},player_min_y_pos,player_max_y_pos)

player2_controller = ShapeController(
    player2, {pygame.K_UP: Vector2(0, -PLAYER_SPEED), pygame.K_DOWN: Vector2(0, PLAYER_SPEED)},player_min_y_pos,player_max_y_pos)

# Ball Setup
ball_starting_speed = Vector2(10, 3)
ball_starting_pos = Vector2(screen.get_width()/2, screen.get_height() / 2)
ball_collider = BallCollider(
    ball_starting_pos, Vector2(BALL_RADIUS, BALL_RADIUS))
ball = ShapeGamePhysicsObject(Circle(BALL_RADIUS, ball_starting_pos, Color(
    255, 255, 255), ball_collider), ball_starting_speed)

# Terrain Setup
terrain_line_height = (screen.get_height() /
                       TERRAIN_LINE_COUNT)-TERRAIN_SPACE_BETWEEM_LINES
terrain_lines: list[Rect] = list()
for i in range(TERRAIN_LINE_COUNT+1):
    terrain_lines.append(
        Rect(Vector2((screen.get_width()/2)-(TERRAIN_LINE_WIDTH/2),
                     ((terrain_line_height+TERRAIN_SPACE_BETWEEM_LINES) * i)+(TERRAIN_SPACE_BETWEEM_LINES/2)),
             Vector2(TERRAIN_LINE_WIDTH,
                     terrain_line_height)))

# Walls Setup
top_bottom_wall_size = Vector2(screen.get_width(), WALL_THICKNESS)
wall_top_pos = Vector2(0, 0)
wall_top_collider = WallCollider(Vector2(screen.get_width()/2,
                                         WALL_THICKNESS/2),
                                 Vector2(top_bottom_wall_size.x/2,
                                         top_bottom_wall_size.y/2))

wall_top = Rectangle(top_bottom_wall_size, wall_top_pos,
                     WALL_COLOUR, wall_top_collider)

wall_bottom_pos = Vector2(0, screen.get_height()-WALL_THICKNESS)
wall_bottom_collider = WallCollider(Vector2(screen.get_width()/2,
                                            wall_bottom_pos.y+(WALL_THICKNESS/2)),
                                    Vector2(top_bottom_wall_size.x/2,
                                            top_bottom_wall_size.y/2))

wall_bottom = Rectangle(top_bottom_wall_size, wall_bottom_pos,
                        WALL_COLOUR, wall_bottom_collider)


def on_goal(last_goal_id: int):
    global last_goal_player_id
    last_goal_player_id = last_goal_id
    ball.shape.set_position(ball_starting_pos)
    player1.set_position(player1_starting_pos)
    player2.set_position(player2_starting_pos)
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
    ball.direction.x = BALL_STARTING_X_SPEED if last_goal_player_id % 2 != 0 else - \
        BALL_STARTING_X_SPEED
    ball.direction.y = BALL_STARTING_Y_SPEED * coefficient


# Goals Setup
goal_manager = GoalManager([PLAYER1_ID, PLAYER2_ID], on_goal)

left_right_goal_size = Vector2(WALL_THICKNESS, screen.get_height())
goal_left_pos = Vector2(0, 0)
goal_left_collider = GoalCollider(Vector2(WALL_THICKNESS/2,
                                          screen.get_height()/2),
                                  Vector2(left_right_goal_size.x/2,
                                          left_right_goal_size.y/2),
                                  PLAYER2_ID,
                                  goal_manager)

goal_left = Rectangle(left_right_goal_size, goal_left_pos,
                      WALL_COLOUR, goal_left_collider)

goal_right_pos = Vector2(screen.get_width()-WALL_THICKNESS, 0)
goal_right_collider = GoalCollider(Vector2(goal_right_pos.x+(WALL_THICKNESS/2),
                                           screen.get_height()/2),
                                   Vector2(left_right_goal_size.x/2,
                                           left_right_goal_size.y/2),
                                   PLAYER1_ID,
                                   goal_manager)

goal_right = Rectangle(left_right_goal_size, goal_right_pos,
                       WALL_COLOUR, goal_right_collider)
# PHYSICS SYSTEM
physics_system = PhysicsSystem(
    [player1.collider, player2.collider, ball.shape.collider, wall_top_collider, wall_bottom_collider, goal_left_collider, goal_right_collider], [ball])


last_goal_player_id = random.randint(1,2)
pause_game()
def draw_game():
    # Draw Terrain
    for line in terrain_lines:
        pygame.draw.rect(screen, TERRAIN_COLOUR, line)
    # Draw Score
    player1_score = str(goal_manager.get_player_score(PLAYER1_ID))
    player2_score = str(goal_manager.get_player_score(PLAYER2_ID))

    draw_text(player1_score, screen.get_width()/3.9, screen.get_height()/15)
    draw_text(player2_score, (screen.get_width()-(text_font.size(player2_score)[0])) -
              (screen.get_width()/3.9), screen.get_height()/15)

    # Draw Walls
    pygame.draw.rect(screen, wall_top.colour, wall_top.rect_like)
    pygame.draw.rect(screen, wall_bottom.colour, wall_bottom.rect_like)
    # Draw Goals
    pygame.draw.rect(screen, goal_left.colour, goal_left.rect_like)
    pygame.draw.rect(screen, goal_right.colour, goal_right.rect_like)
    # Draw Ball
    pygame.draw.circle(screen, ball.shape.colour,
                       ball.shape.get_position(), ball.shape.collider.extents.x)
    # Draw Players
    pygame.draw.rect(screen, player1.colour, player1.rect_like)
    pygame.draw.rect(screen, player2.colour, player2.rect_like)


while running:

    # NETWORKING ARCHITECTURE HERE
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

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with the colour black, wipes everything from last frame away
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

    # TODO: Make middle just change y dir? and keep in mind player dir?
    physics_system.handle_physics()

    # Update the contents of the entire display
    pygame.display.flip()

    # Limits FPS to 60
    delta_time = clock.tick(60) / 1000

pygame.quit()
