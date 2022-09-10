from template import Agent
import random
import time
from Yinsh.yinsh_model import YinshGameRule
from collections import defaultdict
import copy
import numpy as np

THINK_TIME = 0.9
C_PARAMETER = 5
DISCOUNT = 0.8
CORNER_POINTS = [(0,6), (1,4), (4,1), (6,0), (9,0), (10,1), (10,4), (9,5), (6,9), (4,10), (1,10), (0,9)]
VERTEX_POINTS = [(1,5),(5,1), (9,1),(9,5),(5,9),(1,9)]
GAME_RULE = YinshGameRule(2)

def is_terminal_node(current_state):
    """
    Determining whether a node is terminated
    """
    if current_state.counters_left == 0:
        return True
    deadlock = 0
    for agent in current_state.agents:
        deadlock += 1 if agent.passed else 0
        if agent.score == 3:
            return True
    return deadlock == len(current_state.agents)

def compute_rewards(current_state):
    """
    Calculating the rewards in the current state
    """
    agent_1_score = GAME_RULE.calScore(current_state, 1)
    agent_0_score = GAME_RULE.calScore(current_state, 0)
    if agent_0_score > agent_1_score:
        return 0, 1
    elif agent_0_score == agent_1_score:
        return 0, 0
    elif agent_0_score < agent_1_score:
        return 1, 1

class Node():
    def __init__(self, my_agent_id, state_agent_id, action_agent_id, current_state, parent_node=None, move=None):
        self.my_agent_id = my_agent_id
        self.state_agent_id = state_agent_id
        self.action_agent_id = action_agent_id
        self.state = copy.deepcopy(current_state)
        self.parent = parent_node
        self.move = move # parent_node + move => current_node
        self.children_list = []
        self.untried_action_list = GAME_RULE.getLegalActions(copy.deepcopy(self.state), self.action_agent_id)

        self.N = 0
        self.Q = 0

    def q(self):
        return self.Q

    def n(self):
        return self.N

    def is_fully_expanded(self):
        return len(self.untried_action_list) == 0

    def traverse(self):
        current_node = self
        while not is_terminal_node(current_node.state):
            if current_node.is_fully_expanded():
                # If fully expanded, select the child node with the largest uct for expansion
                current_node = current_node.get_most_uct_node()
            else:
                return current_node.get_an_unvisited_node()
        return current_node

    def get_most_uct_node(self):
        # calculate uct
        ust_list = [((float(child.q()) / child.n()) + C_PARAMETER * np.sqrt(2 * (np.log(self.n())) / child.n()))
                    for child in self.children_list]
        return self.children_list[np.argmax(ust_list)]

    def get_an_unvisited_node(self):
        # If not fully extended, a child node is selected at random.
        random.shuffle(self.untried_action_list)
        action = self.untried_action_list.pop()
        agent_id = self.action_agent_id
        state = copy.deepcopy(self.state)
        next_state = GAME_RULE.generateSuccessor(state, action, agent_id)
        opp_id = 0 if agent_id == 1 else 1
        child_node = Node(self.my_agent_id, state_agent_id=agent_id, action_agent_id=opp_id,
                          current_state=next_state, parent_node=self, move=action)
        self.children_list.append(child_node)
        return child_node

    def rollout(self):
        current_node = self
        current_state = copy.deepcopy(current_node.state)
        action_agent_id = self.action_agent_id

        counter = 0
        while not is_terminal_node(current_state) and counter < 10:
            # Narrow the range to 10 steps to increase the number of simulations.
            counter += 1
            legal_action_list = GAME_RULE.getLegalActions(current_state, action_agent_id)
            sequence = [a for a in legal_action_list if "remove" in a["type"]]
            if sequence:
                # If sequences are available, seqeunce is preferred for extension.
                action = sequence[np.random.randint(len(sequence))]
                current_state = GAME_RULE.generateSuccessor(current_state, action, action_agent_id)
                return compute_rewards(current_state)
            else:
                action = legal_action_list[np.random.randint(len(legal_action_list))]
                current_state = GAME_RULE.generateSuccessor(current_state, action, action_agent_id)
            action_agent_id = 0 if action_agent_id == 1 else 1
        return compute_rewards(current_state)

    def back_propagation(self, won_agent_id, result):
        self.N += 1
        if self.state_agent_id == won_agent_id:
            if result == 0:
                result = -0.5 # Penalty Tie
            self.Q += DISCOUNT * result
        else:
            if result == 0:
                result = 0.5 # Penalty Tie
            self.Q -= DISCOUNT * result

        if self.parent:
            self.parent.back_propagation(won_agent_id, result)

    def best_action(self):
        # Select the node with the best Q value
        q_list = [child.q() for child in self.children_list]
        best_child = self.children_list[np.argmax(q_list)]

        return best_child.move

class myAgent():
    def __init__(self, _id):
        self.id = _id
        self.rings_to_place = 5

    def monte_carlo_tree_search(self, start_time, root_node):
        # main function
        while time.time() - start_time < THINK_TIME:
            leaf_node = root_node.traverse()
            won_id, simulation_result = leaf_node.rollout()
            leaf_node.back_propagation(won_id, simulation_result)
        return root_node.best_action()

    def get_other_center_action(self, action_list, root_state):
        state = copy.deepcopy(root_state)
        my_ring_pos = state.ring_pos[self.id]
        for action in action_list:
            flag = True
            if action["type"] == "place ring":
                y1, x1 = action["place pos"]
                y = abs(5 - y1)
                x = abs(5 - x1)
                # Determine if it is located close to the centre
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

    def get_random_board_edge(self, action_list):
        random.shuffle(action_list)
        for action in action_list:
            if action["type"] == "place ring":
                position = action["place pos"]
                if position in CORNER_POINTS + VERTEX_POINTS:
                    # Select a random position on the edge for placement
                    return action

    def place_ring(self, action_list, root_state):
        if self.rings_to_place == 5:
            # Seize the centre
            center = [a for a in action_list if a["place pos"] == (5, 5)]
            self.rings_to_place -= 1
            if center:
                return center[0]
            else:
                # Place the pieces in other positions close to the centre.
                return self.get_other_center_action(action_list, root_state)
        elif self.rings_to_place == 1:
            self.rings_to_place -= 1
            # prevent edge-first strategy
            return self.get_random_board_edge(action_list)
        else:
            self.rings_to_place -= 1
            # Place the pieces in other positions close to the centre.
            return self.get_other_center_action(action_list, root_state)

    def SelectAction(self, actions, root_state):
        # At the stage of placing the ring
        play_ring = [a for a in actions if "ring" in a["type"]]
        if play_ring:
            return self.place_ring(play_ring, root_state)

        # If there is a seqeunce, form the sequence first
        sequence = [a for a in actions if "remove" in a["type"]]
        if sequence:
            return sequence[np.random.randint(len(sequence))]
        else:
            start_time = time.time()
            opp_id = 0 if self.id == 1 else 1
            root_node = Node(self.id, opp_id, self.id, root_state)
            # do mcts
            return self.monte_carlo_tree_search(start_time, root_node)
