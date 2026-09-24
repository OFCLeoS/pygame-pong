# Overview
A multiplayer 2-player game of Infinite Pong. It follows the classical rules of Pong but runs until a
player leaves.

Players control one paddle each. They must stop the ball from entering in their goal, but must
make the ball enter the other player’s goal.
Hitting a goal with the ball gives a point to the player opposite of the goal.

# Requirements
- python 3.14+
- pygame-ce
- socket

# How to play
- Run “pong_client.py” to start a client, or/and “pong_server.py” to
start a server.
## Client Setup
Enter a valid server address. If successfully connected, the game
will start once a second client connects.

### Controls
- W to move the paddle up
- S to move the paddle down.
- Q to disconnect from the server.
- CTRL+Q to quit the game.

## Server Setup
Enter a valid IPV4 address as well as an unused port (use 49152 to 65535).
