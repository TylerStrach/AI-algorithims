import re

class MDP:
    # MDP object and all its needed data parameters
    def __init__(self, rows=0, columns=0, states=None, walls=[], term_states={}, T=[], reward=0, gamma=0, epsilon=0, final_policy=[]):
        self.rows = rows # = y
        self.columns = columns # = x
        self.states = states # list of states (x, y)
        self.walls = walls # states with walls
        self.term_states = term_states # terminal states and their rewards {(x, y) : ''}

        self.reward = reward # non-terminal transition reward
        self.moves = ['U', 'D', 'L', 'R']
        self.T = T # transition probabilites [U, L, R, D]
        self.gamma = gamma # discount factor/rate
        self.epsilon = epsilon #  maximum error allowed

        self.final_policy = final_policy # final policy achieved after iteraton
 
    # read input from the file describing the MDP
    def readInput(self):
        # open file
        with open(input, 'r') as file:
            for line in file:
                line = line.strip()
                # skips enpty lines and comments
                if not line:
                    continue
                if "#" in line:
                    continue
                
                # creates row x column list
                if "size" in line:
                    # Use a regular expression to find all numbers in the line
                    numbers = [int(match.group()) for match in re.finditer(r'\d+', line)]
                    self.columns = numbers[0]
                    self.rows = numbers[1]

                    # populate the array with the coordinates of each space
                    states = []
                    x = 1
                    y = self.rows
                    for i in range(self.columns * self.rows):
                        if x is self.columns:
                            states.append((x,y))
                            x = 1
                            y -= 1
                        else:
                            states.append((x,y))
                            x += 1
                    self.states = states
                            
                # sets walls to ignore in value iteration
                if "walls" in line:
                    numbers = [int(match.group()) for match in re.finditer(r'\d+', line)]
                    i = 0
                    wallColumns = []
                    wallRows = []
                    for num in numbers:
                        if i%2 == 0:
                            wallColumns.append(num)
                        else:
                            wallRows.append(num)
                        i += 1

                    # replaces 0 in matrix
                    for i in range (len(wallColumns)):
                        self.walls.append((wallColumns[i], wallRows[i]))
                    
                # list of terminal states and their values
                if "terminal_states" in line:
                    values = line.split(":", 1)[1].split(",")
    
                    for set in values:
                        tVal = set.split(" ")
                        tVal = [item for item in tVal if item != '']
                        self.term_states[(int(tVal[0]), int(tVal[1]))] = float(tVal[2])
            
                # cost of a transition to a non terminal state
                if "reward" in line:
                    reward = line.split(":", 1)[1].split(" ")
                    self.reward = float(reward[1])
                
                # probabilites when making a move 
                if "transition_probabilities" in line:
                    values = line.split(":", 1)[1].split(" ")
                    values = [item for item in values if item != ''] # strip to only values
                    for value in values:
                        self.T.append(float(value))
                
                # gamma value
                if "discount_rate" in line:
                    dRate = line.split(":", 1)[1].split(" ")
                    self.gamma = float(dRate[1])

                # epsilon value
                if "epsilon" in line:
                    eps = line.split(":", 1)[1].split(" ")
                    self.epsilon = float(eps[1])
        
    # print MDP description
    def print(self):
        mdp = ""

        # row x column
        mdp += f"({self.rows}, {self.columns}, ["

        # walls [x= y= ,]
        i = 1
        for pair in self.walls:
            if i == len(self.walls):
                mdp += f"x= {pair[0]} y= {pair[1]}], "
                mdp += "{"
            else: 
                mdp += f"x= {pair[0]} y= {pair[1]}, "
            i += 1
        
        # term states
        i = 1
        for key in self.term_states:
            if i == len(self.term_states):
                mdp += f"x= {key[0]} y= {key[1]}: {self.term_states[key]}"
                mdp += "}, "
            else:
                mdp += f"x= {key[0]} y= {key[1]}: {self.term_states[key]}, "
            i += 1
        
        # transition cost
        mdp += f"{self.reward}, '"

        # transition probabilites
        i = 1
        for num in self.T:
            if i == len(self.T):
                mdp += f"{num}', "
            else:
                mdp += f"{num} "
            i += 1
            
        # gamma
        mdp += f"{self.gamma}, "

        # epsilon
        mdp += f"{self.epsilon})"

        print(mdp)

    # gets all possible squares we can end up in after a move
    def move_calculator(self, coords, move):
        # new (coord, reward) pairs to hold the new states we might land in
        straightTile = ()
        leftTile = ()
        rightTile = ()
        backTile = ()

        # list [U, L, R, D] to hold the new states of those moves
        newStates = []

        newCoords = list(coords)
        # we can move 4 different directions, each direction have chances to go in 3 (max 4) different directions
        if move == 'U':
            straightTile = ((newCoords[0], newCoords[1] + 1), self.reward)
            leftTile = ((newCoords[0] - 1, newCoords[1]), self.reward)
            rightTile = ((newCoords[0] + 1, newCoords[1]), self.reward)
            backTile = ((newCoords[0], newCoords[1] - 1), self.reward)
        elif move == 'L':
            straightTile = ((newCoords[0] - 1, newCoords[1]), self.reward)
            leftTile = ((newCoords[0], newCoords[1] - 1), self.reward)
            rightTile = ((newCoords[0], newCoords[1] + 1), self.reward)
            backTile = ((newCoords[0] + 1, newCoords[1]), self.reward)
        elif move == 'R':
            straightTile = ((newCoords[0] + 1, newCoords[1]), self.reward)
            leftTile = ((newCoords[0], newCoords[1] + 1), self.reward)
            rightTile = ((newCoords[0], newCoords[1] - 1), self.reward)
            backTile = ((newCoords[0] - 1, newCoords[1]), self.reward)
        elif move == 'D':
            straightTile = ((newCoords[0], newCoords[1] - 1), self.reward)
            leftTile = ((newCoords[0] + 1, newCoords[1]), self.reward)
            rightTile = ((newCoords[0] - 1, newCoords[1]), self.reward)
            backTile = ((newCoords[0], newCoords[1] + 1), self.reward)
        
        # append the new possible moves in [U, L, R, D] order
        newStates.append(straightTile)
        newStates.append(leftTile)
        newStates.append(rightTile)
        newStates.append(backTile)

        # if moving to a terminal state, adjust the value mapping
        for term_key in self.term_states:
            index = 0
            for state_pair in newStates:
                if term_key == state_pair[0]:
                    newStates[index] = (term_key, self.term_states[term_key])
                index += 1

        # checking if the new state hits any walls, if so, assign to original coordinates
        index = 0
        for state_pair in newStates:
            if state_pair[0][0] < 1 or state_pair[0][1] < 1 or state_pair[0][0] > self.columns or state_pair[0][1] > self.rows or state_pair[0] in self.walls:
                newStates[index] = (coords, self.reward)
            index += 1

        return newStates # list of the states we have a chance of ending up in
    
    # displays the current utility values after completed i iterations
    def displayValues(self, u_vals, i):
        if i != -1:
            print("iteration: ", i)

        i = 1
        for u_val in u_vals:
            if i % self.columns == 0:
                print(u_val)
                print()
            else:
                print(u_val, " ", end='')
            i += 1
        print()

    # calculates the converging values for the best move at a given square
    def valueIteration(self):
        # list which holds the current U values and will hold the final U values after convergence
        u_values = []
        for j in range(self.columns * self.rows):
            u_values.append(0)

        # dictionary that holds prev U values {(x, y): value, ..}
        prev_u_values = {}
        x = 1
        y = self.rows
        for i in range(self.columns * self.rows):
            if x is self.columns:
                prev_u_values[(x,y)] = 0
                x = 1
                y -= 1
            else:
                prev_u_values[(x,y)] = 0
                x += 1
        
        # assign the walls with dashes
        for wall in self.walls:
            index = 0
            for square in self.states:
                if wall == square:
                    u_values[index] = '--------------'
                index += 1
        
        print("################ VALUE ITERATION ###########################")
        print()
        self.displayValues(u_values, 0)

        iter = 1
        notConverged = True
        while(True):
            # reset max change to 0
            max_change = 0

            # update previous util values with current util values 
            x = 1
            y = self.rows
            for cur_value in u_values:
                if x is self.columns:
                    prev_u_values[(x,y)] = cur_value
                    x = 1
                    y -= 1
                else:
                    prev_u_values[(x,y)] = cur_value
                    x += 1

            # "base case" and breaks out of the loop
            if notConverged is False:
                print('Final Value After Convergence')
                self.displayValues(u_values, -1)
                return prev_u_values # return dict of converged values

            # update each states util value
            state_index = 0
            for state in self.states:
                # do not caluclate walls or terminal states
                if state not in self.walls and state not in self.term_states:
                    # each state has an option to move 4 different directions
                    possible_util = []
                    for move in self.moves: # for each direction
                        uStates = self.move_calculator(state, move) # retrieve the states they can end up in for each direction
                        # sum the values of each transition to each state using bellman equation
                        moveValue = 0 
                        i = 0
                        for space_pairs in uStates:
                            moveValue += self.T[i] * (space_pairs[1] + (self.gamma*prev_u_values[space_pairs[0]])) # bellman equation using the previous iterations util values
                            i += 1
                        
                        # add to list to find the max
                        possible_util.append(moveValue)

                    # get the best value out of the possible moves and assign to u values
                    best_util_value = max(possible_util)
                    u_values[state_index] = round(best_util_value, 12)

                    # assigning the max_change for convergence
                    if abs(best_util_value - prev_u_values[state]) > max_change:
                        max_change = abs(best_util_value - prev_u_values[state])

                state_index += 1
            
            # check to see if the values have converged yet
            change = (self.epsilon * ((1-self.gamma) / self.gamma))

            # rounded to 12 places to reach convergence criteria faster
            if round(max_change, 12) <= round(change, 12): 
                notConverged = False

            self.displayValues(u_values, iter)
            iter += 1
    
    # uses the converged values from value iteration to decide the best move at each square
    def finalPolicy(self, utitityFunction):
        # add terminal state transition values
        x = 1
        y = self.rows
        for i in range(self.rows*self.columns):
            if (x, y) in self.term_states:
                utitityFunction[i] = self.term_states[(x,y)]

            if x == self.columns:
                x = 1
                y -= 1
            else:
                x += 1    
    
        directions = ['N', 'S', 'W', 'E'] # to match the output
        optimalMoves = []

        for state in self.states:
            # do not caluclate walls or terminal states
            if state not in self.walls and state not in self.term_states:

                # each state has an option to move 4 different directions
                possible_util = []
                for move in self.moves: # for each direction
                    uStates = self.move_calculator(state, move) # retrieve the states they can end up in for each direction
                    # sum the values of each transition to each state using bellman equation
                    moveValue = 0 
                    i = 0
                    for space_pairs in uStates:
                        moveValue += self.T[i] * (space_pairs[1] + (self.gamma*utilityFunction[space_pairs[0]])) # bellman equation using the converged values
                        i += 1    

                    # add to list to find the max
                    possible_util.append(moveValue)

                # get the best value out of the possible moves and assign to corresponding direction
                maxVal = 0
                maxIndex = 0
                for i in range(4):
                    if possible_util[i] > maxVal:
                        maxVal = possible_util[i]
                        maxIndex = i
                optimalMoves.append(directions[maxIndex])
            elif state in self.walls:
                optimalMoves.append('-') # for walls we have -
            elif state in self.term_states:
                optimalMoves.append('T') # for terminal states we have T

        self.final_policy = optimalMoves # assign to mdp object    
        print("Final Policy")
        self.displayValues(optimalMoves, -1)
             
if __name__ == '__main__':
    print("Please enter the name of the input file (must be in the form of the provided test file)")
    print("Ex: 'mdp_input_book.txt'")
    input = input()
    print()
    myMDP = MDP() # create mdp object
    myMDP.readInput() # read in the input from the file to populate mdp details/params
    myMDP.print() # print the description of the mdp
    utilityFunction = myMDP.valueIteration() # obtain the final converged values of each state from valueIteraton
    myMDP.finalPolicy(utilityFunction) # run the "game" using the final converged values and display the condition/action rules in each state


