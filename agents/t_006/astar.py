
import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from queue import PriorityQueue
from collections import defaultdict
import math
import heapq
import json

THINKTIME = 0.80


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#

class MyPriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id  # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2)  # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        with open("agents/astar_heuristic.json", "r", encoding='utf-8') as f:
            self.hValue = json.load(f)

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score - score

    def CalHValue(self, board, id):
        ring_color = str(2 * id + 1)
        counter_color = str(2 * id + 2)
        return_value = 51
        # vertical
        for x in range(11):
            for y in range(7):
                value_ver = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x, y + 1)]) + str(board[(x, y + 2)]) + str(
                    board[(x, y + 3)]) + str(board[(x, y + 4)])
                if place_5 in self.hValue:
                    value_ver = self.hValue[place_5]
                return_value = min(return_value, value_ver)
        # vertical
        for x in range(7):
            for y in range(11):
                value_hor = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x + 1, y)]) + str(board[(x + 2, y)]) + str(
                    board[(x + 3, y)]) + str(board[(x + 4, y)])
                if place_5 in self.hValue:
                    value_hor = self.hValue[place_5]
                return_value = min(return_value, value_hor)
        # diagonal
        for x in range(4, 11):
            for y in range(7):
                value_dia = 0
                place_5 = str(id) + str(board[(x, y)]) + str(board[(x - 1, y + 1)]) + str(board[(x - 2, y + 2)]) + str(
                    board[(x - 3, y + 3)]) + str(board[(x - 4, y + 4)])
                if place_5 in self.hValue:
                    value_dia = self.hValue[place_5]
                return_value = min(return_value, value_dia)
        return return_value

    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to reward, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        closed = set()
        best_g = defaultdict(int)
        # queue = deque([(deepcopy(rootstate), [])])  # Initialise queue. First node = root state and an empty path.
        score = rootstate.agents[self.id].score
        pqueue = MyPriorityQueue()
        pqueue.push((deepcopy(rootstate), []), 0)
        c = 0
        # Conduct BFS starting from rootstate.
        while not pqueue.isEmpty() and time.time() - start_time < THINKTIME:
            (state, path) = pqueue.pop()  # Pop the next node (state, path) in the PriorityQueue.
            state_str = re.sub(r'\D', "", "".join(map(str, state.board)))
            if (not state_str in closed) or (len(path) < best_g[state_str]):
                closed.add(state_str)
                best_g[state_str]=len(path)
                new_actions = self.GetActions(state)  # Obtain new actions available to the agent in this state.
                for a in new_actions:
                    next_state = deepcopy(state)
                    next_path = path + [a]
                    score = self.DoAction(next_state, a)
                    if score:
                        return next_path[0]
                    else:
                        pqueue.push((deepcopy(next_state), next_path), len(next_path) + self.CalHValue(next_state.board, self.id) + 1)
        return random.choice(actions)  # If no reward was found in the time limit, return a random action.


