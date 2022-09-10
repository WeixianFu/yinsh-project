

import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
import json
import math

THINKTIME = 0.8
diagPoints = [(0,0), (0,0), (0,0), (0,0), (2,6), (1,7), (0,7), (0,7), (0,7), (0,6), (1,5)]
EPSI = 0.4
ALPHA = 0.1
GAMMA = 0.9
CORNER_POINTS = [(0,6), (1,4), (4,1), (6,0), (9,0), (10,1), (10,4), (9,5), (6,9), (4,10), (1,10), (0,9)]


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#


class myAgent():
    def __init__(self, _id):
        self.id = _id  # Agent needs to remember its own id.
        self.oppo_id = 1 if self.id == 0 else 0
        self.game_rule = YinshGameRule(2)  # Agent stores an instance of GameRule, from which to obtain functions.
        self.weights = [1, 0.1, -0.1, 0.2]
        self.round = 0
        self.ring_color = 2 * self.id + 1
        self.oppo_ring_color = 3 - 2 * self.id
        self.counter_color = 2 * self.id + 2
        self.oppo_counter_color = 4 - 2 * self.id
        with open("agents/t_006/astar_heuristic.json", "r", encoding='utf-8') as f:
            self.hValue = json.load(f)
        with open("agents/t_006/rl_weights_bfs.json", "r", encoding='utf-8') as f:
            self.weights = json.load(f)["weight"]
        # print(f"weights is {self.weights}")



    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    # Carry out a given action on this state and return the difference of score
    def DoAction_flip(self, state, action):
        score = state.agents[self.id].score
        before_act_board = "".join(map(str, state.board)) # new feature 1
        flip_diff_before_act = before_act_board.count(str(self.counter_color)) - before_act_board.count(str(self.oppo_counter_color)) # new feature 1
        state = self.game_rule.generateSuccessor(state, action, self.id)
        after_act_board = "".join(map(str, state.board))  # new feature 1
        flip_diff_after_act = after_act_board.count(str(self.counter_color)) - after_act_board.count(str(self.oppo_counter_color))  # new feature 1
        # action
        if state.agents[self.id].score - score > 0:
            flip_num = 0
        else:
            flip_num = (flip_diff_before_act - flip_diff_after_act)/15
        return [state.agents[self.id].score - score, flip_num]

    # Carry out a given action on this state and return the difference of score
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score - score

    def get_other_center_action(self, action_list, root_state):
        state = deepcopy(root_state)
        my_ring_pos = state.ring_pos[self.id]
        for action in action_list:
            flag = True
            if action["type"] == "place ring":
                y1, x1 = action["place pos"]
                y = abs(5 - y1)
                x = abs(5 - x1)

                if (y == 1 and x == 0) or (y == 0 and x == 1) or (x == 1 and y == 1 and (x1 + y1 == 10)):
                    for ring_pos in my_ring_pos:
                        if ring_pos != (5, 5):
                            y2, x2 = ring_pos
                            if (y1 == y2 and x1 != x2) or (x1 == x2 and y1 != y2):
                                flag = False
                            elif (y1, x1) in [(y2 + i, x2 - i) for i in range(-10, 11)
                                              if (0 <= y2 + i <= 10 and 0 <= x2 - i <= 10)]:
                                flag = False
                            else:
                                flag = True
                else:
                    flag = False
            if flag:
                return action
        return random.choice(action_list)

    def place_ring(self, action_list, root_state):
        if self.round == 1:
            center = [a for a in action_list if a["place pos"] == (5, 5)]
            if center:
                return center[0]
            else:
                return self.get_other_center_action(action_list, root_state)
        elif self.round == 5:
            return random.choice(action_list)
        else:
            return self.get_other_center_action(action_list, root_state)

    def CalHValueFeature(self, board, id):
        ring_color = str(2 * id + 1)
        counter_color = str(2 * id + 2)
        return_value = 0
        # vertical
        for x in range(11):
            for y in range(7):
                value_ver = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x, y+1)]) + str(board[(x, y+2)]) + str(board[(x, y+3)]) + str(board[(x, y+4)])
                if place_5 in self.hValue:
                    if place_5.count(ring_color) > 0:
                        value_ver += 5
                    value_ver += 6-self.hValue[place_5]
                return_value = max(return_value, value_ver)
        # vertical
        for x in range(7):
            for y in range(11):
                value_hor = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x + 1, y)]) + str(board[(x + 2, y)]) + str(board[(x + 3, y)]) + str(board[(x + 4, y)])
                if place_5 in self.hValue:
                    if place_5.count(ring_color) > 0:
                        value_hor += 5
                    value_hor += 6 - self.hValue[place_5]
                return_value = max(return_value, value_hor)
        # diagonal
        for x in range(4, 11):
            for y in range(7):
                value_dia = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x - 1, y + 1)]) + str(board[(x - 2, y + 2)]) + str(board[(x - 3, y + 3)]) + str(board[(x - 4, y + 4)])
                if place_5 in self.hValue:
                    if place_5.count(ring_color) > 0:
                        value_dia += 5
                    value_dia += 6 - self.hValue[place_5]
                return_value = max(return_value, value_dia)
        return return_value

    def CalRingsFeature(self, state):
        ring_pos = state.ring_pos[self.id]
        ring_x_pos = [i[0] for i in ring_pos]
        ring_y_pos = [i[1] for i in ring_pos]
        ring_x_plus_y_pos = [i[0]+i[1] for i in ring_pos]
        return len(set(ring_x_pos)) + len(set(ring_y_pos)) + len(set(ring_x_plus_y_pos))

    def CalCornerFeauture(self, board):
        c1 = 0
        o1 = 0
        for pos in CORNER_POINTS:
            if board[pos] == self.counter_color:
                c1 += 1
            elif board[pos] == self.oppo_counter_color:
                o1 += 1
        return [c1/12, o1/12]


    # Generates actions from this state.
    def GetLegalProp(self, state):
        self_actions = self.game_rule.getLegalActions(state, self.id)
        oppo_actions = self.game_rule.getLegalActions(state, self.oppo_id)

        return len(self_actions)/(len(self_actions)+len(oppo_actions))



    def CalFeatures(self, state, action):

        self_counter_color = str(self.counter_color)
        oppo_counter_color = str(self.oppo_ring_color)
        features = []
        #
        next_state = deepcopy(state)
        score = self.DoAction_flip(next_state, action)
        features.extend(score) # new feature

        # score = self.DoAction(next_state, action)
        # features.append(score)  # new feature
        #
        t_board = "".join(map(str, next_state.board))
        features.append(t_board.count(str(self_counter_color))/51)
        features.append(t_board.count(str(oppo_counter_color))/51)

        # features.append(self.CalRemainStepsFeature(next_state.board)/21)
        # print(state.rings_won[self.id])
        features.append(self.CalHValueFeature(next_state.board, self.id)/11)
        features.append(self.CalHValueFeature(next_state.board, self.oppo_id)/11)

        # features.append(self.CalRingsFeature(next_state)/(3*(5 - state.rings_won[self.id])))
        # features.extend(self.CalCornerFeauture(next_state.board))
        # features.append(self.GetLegalProp(next_state))
        # print(features)
        return features

    def CalQValue(self, state, action):
        features = self.CalFeatures(state, action)
        if len(features) != len(self.weights):
            return -math.inf
        else:
            ans = 0
            for i in range(len(features)):
                ans += features[i] * self.weights[i]
            return ans

    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to reward, if any was found.
    def SelectAction(self, actions, rootstate):
        self.round += 1
        start_time = time.time()
        best_Q_value = - math.inf
        best_action = random.choice(actions)
        if self.round <= 5:
            return self.place_ring(actions, rootstate)
        if random.uniform(0,1) <1 - EPSI:
            for action in actions:
                if time.time()-start_time > THINKTIME:
                    break
                Q_value = self.CalQValue(deepcopy(rootstate), action)
                if Q_value > best_Q_value:
                    best_Q_value = Q_value
                    best_action = action
        else:
            best_Q_value = self.CalQValue(deepcopy(rootstate), best_action)

        next_state = deepcopy(rootstate)
        reward = self.DoAction(next_state, best_action)

        next_actions = self.GetActions(next_state)
        best_Q_value_next = -math.inf
        c = 0
        for action in next_actions:
            c += 1
            if time.time()-start_time>THINKTIME:
                break
            Q_value = self.CalQValue(deepcopy(next_state), action)
            best_Q_value_next = max(best_Q_value_next, Q_value)

        features = self.CalFeatures(deepcopy(rootstate), best_action)
        delta_value = reward + GAMMA * best_Q_value_next - best_Q_value
        # print('---------------------')
        # print(c)
        # print(reward)
        # print(best_Q_value_next)
        # print(best_Q_value)
        # print(delta_value)
        # print(self.weights)
        # print(features)
        # print(f'1 use {time.time()-start_time}')
        # print('---------------------')
        for i in range(len(features)):
            self.weights[i] += ALPHA * delta_value * features[i]

        with open("agents/t_006/rl_weights_bfs.json", "w", encoding='utf-8') as f:
            json.dump({"weight": self.weights}, f, indent=4, ensure_ascii=False)
        return best_action


