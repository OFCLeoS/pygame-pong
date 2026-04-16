TIME_WITHOUT_PACKETS_BEFORE_CONNECTION_LOST = 10
'''
The time a machine can go without recceiving any packet before the connection is deemed lost
'''

########
# SERVER
########


TIME_WITHOUT_PACKETS_BEFORE_PAUSE = 2
'''
The time a server can go without recceiving any packet from a client before the game is paused
'''

########
#
########

########
# CLIENT
########

ALLOWED_SQUARDED_DISTANCE_ERROR = 500
'''
The maximum squared distance allowed for the ball that a client can have from
the client ball position to the server ball position before a correction is made
'''

ALLOWED_DIRECTION_ERROR_TIME  = 0.1
'''
The time a direction can be difference from the server in a client before a correction is made
'''

TIME_WITHOUT_PACKETS_BEFORE_ACTION = 1.5
'''
The time a client can go without recceiving any packet from the server before an action is taken
'''