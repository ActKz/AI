# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util
import math
from game import Agent
from operator import itemgetter

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        capPos = currentGameState.getCapsules()
        newPos = successorGameState.getPacmanPosition()
        newFood = currentGameState.getFood().asList()

        newGhostStates = successorGameState.getGhostStates()
        ghoPos = newGhostStates[0].getPosition()

        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        if len(capPos) > 0:
            nearestFood = [util.manhattanDistance(newPos,capsulePos) for capsulePos in capPos]
        else:
            nearestFood = [util.manhattanDistance(newPos,foodPos) for foodPos in newFood] + [util.manhattanDistance(newPos,capsulePos) for capsulePos in capPos]
        manDis = util.manhattanDistance(newPos,ghoPos)
        if len(capPos) == 0 and newScaredTimes[0] > 0:
            Score = -manDis
        else:
            Score = -min(nearestFood)
            if manDis<2:
                Score -=500000
        "[Project 3] YOUR CODE HERE"
        
        return Score

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        res = self.minimax(0, 0, gameState, self.evaluationFunction)
        if res:
            return res[1]
        return Directions.STOP


        util.raiseNotDefined()
    def minimax(self, agentIndex, depth, state, f):
        if depth == self.depth:
            return (f(state), None)
        fMAX_MAX = -9999999999
        fMIN_MIN = 9999999999
        tmp = None
        agentNum = state.getNumAgents()
        if agentIndex != agentNum-1:
            for act in state.getLegalActions(agentIndex % agentNum):
                succ = state.generateSuccessor(agentIndex % agentNum, act)
                val = self.minimax(agentIndex + 1, depth, succ, f)
                if agentIndex%agentNum == 0:
                    if val and val[0] > fMAX_MAX:
                        fMAX_MAX = val[0]
                        tmp = (val[0], act)
                else:
                    if val and val[0] < fMIN_MIN:
                        fMIN_MIN = val[0]
                        tmp = (val[0], act)
        else:
            for act in state.getLegalActions(agentIndex % agentNum):
                succ = state.generateSuccessor(agentIndex % agentNum, act)
                val = self.minimax(0, depth + 1, succ, f)
                if agentIndex%agentNum == 0:
                    if val and val[0] > fMAX_MAX:
                        fMAX_MAX = val[0]
                        tmp = (val[0], act)
                else:
                    if val and val[0] < fMIN_MIN:
                        fMIN_MIN = val[0]
                        tmp = (val[0], act)

        if tmp is None:
            return (f(state), None)
        return tmp
            

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        res = self.alphabeta(0, 0, gameState, self.evaluationFunction, -999999999,999999999)
        if res:
            return res[1]
        return Directions.STOP
        "[Project 3] YOUR CODE HERE"        
        
        util.raiseNotDefined()
    def alphabeta(self, agentIndex, depth, state, f, alpha, beta ):
        if depth == self.depth or state.isWin() or state.isLose():
            return (f(state), None)
        MAX = -999999999
        MIN = 999999999
        tmp = None
        agentNum = state.getNumAgents()
        if agentIndex != agentNum-1:
            for act in state.getLegalActions(agentIndex % agentNum):
                if alpha > beta:
                    return tmp
                succ = state.generateSuccessor(agentIndex % agentNum, act)
                val = self.alphabeta(agentIndex + 1, depth, succ, f, alpha, beta )
                if agentIndex%agentNum == 0:
                    if val and val[0] > MAX:
                        MAX = val[0]
                        tmp = (val[0], act)
                    if MAX > alpha:
                        alpha = MAX
                else:
                    if val and val[0] < MIN:
                        MIN = val[0]
                        tmp = (val[0], act)
                    if MIN < beta:
                        beta = MIN
        else:
            for act in state.getLegalActions(agentIndex % agentNum):
                if alpha > beta:
                    return tmp
                succ = state.generateSuccessor(agentIndex % agentNum, act)
                val = self.alphabeta(0, depth + 1, succ, f, alpha, beta)
                if agentIndex%agentNum == 0:
                    if val and val[0] > MAX:
                        MAX = val[0]
                        tmp = (val[0], act)
                    if MAX > alpha:
                        alpha = MAX
                else:
                    if val and val[0] < MIN:
                        MIN = val[0]
                        tmp = (val[0], act)
                    if MIN < beta:
                        beta = MIN


        return tmp

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    
    "[Project 3] YOUR CODE HERE"   
    food = currentGameState.getFood()
    foodList = currentGameState.getFood().asList()
    pacPos = currentGameState.getPacmanPosition()
    g1Pos = currentGameState.getGhostPosition(1)
    g2Pos = currentGameState.getGhostPosition(2)
    capPos = currentGameState.getCapsules()
    g1Dis = util.manhattanDistance(pacPos, g1Pos)
    g2Dis = util.manhattanDistance(pacPos, g2Pos)
    ghostState = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostState]

    if len(capPos) == 2:
        nFood = [util.manhattanDistance(pacPos, caPos) for caPos in capPos]
    elif len(capPos) == 1:
        nFood = [util.manhattanDistance(pacPos, foodPos) for foodPos in foodList] + [util.manhattanDistance(pacPos, caPos) for caPos in capPos]
    else:
        nFood = [util.manhattanDistance(pacPos, foodPos) for foodPos in foodList]
    nFood.sort()
    Score = 0
    Score += 1/nFood[0]*500
    if g1Dis < 3:
        Score -= 500000
    if g2Dis < 3:
        Score -= 500000
    Score += currentGameState.getScore()
    print Score
    return Score
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

