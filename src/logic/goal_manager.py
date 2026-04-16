from pygame import Vector2


class GoalManager:
    def __init__(self, player_ids_list: list[int], on_goal_func):
        self.__player_score_dic: dict[int, int] = dict()
        self.on_goal = on_goal_func
        for player_id in player_ids_list:
            self.__player_score_dic[player_id] = 0

    #################
    # Bandaid Methods
    #################

    def set_score(self, new_score: Vector2):
        self.__player_score_dic[1] = int(new_score.x)
        self.__player_score_dic[2] = int(new_score.y)
        self.on_goal()

    def get_player_scores(self) -> Vector2:
        return Vector2(self.__player_score_dic[1], self.__player_score_dic[2])

    #################
    #
    #################

    @DeprecationWarning
    def score(self, player_id: int):
        if player_id not in self.__player_score_dic:
            self.__player_score_dic[player_id] = 0
        self.__player_score_dic[player_id] += 1
        self.on_goal(player_id)

    @DeprecationWarning
    def get_player_score(self, player_id: int) -> int:
        return self.__player_score_dic[player_id]
