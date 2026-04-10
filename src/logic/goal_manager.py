class GoalManager:
    def __init__(self, player_ids_list: list[int], on_goal_func):
        self.__player_score_dic: dict[int, int] = dict()
        self.on_goal = on_goal_func
        for player_id in player_ids_list:
            self.__player_score_dic[player_id] = 0

    def score(self, player_id: int):
        if player_id not in self.__player_score_dic:
            self.__player_score_dic[player_id] = 0
        self.__player_score_dic[player_id] += 1
        self.on_goal(player_id)
        
    def get_player_score(self,player_id: int) -> int:
        return self.__player_score_dic[player_id]
