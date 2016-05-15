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

    def __init__(self):

        self.target=None


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
        currPos=currentGameState.getPacmanPosition()
        currFood = currentGameState.getFood()
        ghostPos=newGhostStates[0].getPosition()
        ghostDir=newGhostStates[0].getDirection()


        "[Project 3] YOUR CODE HERE"
        def findFood(currFood,currPos):
            nearest=10000
            target_food=None
            foodmap=currFood.asList()
            for f in foodmap:
                distance=util.manhattanDistance(f,currPos)
                if distance < nearest:
                    nearest=distance
                    target_food=f

            return target_food

        if self.target==None:
            self.target=findFood(currFood,currPos)
        elif currFood[self.target[0]][self.target[1]]:
            pass
        else:
            self.target=findFood(currFood,currPos)


        if util.manhattanDistance(newPos,ghostPos)<=1:
            return -100
        return 100-util.manhattanDistance(self.target,newPos)


        #return successorGameState.getScore()

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
        def update(node,best,agentIndex,action):
            if agentIndex==0:
                if node['score'] > best['score']:
                    best['score']=node['score']
                    best['action']=action
            else:
                if node['score'] < best['score']:
                    best['score']=node['score']
                    best['action']=action


        def minmax(gameState,agentIndex,depth,ghost_n):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return {"score":self.evaluationFunction(gameState),"action":None}

            tmp_score= float("inf") if agentIndex else -float("inf")
            best={"action":Directions.STOP,"score":tmp_score}
            actions=gameState.getLegalActions(agentIndex)
            # not pacman
            if agentIndex != ghost_n:
                for action in actions:
                    node=minmax(gameState.generateSuccessor(agentIndex, action), \
                            agentIndex + 1,depth, ghost_n)
                    update(node,best,agentIndex,action)

            else:
                for action in actions:
                    node=minmax(gameState.generateSuccessor(agentIndex, action), \
                            0, depth-1, ghost_n)
                    update(node,best,agentIndex,action)

            return best


        ghost_n= gameState.getNumAgents() - 1
        bestAction=minmax(gameState, 0, self.depth, ghost_n)['action']
        return bestAction


        util.raiseNotDefined()


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """

        "[Project 3] YOUR CODE HERE"
        def minmax(gameState,agentIndex,depth,ghost_n,alpha,beta):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return {"score":self.evaluationFunction(gameState),"action":None}

            tmp_score= float("inf") if agentIndex else -float("inf")
            best={"action":Directions.STOP,"score":tmp_score}
            actions=gameState.getLegalActions(agentIndex)

            for action in actions:
                if alpha > beta:
                    return best
                if agentIndex != ghost_n:
                        node=minmax(gameState.generateSuccessor(agentIndex, action), \
                                agentIndex + 1,depth, ghost_n,alpha,beta)
                else:
                        node=minmax(gameState.generateSuccessor(agentIndex, action), \
                                0, depth-1, ghost_n,alpha,beta)
                if agentIndex==0:
                    if node['score'] > best['score']:
                        best['score']=node['score']
                        best['action']=action
                    if node['score']> alpha:
                        alpha=node['score']
                else:
                    if node['score'] < best['score']:
                        best['score']=node['score']
                        best['action']=action
                    if node['score'] < beta:
                        beta=node['score']

            return best


        ghost_n= gameState.getNumAgents() - 1
        bestAction=minmax(gameState, 0, self.depth, ghost_n,-(float("inf")), float("inf"))['action']
        return bestAction
        util.raiseNotDefined()

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
    # initial of pacman position, ghost state & position, food
    pos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    foodList = newFood.asList()
    ghostState = currentGameState.getGhostStates()
    ghostPos = currentGameState.getGhostPositions()
    #### scaredTimes : If pacman eat a capsule, then pacman can eat ghosts for a while. And scareTimes will start to count down to 0.
    ####               >0 : can eat ghost  ==0 : dodge the ghost
    scaredTimes = [state.scaredTimer for state in ghostState]
    #### scaredState:  1 : eat  0 : dodge      sum > 3 : To avoid too close. Since after eating a ghost, it will reborn.
    scaredState = 1 if sum(scaredTimes) > 2 else 0
    # distance with pacman, ghost
    foodDis = [manhattanDistance(food, pos) for food in foodList]
    ghostDis = [manhattanDistance(pos, ghost) for ghost in ghostPos]
    capDis = [manhattanDistance(pos, capsule) for capsule in currentGameState.getCapsules()]
    # initial of score
    score = currentGameState.getScore()

    def findFood(currFood,currPos):
        nearest=10000
        target_food=None
        foodmap=currFood.asList()
        for f in foodmap:
            distance=util.manhattanDistance(f,currPos)
            if distance < nearest:
                nearest=distance
                target_food=f

        return distance
    ######################
    # Win
    if currentGameState.isWin():
        return float("inf")
    # Lose
    elif currentGameState.isLose():
        return -(float("inf"))

    ### situationi : ghost
    for gD in ghostDis:
        fraction = 1.0/gD
        # eat ghost
        if scaredState == 1:
            score += fraction*8
        # dodge ghost
        elif scaredState == 0:
            score -= fraction

    ### food distance
    near=findFood(newFood,pos)
    fracton=1.0/near
    if len(foodList)==1:
        score+=fracton*10

    ### situation : food amount
    for fD in foodDis:
        fraction = 1.0/fD
        if len(foodList)==1 and len(capDis)==2:
            score += fraction*0.1
        else:
            score += fraction*3

    ### situation : capsule   fraction*3 for avoiding to hesitate
    for cD in capDis:
        fraction = 1.0/cD
        if len(foodList)<=1 and len(capDis)==2:
            score += fraction*5
        else:
            score += fraction*3

    return score

    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction

