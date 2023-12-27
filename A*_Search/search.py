# 15 Puzzle AI using AStar search, with 2 different heuristic options, manhattan distance and number of misplaced tiles
# Tyler Strach - Fall 2023 - CS 411

from collections import deque
import os, time, resource, heapq
import psutil

# node struct for the tree 
class Node:
    # initializes a new node
    def __init__(self, state=None, prevCheepest=None, path=None, cost=None):
        self.state = state
        self.prevCheepest = prevCheepest;
        self.path = path
        self.cost = cost
    
    # copies data from other node
    def copy(self, node):
        self.state = node.state[:]
        self.path = node.path
        self.cost = node.cost
    
    # Define comparison method to compare nodes based on their costs
    def __lt__(self, other):
        return self.cost < other.cost

class Search:
    moves = [-4, 4, -1, 1] # change in index when empty space moves [UDLR]
    numNodes = 0 # number of nodes expanded in search
    solution_state = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0']
    wrong_states = {}
  
    # test if the goal state has been reached
    def goal_test(self, cur_tiles):
        return cur_tiles == self.solution_state
    
    # check if a valid move
    def isValidMove(self, position, move):
        if (position + move < 0) or (position + move > 15):
            return False
        else:
            return True
    
    # get the blank index
    def findBlank(self, state):
        index = 0
        for square in state:
            if int(square) == 0:
                return index
            index+=1

    # make the move and create a new node
    def makeMove(self, node, blank, move):
        tileSwapped = node.state[blank+move] 
        node.state[blank] = tileSwapped
        node.state[blank+move] = '0'

        if move == -4:
            node.path += 'U'
        elif move == 4:
            node.path += 'D'
        elif move == -1:
            node.path += 'L'
        else:
            node.path += 'R'

    # misplaced tiles hueristic function
    def misplaced(self, cur_state):
        hValue = 0;
        for i in range(16):
            if cur_state[i] != self.solution_state[i]:
                hValue += 1
        return hValue

    # manhattan distance hueristic function
    def manhattan(self, cur_state):
        hValue = 0;
        solution_x_y = {'1':(0,0), '2':(0,1), '3':(0,2), '4':(0,3),
                        '5':(1,0), '6':(1,1), '7':(1,2), '8':(1,3),
                        '9':(2,0), '10':(2,1), '11':(2,2), '12':(2,3),
                        '13':(3,0), '14':(3,1), '15':(3,2), '0':(3,3)}

        # finds the incorrect tiles
        for i in range(16):
            if cur_state[i] != self.solution_state[i]:
                self.wrong_states[cur_state[i]] = ()
        
        # finds the "x" and "y" values of the incorrect tiles
        k = 0;
        for i in range(4):
            for j in range(4):
                if cur_state[k] in self.wrong_states:
                    self.wrong_states[cur_state[k]] = (i, j)
                k += 1

        # for each incorrect tile, calculates the manhattan distance
        for tile in self.wrong_states:
            x_difference = abs((self.wrong_states[tile])[0] - (solution_x_y[tile])[0])
            y_difference = abs((self.wrong_states[tile])[1] - (solution_x_y[tile])[1])
            hValue += (x_difference + y_difference)

        return hValue
        
    # run the breadth-first-search and build a tree
    def run_AStar(self, starting_state, h):
        # create priority queue with start node only
        state = starting_state[:]
        startNode = Node(state, None, '', 0)
        pq = []
        heapq.heappush(pq, startNode)

        # holds the states visited (key) paired with the nodes (value) so that the cost may be updated when a more cost effecient path is found
        visitedStates = {} 

        # while there are unexpored nodes in the priority queue
        while pq:
            #pop least cost node and check for solution
            curNode = heapq.heappop(pq)
            Search.numNodes += 1
            if self.goal_test(curNode.state):
                return curNode.path
            
            blank = self.findBlank(curNode.state)

            # check all the 4 possible moves, and create new nodes
            for move in Search.moves:
                # only move if the move is possible
                if self.isValidMove(blank, move):
                    # Create a new node copy of the parent
                    newNode = Node()
                    newNode.copy(curNode)
                    newNode.prevCheepest = curNode # assign current node to the parent which is the current cheepest 

                    # uses desired h(n) function to calculate the cost of the move
                    additional_cost = 0
                    if h == "manhattan":
                        additional_cost = self.manhattan(newNode.state)
                    else:
                        additional_cost = self.misplaced(newNode.state)
                    
                    newNode.cost += additional_cost # update the new cost g(n) + h(n)
                    self.makeMove(newNode, blank, move) # make the move and change the state using transition function

                    # checks if this state has been seen before and if it has a less cost then originally
                    if tuple(newNode.state) in visitedStates:
                        if newNode.cost < visitedStates[tuple(newNode.state)].cost:
                            updateNode = visitedStates[tuple(newNode.state)]
                            updateNode.path = newNode.path
                            updateNode.cost = newNode.cost
                            updateNode.prevCheepest = newNode.prevCheepest
                    else:
                        visitedStates[tuple(newNode.state)] = newNode
                        heapq.heappush(pq, newNode)
        return "failure"
                    
    def solve(self, initial_state, heuristic='manhattan'): # Format : "1 0 2 4 5 7 3 8 9 6 11 12 13 10 14 15"
        # split into array and retrieve the heuristic value
        # initial_list, heuristic = initial_state.split("-")
        # initial_state = initial_list.split(" ")
        initial_list = initial_state.split(" ")
    
        # record times when doing the search
        startTime = time.time()
        solution_moves = self.run_AStar(initial_list, heuristic)
        endTime = time.time()
        runTime = endTime - startTime

        # get amount of data used
        target_pid = os.getpid()
        process = psutil.Process(target_pid)
        memoryUsage = process.memory_info().rss / (1024*1024)
       
        print("Moves: " + "".join(solution_moves))
        print("Number of expanded Nodes: " + str(Search.numNodes))
        print("Time Taken (sec): " + str(runTime))
        print("Max Memory Appx. (MB): " + str(memoryUsage))
        return "".join(solution_moves) # Get the list of moves to solve the puzzle. Format is "RDLDDRR"

if __name__ == '__main__':
    agent = Search()
    print("Please enter the starting position of the 15 puzzle board.")
    print("Ex: '1 0 2 4 5 7 3 8 9 6 11 12 13 10 14 15'")
    input = input()
    agent.solve(input)