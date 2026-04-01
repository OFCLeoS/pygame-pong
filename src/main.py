# Example file showing a circle moving on screen
import math
import pygame
from pygame import Vector2
from pygame import Color

from geometry.circle import Circle
from geometry.colliders.ball_collider import BallCollider
from geometry.colliders.paddle_collider import PaddleCollider
from geometry.rectangle import Rectangle

from logic.shape_controller import ShapeController
from logic.physics_system import PhysicsSystem
from logic.shape_game_physics_object import ShapeGamePhysicsObject


BALL_RADIUS = 15

RECT_WIDTH = 30
RECT_HEIGHT = 200

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1100, 900))
clock = pygame.time.Clock()
running = True
delta_time = 0

# Game Setup
player_size = Vector2(RECT_WIDTH, RECT_HEIGHT)

player1_starting_pos = Vector2(
    screen.get_width() / 15, (screen.get_height() / 2)-(RECT_HEIGHT/2))
player1_collider = PaddleCollider(Vector2(player1_starting_pos.x+(player_size.x/2),
                                  player1_starting_pos.y+(player_size.y/2)), Vector2(player_size.x/2, player_size.y/2))

player1 = Rectangle(player_size, player1_starting_pos,
                    Color(255, 255, 255), player1_collider)

player2_starting_pos = Vector2(screen.get_width(
)-(screen.get_width() / 15)-RECT_WIDTH, (screen.get_height() / 2)-(RECT_HEIGHT/2))
player2_collider = PaddleCollider(Vector2(player2_starting_pos.x+(player_size.x/2),
                                  player2_starting_pos.y+(player_size.y/2)), Vector2(player_size.x/2, player_size.y/2))

player2 = Rectangle(player_size, player2_starting_pos,
                    Color(255, 255, 255), player2_collider)

player1_controller = ShapeController(
    player1, {pygame.K_w: Vector2(0, -10), pygame.K_s: Vector2(0, 10)})

player2_controller = ShapeController(
    player2, {pygame.K_UP: Vector2(0, -5), pygame.K_DOWN: Vector2(0, 5)})

ball_starting_speed = Vector2(3, 3)
ball_starting_pos = Vector2(screen.get_width()/2, screen.get_height() / 2)
ball_collider = BallCollider(
    ball_starting_pos, Vector2(BALL_RADIUS, BALL_RADIUS))
ball = ShapeGamePhysicsObject(Circle(BALL_RADIUS, ball_starting_pos, Color(
    255, 255, 255), ball_collider), ball_starting_speed)


physics_system = PhysicsSystem(
    [player1.collider, player2.collider, ball.shape.collider], [ball])

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

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    keys = pygame.key.get_pressed()
    player1_controller.handle_movement(keys)
    player2_controller.handle_movement(keys)

    pygame.draw.circle(screen, ball.shape.colour,
                       ball.shape.get_position(), ball.shape.collider.extents.x)
    pygame.draw.rect(screen, player1.colour, player1.rect_like)
    pygame.draw.rect(screen, player2.colour, player2.rect_like)

    # TODO: Make middle just change y dir? and keep in mind player dir?

    physics_system.handle_physics()

    if ball.shape.get_position().y >= screen.get_height()-ball.shape.collider.extents.x:
        ball.direction.y *= -1
    elif ball.shape.get_position().y <= 0+ball.shape.collider.extents.x:
        ball.direction.y *= -1
    elif ball.shape.get_position().x <= 0+ball.shape.collider.extents.x:
        ball.direction.x *= -1
    elif ball.shape.get_position().x >= screen.get_width()-ball.shape.collider.extents.x:
        ball.direction.x *= -1

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # independent physics.
    delta_time = clock.tick(60) / 1000

pygame.quit()
