from socket import socket as Socket

from pygame import Vector2

from geometry.rectangle import Rectangle

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




def process_server_message(message, player_id: int, player1: Rectangle, player2: Rectangle):
    """
        Processes the server message and acts accordingly:
            - Sets the other player's position
            - Updates the ball position if there is a big difference between the local and server position
            - When a score change is detected -> recenter the game
            - If the direction has been different for too long, change the direction as well as the ball position to the server's
        Args:
            - The packet received by the server
            - The ID of the player that is receiving the packet
            - Player 1 Object
            - Player 2 Object
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

    # TODO: HANDLE SCORE AND PACKET_NUM AND CORRECTIONS!!!
