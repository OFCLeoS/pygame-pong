from socket import socket as Socket

from pygame import Vector2

from geometry.rectangle import Rectangle
from logic.goal_manager import GoalManager
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from values import networking_settings


def send_server_message(server_socket: Socket, client1, client2, ball_pos:Vector2,ball_dir:Vector2,player1_pos:Vector2,player2_pos:Vector2, score:Vector2 ,packet_number: int):
    # Message is formatted as follows: BALL_POS|BALL_DIR|PLAYER1_POS|PLAYER2_POS|SCORE|PACKET_NUM
    """
        Sends a server message from the provided socket to the provided client
    """
    message = f"{ball_pos.x},{ball_pos.y}|{ball_dir.x},{ball_dir.y}|{player1_pos.x},{player1_pos.y}|{player2_pos.x},{player2_pos.y}|{score.x},{score.y}|{packet_number}"
    server_socket.sendto(message.encode(), client1)
    server_socket.sendto(message.encode(), client2)
    
def send_client_message(client_socket: Socket, server, player_id: int, player_position_x, player_position_y, packet_number: int):
    """
        Sends a client message from the provided socket to the provided server
    """
    message = f"{player_id}|{player_position_x},{player_position_y}|{packet_number}"
    client_socket.sendto(message.encode(), server)


def process_server_message(message_values: list[str],
                           player_id: int,
                           player1: Rectangle,
                           player2: Rectangle,
                           ball: ShapeGamePhysicsObject,
                           time_since_different_ball_dir: float,
                           goal_manager: GoalManager
                           ):
    """
        Processes the server message and acts accordingly:
            - Sets the other player's position
            - Updates the ball position if there is a big difference between the local and server position
            - When a score change is detected -> recenter the game
            - If the direction has been different for too long, change the direction as well as the ball position to the server's
        Args:
            - The information received by the client
            - The ID of the player that is receiving the packet
            - Player 1 Object
            - Player 2 Object
            - Ball Object
            - The time since the Client's ball direction has been different from the Server's
            - The Goal Manager
    """

    # Message is formatted as follows: BALL_POS|BALL_DIR|PLAYER1_POS|PLAYER2_POS|SCORE|PACKET_NUM
    ball_position_values = message_values[0].split(",")
    server_ball_position = Vector2(
        float(ball_position_values[0]),
        float(ball_position_values[1])
    )

    if ball.direction.x == 0 and ball.direction.y == 0:
        # BALL DIRECTION AND POSITION SYNCING
        ball_direction_values = message_values[1].split(",")
        server_ball_direction = Vector2(
            float(ball_direction_values[0]), float(ball_direction_values[1]))
        ball.direction = server_ball_direction
        ball.shape.set_position(server_ball_position)
    elif time_since_different_ball_dir > networking_settings.ALLOWED_DIRECTION_ERROR_TIME:
        print("DIR CHANGED")
        # BALL DIRECTION AND POSITION SYNCING
        ball_direction_values = message_values[1].split(",")
        server_ball_direction = Vector2(
            float(ball_direction_values[0]), float(ball_direction_values[1]))
        ball.direction = server_ball_direction
        ball.shape.set_position(server_ball_position)
    elif Vector2.magnitude_squared(ball.shape.get_position() - server_ball_position) >= networking_settings.ALLOWED_SQUARDED_DISTANCE_ERROR:
        # BALL POSITION SYNCING
        ball.shape.set_position(server_ball_position)

    # PLAYER POSITION SYNCING
    if player_id == 1:
        player2_pos_values = message_values[3].split(",")
        server_player2_pos = Vector2(
            float(player2_pos_values[0]), float(player2_pos_values[1]))
        player2.set_position(server_player2_pos)
    else:
        player1_pos_values = message_values[2].split(",")
        server_player1_pos = Vector2(
            float(player1_pos_values[0]), float(player1_pos_values[1]))
        player1.set_position(server_player1_pos)

    score_values = message_values[4].split(",")
    server_scores = Vector2(int(float(score_values[0])), int(float(score_values[1])))
    if goal_manager.get_player_scores() != server_scores:
        goal_manager.set_score(server_scores)


def handle_client_connection_lost():
    pass


def handle_server_connection_lost():
    print("Server Is Not Sending Packets")
    pass
