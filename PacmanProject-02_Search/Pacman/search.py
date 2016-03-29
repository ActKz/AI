# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

# P2-1
def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """

    "[Project 2] YOUR CODE HERE"
    #print "Start:", problem.getStartState()
    #print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    if problem.isGoalState(problem.getStartState()):
        return []
    #print "Start's successors:", problem.getSuccessors(problem.getStartState())
    from game import Directions
    n = Directions.NORTH
    s = Directions.SOUTH
    w = Directions.WEST
    e = Directions.EAST
    
    
    from util import Stack
    visited = set(problem.getStartState())
    stack = Stack()
    path = []  
    stack.push((problem.getStartState(), []))
    #stack is tup  [0] is state [1] is path
    while not stack.isEmpty() :        
        cur = stack.pop()
        visited.add(cur[0])
        #print cur[0], cur[1]
        if problem.isGoalState(cur[0]):
            path = list(cur[1])
            break
        #To avoid expand error, push every node on branch onto stack once
        successors = problem.getSuccessors(cur[0])
        for succ in successors:            
            tmp = list(cur[1])
            
            if not succ[0] in visited:                                
                if succ[1] == 'North':
                    tmp.append(n)
                elif succ[1] == 'South':
                    tmp.append(s)
                elif succ[1] == 'East':
                    tmp.append(e)
                elif succ[1] == 'West':
                    tmp.append(w)
                else:
                    tmp.append(succ[1])
                stack.push((succ[0],tmp))
                #print tmp
        
    return path  
    util.raiseNotDefined()

# P2-2
def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""

    "[Project 2] YOUR CODE HERE"
    
    if problem.isGoalState(problem.getStartState()):
        return []
    #print "Start's successors:", problem.getSuccessors(problem.getStartState())
    from game import Directions
    n = Directions.NORTH
    s = Directions.SOUTH
    w = Directions.WEST
    e = Directions.EAST
    
    
    from util import Queue
    visited = set(problem.getStartState())
    queue = Queue()
    path = []
    queue.push((problem.getStartState(), []))
    #queue is tup  [0] is state [1] is path
    while not queue.isEmpty():
        cur = queue.pop()
        #visited.add(cur[0])
        #print cur[0], cur[1]
        if problem.isGoalState(cur[0]):            
            path = list(cur[1])
            break
        #To avoid expand too much . Change the position pushing the node onto visited
        successors = problem.getSuccessors(cur[0])        
        for succ in successors:            
            tmp = list(cur[1])
            if not succ[0] in visited:
                #### visited different with dfs
                visited.add(succ[0])
                if succ[1] == 'North':
                    tmp.append(n)
                elif succ[1] == 'South':
                    tmp.append(s)
                elif succ[1] == 'East':
                    tmp.append(e)
                elif succ[1] == 'West':
                    tmp.append(w)
                else:
                    tmp.append(succ[1])
                queue.push((succ[0],tmp))
                #print tmp
    
    return path  
    util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

# P2-3
def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "print heuristic(problem.getStartState(), problem)"
    
    "[Project 2] YOUR CODE HERE"
    
    if problem.isGoalState(problem.getStartState()):
        return []
    #print "Start's successors:", problem.getSuccessors(problem.getStartState())
    from game import Directions
    n = Directions.NORTH
    s = Directions.SOUTH
    w = Directions.WEST
    e = Directions.EAST
    
    
    from util import PriorityQueue
    visited = set(problem.getStartState())
    queue = PriorityQueue()
    path = []
    queue.push((problem.getStartState(), []), 0)
    #queue is tup  [0] is state [1] is path
    while not queue.isEmpty():
        cur = queue.pop()
        #visited.add(cur[0])
        #print cur[0], cur[1]
        if problem.isGoalState(cur[0]):            
            path = list(cur[1])
            break
        #To avoid expand too much . Change the position pushing the node onto visited
        successors = problem.getSuccessors(cur[0])        
        for succ in successors:            
            tmp = list(cur[1])
            hCost = heuristic(succ[0], problem)
            if not succ[0] in visited:
                #### visited different with dfs
                visited.add(succ[0])
                if succ[1] == 'North':
                    tmp.append(n)
                elif succ[1] == 'South':
                    tmp.append(s)
                elif succ[1] == 'East':
                    tmp.append(e)
                elif succ[1] == 'West':
                    tmp.append(w)
                else:
                    tmp.append(succ[1])
                cost = problem.getCostOfActions(tmp) + hCost
                queue.push((succ[0],tmp), cost)
                #print tmp
    
    return path  
    util.raiseNotDefined()


# Abbreviations
astar = aStarSearch
bfs = breadthFirstSearch
dfs = depthFirstSearch
ucs = uniformCostSearch
