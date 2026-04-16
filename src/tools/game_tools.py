from pygame import Color, Font, Rect, Surface, Vector2
import pygame

from geometry.circle import Circle
from geometry.colliders.ball_collider import BallCollider
from geometry.colliders.goal_collider import GoalCollider
from geometry.colliders.paddle_collider import PaddleCollider
from geometry.colliders.wall_collider import WallCollider
from geometry.rectangle import Rectangle

from logic.goal_manager import GoalManager
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from values import game_settings


def draw_text(screen: Surface, text: str, text_font: Font, x, y):
    txt = text_font.render(text, True, game_settings.SCORE_COLOUR)
    screen.blit(txt, (x, y))


def create_player_1() -> Rectangle:
    player1_collider = PaddleCollider(
        Vector2(game_settings.PLAYER1_STARTING_POS.x+(game_settings.PLAYER_WIDTH/2),
                game_settings.PLAYER1_STARTING_POS.y+(game_settings.PLAYER_HEIGHT/2)),
        Vector2(game_settings.PLAYER_WIDTH/2, game_settings.PLAYER_HEIGHT/2))
    return Rectangle(
        game_settings.PLAYER_SIZE,
        game_settings.PLAYER1_STARTING_POS,
        Color(255, 255, 255),
        player1_collider)


def create_player_2() -> Rectangle:
    player2_collider = PaddleCollider(
        Vector2(game_settings.PLAYER2_STARTING_POS.x+(game_settings.PLAYER_WIDTH/2),
                game_settings.PLAYER2_STARTING_POS.y+(game_settings.PLAYER_HEIGHT/2)),
        Vector2(game_settings.PLAYER_WIDTH/2,
                game_settings.PLAYER_HEIGHT/2))

    return Rectangle(
        game_settings.PLAYER_SIZE,
        game_settings.PLAYER2_STARTING_POS,
        Color(255, 255, 255),
        player2_collider)


def create_ball() -> ShapeGamePhysicsObject:
    ball_collider = BallCollider(
        game_settings.BALL_STARTING_POS,
        Vector2(
            game_settings.BALL_RADIUS,
            game_settings.BALL_RADIUS))
    return ShapeGamePhysicsObject(
        Circle(
            game_settings.BALL_RADIUS,
            game_settings.BALL_STARTING_POS,
            Color(255, 255, 255),
            ball_collider),
        Vector2(0, 0))


def create_top_wall() -> Rectangle:
    wall_top_pos = Vector2(0, 0)
    wall_top_collider = WallCollider(
        Vector2(
            game_settings.SCREEN_WIDTH/2,
            game_settings.WALL_THICKNESS/2),
        Vector2(
            game_settings.TOP_BOTTOM_WALL_SIZE.x/2,
            game_settings.TOP_BOTTOM_WALL_SIZE.y/2))

    return Rectangle(
        game_settings.TOP_BOTTOM_WALL_SIZE,
        wall_top_pos,
        game_settings.WALL_COLOUR,
        wall_top_collider)


def create_bottom_wall() -> Rectangle:
    wall_bottom_pos = Vector2(
        0, game_settings.SCREEN_HEIGHT-game_settings.WALL_THICKNESS)
    wall_bottom_collider = WallCollider(
        Vector2(
            game_settings.SCREEN_WIDTH/2,
            wall_bottom_pos.y+(game_settings.WALL_THICKNESS/2)),
        Vector2(
            game_settings.TOP_BOTTOM_WALL_SIZE.x/2,
            game_settings.TOP_BOTTOM_WALL_SIZE.y/2))

    return Rectangle(
        game_settings.TOP_BOTTOM_WALL_SIZE,
        wall_bottom_pos,
        game_settings.WALL_COLOUR,
        wall_bottom_collider)


def create_left_goal(goal_manager: GoalManager) -> Rectangle:
    goal_left_pos = Vector2(0, 0)
    goal_left_collider = GoalCollider(
        Vector2(
            game_settings.WALL_THICKNESS/2,
            game_settings.SCREEN_HEIGHT/2),
        Vector2(
            game_settings.LEFT_RIGHT_GOAL_SIZE.x/2,
            game_settings.LEFT_RIGHT_GOAL_SIZE.y/2),
        game_settings.PLAYER2_ID,
        goal_manager)

    return Rectangle(
        game_settings.LEFT_RIGHT_GOAL_SIZE,
        goal_left_pos,
        game_settings.WALL_COLOUR,
        goal_left_collider)


def create_right_goal(goal_manager: GoalManager) -> Rectangle:
    goal_right_pos = Vector2(
        game_settings.SCREEN_WIDTH-game_settings.WALL_THICKNESS, 0)

    goal_right_collider = GoalCollider(
        Vector2(
            goal_right_pos.x+(game_settings.WALL_THICKNESS/2),
            game_settings.SCREEN_HEIGHT/2),
        Vector2(
            game_settings.LEFT_RIGHT_GOAL_SIZE.x/2,
            game_settings.LEFT_RIGHT_GOAL_SIZE.y/2),
        game_settings.PLAYER1_ID,
        goal_manager)

    return Rectangle(
        game_settings.LEFT_RIGHT_GOAL_SIZE,
        goal_right_pos,
        game_settings.WALL_COLOUR,
        goal_right_collider)


def VISUAL_create_terrain_lines() -> list[Rect]:
    terrain_line_height = (game_settings.SCREEN_HEIGHT /
                           game_settings.TERRAIN_LINE_COUNT)-game_settings.TERRAIN_SPACE_BETWEEM_LINES
    terrain_lines: list[Rect] = list()
    for i in range(game_settings.TERRAIN_LINE_COUNT+1):
        terrain_lines.append(
            Rect(Vector2((game_settings.SCREEN_WIDTH/2)-(game_settings.TERRAIN_LINE_WIDTH/2),
                         ((terrain_line_height+game_settings.TERRAIN_SPACE_BETWEEM_LINES) * i)+(game_settings.TERRAIN_SPACE_BETWEEM_LINES/2)),
                 Vector2(game_settings.TERRAIN_LINE_WIDTH,
                         terrain_line_height)))
    return terrain_lines


def draw_game(screen: Surface,
              player1: Rectangle,
              player2: Rectangle,
              ball: ShapeGamePhysicsObject,
              terrain_lines: list[Rect],
              wall_top: Rectangle,
              wall_bottom: Rectangle,
              goal_left: Rectangle,
              goal_right: Rectangle,
              player1_score: int,
              player2_score: int,
              text_font: Font):
    # Draw Terrain
    for line in terrain_lines:
        pygame.draw.rect(screen, game_settings.TERRAIN_COLOUR, line)
    # Draw Score

    draw_text(
        screen,
        str(player1_score),
        text_font, screen.get_width()/3.9,
        screen.get_height()/15)

    draw_text(
        screen,
        str(player2_score),
        text_font,
        (screen.get_width()-(text_font.size(str(player1_score))
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
