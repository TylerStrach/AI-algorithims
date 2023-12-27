# 15 Puzzle AI using IDS
# Tyler Strach - Fall 2023 - CS 411

from collections import deque
import os, time, resource, psutil

# node struct for the tree 
class Node:
    # initializes a new node
    def __init__(self, state=None, parent=None, path=None, cost=None):
        self.state = state
        self.parent = parent
        self.path = path
        self.cost = cost
    
    # copies data from other node
    def copy(self, node):
        self.state = node.state[:]
        self.path = node.path
        self.cost = node.cost

class Search:
    moves = [-4, 4, -1, 1] # change in index when empty space moves [UDLR]
    numNodes = 0 # number of nodes expanded in search
  
    # test if the goal state has been reached
    def goal_test(self, cur_tiles):
        return cur_tiles == ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0']
    
    # check if a valid move
    def isValidMove(self, position, move):
        if (position + move < 0) or (position + move > 15):
            return False
        else:
            return True
        
    # checks is node is in a cycle
    def isCycle(self, node):
        seenNodes = {node}
        while(node.parent):
            node = node.parent
            if node in seenNodes:
                return True
            seenNodes.add(node)
        
        return False

    
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
        node.cost += 1
        
    # run the breadth-first-search and build a tree
    def run_ids(self, starting_state, depth):

        # root node store into frontier and check solution
        state = starting_state[:]
        startNode = Node(state, None, '', 0)
        Search.numNodes += 1
        if self.goal_test(startNode.state):
            return startNode.path
        
        frontier = deque([startNode]) # all the possible new nodes that have not been searched
        result = "failure"

        # while there are unexpored nodes in the queue
        while frontier:
            # get node and first check if it is a soltion...
            curNode = frontier.pop()
            Search.numNodes += 1
            if self.goal_test(curNode.state):
                return curNode.path
            
            # ...then checking the depth
            if curNode.cost > depth:
                result = "cutoff"
            elif not self.isCycle(curNode):

                # get the blank to expand 
                blank = self.findBlank(curNode.state)

                # check all the 4 possible moves, and create new nodes
                for move in Search.moves:
                    # only move if the move is possible
                    if self.isValidMove(blank, move):
                        newNode = Node()
                        newNode.copy(curNode)
                        newNode.parent = curNode # assign current node to the parent
                        self.makeMove(newNode, blank, move) # make the move and change the state using transition function
                        frontier.append(newNode)

        return result
                    
    def solve(self, input): # Format : "1 0 2 4 5 7 3 8 9 6 11 12 13 10 14 15"
        initial_list = input.split(" ")
    
        # record times when doing the search
        startTime = time.time()

        # perform the IDS search at depths 0-100
        for depth in range (0, 100):
            solution_moves = self.run_ids(initial_list, depth)
            if solution_moves != "cutoff":
                break

        endTime = time.time()
        runTime = endTime - startTime

        #get amount of data used
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