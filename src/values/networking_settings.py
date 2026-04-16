########
# SERVER
########


'''
The time a server can go without recceiving any packet from a client before the game is paused
'''
TIME_WITHOUT_PACKETS_BEFORE_PAUSE = 2

########
#
########

########
# CLIENT
########
'''
The maximum squared distance allowed for the ball that a client can have from
the client ball position to the server ball position before a correction is made
'''
ALLOWED_SQUARDED_DISTANCE_ERROR = 500

'''
The time a direction can be difference from the server in a client before a correction is made
'''
ALLOWED_DIRECTION_ERROR_TIME  = 0.1

'''
The time a client can go without recceiving any packet from the server before an action is taken
'''
TIME_WITHOUT_PACKETS_BEFORE_ACTION = 1.5