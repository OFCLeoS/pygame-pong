# Example file showing a circle moving on screen
import math
import pygame
from pygame import Vector2
from pygame import Color

from geometry.circle import Circle
from geometry.rectangle import Rectangle

from logic.shape_controller import ShapeController

BALL_SIZE = 15

RECT_WIDTH = 30
RECT_HEIGHT = 200

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1100, 900))
clock = pygame.time.Clock()
running = True
dt = 0

player1 = Rectangle(Vector2(RECT_WIDTH, RECT_HEIGHT), Vector2(screen.get_width(
) / 15, (screen.get_height() / 2)-(RECT_HEIGHT/2)), Color(255, 255, 255))

player2 = Rectangle(Vector2(RECT_WIDTH, RECT_HEIGHT), Vector2(screen.get_width(
)-(screen.get_width() / 15)-RECT_WIDTH, (screen.get_height() / 2)-(RECT_HEIGHT/2)), Color(255, 255, 255))


player1_controller = ShapeController(
    player1, {pygame.K_w: Vector2(0, -10), pygame.K_s: Vector2(0, 10)})

player2_controller = ShapeController(
    player2, {pygame.K_UP: Vector2(0, -5), pygame.K_DOWN: Vector2(0, 5)})

circle = Circle(BALL_SIZE, Vector2(player1.get_position().x+1,
                screen.get_height() / 2), Color(255, 255, 255))

movement = Vector2(0, 0)
while running:
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

    pygame.draw.circle(screen, circle.colour,
                       circle.get_position(), circle.radius)
    pygame.draw.rect(screen, player1.colour, player1.rect_like)
    pygame.draw.rect(screen, player2.colour, player2.rect_like)

    # TODO: Make middle just change y dir? and keep in mind player dir?

    circle.set_position((circle.get_position() + movement))
    if circle.get_position().y >= screen.get_height()-circle.radius:
        movement.y *= -1
    elif circle.get_position().y <= 0+circle.radius:
        movement.y *= -1
    elif circle.get_position().x <= 0+circle.radius:
        movement.x *= -1
    elif circle.get_position().x >= screen.get_width()-circle.radius:
        movement.x *= -1
    # PLAYER 1 RIGHT COLLISION
    elif circle.get_position().x <= player1.get_position().x + player1.rect_like.width+circle.radius and circle.get_position().x >= player1.get_position().x+circle.radius:
        print("HIT RIGHT")
        # Top Collision
        if circle.get_position().y >= player1.get_position().y and circle.get_position().y <= player1.get_position().y + (player1.rect_like.height/2):
            movement.x = abs(movement.x)
            movement.y = -abs(movement.y)
        # Bottom Collision
        elif circle.get_position().y > player1.get_position().y + (player1.rect_like.height/2) and circle.get_position().y <= player1.get_position().y + player1.rect_like.height:
            movement.x = abs(movement.x)
            movement.y = abs(movement.y)
    # PLAYER 1 LEFT COLLISION
    elif circle.get_position().x >= player1.get_position().x-circle.radius and circle.get_position().x <= player1.get_position().x + player1.rect_like.width-circle.radius:
        print("HIT LEFT")
        # Top Collision
        if circle.get_position().y >= player1.get_position().y and circle.get_position().y <= player1.get_position().y + (player1.rect_like.height/2):
            movement.x = -abs(movement.x)
            movement.y = -abs(movement.y)
        # Bottom Collision
        elif circle.get_position().y > player1.get_position().y + (player1.rect_like.height/2) and circle.get_position().y <= player1.get_position().y + player1.rect_like.height:
            movement.x = -abs(movement.x)
            movement.y = abs(movement.y)
    # PLAYER 1 TOP COLLISION
    elif circle.get_position().y >= player1.get_position().y-circle.radius and circle.get_position().y <= player1.get_position().y + player1.rect_like.height-circle.radius:
        # Right Collision
        print("HIT!!!")
        if circle.get_position().x >= player1.get_position().x+(player1.rect_like.width/2) and circle.get_position().x <= player1.get_position().x + player1.rect_like.width + circle.radius:
            print("HIT")
            movement.y = -abs(movement.y)
            movement.x = abs(movement.x)
            circle.set_position(
                Vector2(circle.get_position().x, player1.get_position().y-circle.radius))
        # Left Collision
        elif circle.get_position().x >= player1.get_position().x-circle.radius and circle.get_position().x < player1.get_position().x + (player1.rect_like.width/2):
            print("HIT")
            movement.y = -abs(movement.y)
            movement.x = -abs(movement.x)
            circle.set_position(
                Vector2(circle.get_position().x, player1.get_position().y-circle.radius))
    # PLAYER 1 BOTTOM COLLISION
    elif circle.get_position().y <= player1.get_position().y + player1.rect_like.height+circle.radius and circle.get_position().y >= player1.get_position().y+circle.radius:
        # Right Collision
        if circle.get_position().x >= player1.get_position().x+(player1.rect_like.width/2) and circle.get_position().x <= player1.get_position().x + player1.rect_like.width + circle.radius:
            movement.y = abs(movement.y)
            movement.x = abs(movement.x)
            circle.set_position(
                Vector2(circle.get_position().x, player1.get_position().y+player1.rect_like.height+circle.radius))
        # Left Collision
        elif circle.get_position().x >= player1.get_position().x-circle.radius and circle.get_position().x < player1.get_position().x + (player1.rect_like.width/2):
            movement.y = abs(movement.y)
            movement.x = -abs(movement.x)
            circle.set_position(
                Vector2(circle.get_position().x, player1.get_position().y+player1.rect_like.height+circle.radius))

    # elif circle.get_position().y <= 0+circle.radius:
    #     movement.y *= -1
    # elif circle.get_position().x <= 0+circle.radius:
    #     movement.x *= -1
    # elif circle.get_position().x >= screen.get_width()-circle.radius:
    #     movement.x *= -1

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
