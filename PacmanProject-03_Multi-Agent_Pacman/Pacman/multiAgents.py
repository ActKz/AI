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

from game import Agent

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
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "[Project 3] YOUR CODE HERE"
        newGhostPos = successorGameState.getGhostPositions()
        foodList = newFood.asList()
        # distance with pacman
        foodDis = [manhattanDistance(food, newPos) for food in foodList]        
        ghostDis = [manhattanDistance(newPos, ghost) for ghost in newGhostPos]
        # food number
        curNum = currentGameState.getNumFood()
        sucNum = successorGameState.getNumFood()        
        # initial
        score = successorGameState.getScore()
        closest = 10000
        
        #print "FK"#, newPos, newFood, foodList
        #print foodDis
        ######################
        # Win
        if successorGameState.isWin():
            score += 100000000
        # dodge ghost
        for gD in ghostDis:
            if gD < 2:
                score -= 1000000
        # search the closest food
        for dis in foodDis:
            if dis < closest:
                closest = dis
        score -= closest*10
        # To avoid all scores are the same. Need to plus much, or pacman will stay in a small place
        if curNum > sucNum:
            score += 10000
        # successorGameState include currentPosistion. But we want to keep going
        if currentGameState.getPacmanPosition() == newPos:
            score -= 1000
        #print score, closest
        return score

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
        
        "[Project 3] YOUR CODE HERE"
        #print self.depth, self.evaluationFunction(), gameState.getLegalActions()
        # Pacman is 0 Ghost > 0     one depth include 1 pacman & n ghost
        def MiniMax(gameState, depth, agentIndex, ghostNum):
            if depth == self.depth or gameState.isWin() or gameState.isLose():
                return (self.evaluationFunction(gameState), None)
            bestScore = -(float("inf")) if agentIndex == 0 else float("inf")
            bestAction = None
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                newScore = MiniMax(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, ghostNum)[0] if agentIndex != ghostNum\
                else MiniMax(gameState.generateSuccessor(agentIndex, action), depth + 1, 0, ghostNum)[0]
                if agentIndex == 0 and newScore > bestScore or agentIndex != 0 and newScore < bestScore:
                    bestScore, bestAction = newScore, action
                    
            return bestScore, bestAction

        ghostNum = gameState.getNumAgents() - 1        
        return MiniMax(gameState, 0, 0, ghostNum)[1]
        #util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        
        "[Project 3] YOUR CODE HERE"        
        # http://web.cs.ucla.edu/~rosen/161/notes/alphabeta.html
        # Pacman is 0 Ghost > 0     one depth include 1 pacman & n ghost    alpha for max(pacman)   beta for min(ghost)  for explored
        def MiniMax(gameState, depth, agentIndex, alpha, beta, ghostNum):
            if depth == self.depth or gameState.isWin() or gameState.isLose():
                return (self.evaluationFunction(gameState), None)
            bestScore = -(float("inf")) if agentIndex == 0 else float("inf")
            bestAction = None
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                if alpha > beta:
                    return bestScore, bestAction
                newScore = MiniMax(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta, ghostNum)[0] if agentIndex != ghostNum\
                else MiniMax(gameState.generateSuccessor(agentIndex, action), depth + 1, 0, alpha, beta, ghostNum)[0]
                if agentIndex == 0 and newScore > bestScore or agentIndex != 0 and newScore < bestScore:
                    bestScore, bestAction = newScore, action
                if agentIndex == 0 and newScore > alpha:
                    alpha = newScore
                if agentIndex != 0 and newScore < beta:
                    beta = newScore
            return bestScore, bestAction

        ghostNum = gameState.getNumAgents() - 1        
        
        return MiniMax(gameState, 0, 0, -(float("inf")), float("inf"), ghostNum)[1]
        
        #util.raiseNotDefined()

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
    
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

