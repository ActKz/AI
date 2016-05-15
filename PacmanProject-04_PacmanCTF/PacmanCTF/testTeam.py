# baselineTeam.py
# ---------------
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
from util import manhattanDistance

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, thirdIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent',
               third = 'DefensiveReflexAgent'):
  """
  This function should return a list of three agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex), eval(third)(thirdIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    #print('mii')
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):

    def minmax(gameState,mode,enemyId,depth,alpha,beta):
        enemies = self.getOpponents(gameState)

        while enemyId <2 and gameState.getAgentState(enemies[enemyId+1]).configuration == None:
            enemyId+=1

        if enemyId >2:
            mode ="team"

        if depth == 0:
            return {"score":self.evaluationFunction(gameState),"action":None}

        tmp_score= -float("inf") if mode == "team" else float("inf")
        best={"action":Directions.STOP,"score":tmp_score}

        if mode =="team":
            actions=gameState.getLegalActions(self.index)
        else:
            actions=gameState.getLegalActions(enemyId)

        for action in actions:
            if alpha > beta:
                return best
            if enemyId < 2:
                    node=minmax(gameState.generateSuccessor(enemies[enemyId], action), \
                            "enemy",enemies[enemyId+1],depth, alpha,beta)
            else:
                    node=minmax(gameState.generateSuccessor(self.index, action), \
                            "team",self.index, depth-1, alpha,beta)
            if mode == "team":
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


    bestAction=minmax(gameState,"team", 0, 2,-(float("inf")), float("inf"))['action']
    print bestAction
    return bestAction
    util.raiseNotDefined()

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def evaluationFunction(self, gameState):
    pos = gameState.getAgentState(self.index).getPosition()
    foodmap = self.getFood(gameState)
    foodList = self.getFood(gameState).asList()
    #ghostState = gameState.getGhostStates()
    #ghostPos = gameState.getGhostPositions()
    #### scaredTimes : If pacman eat a capsule, then pacman can eat ghosts for a while. And scareTimes will start to count down to 0.
    ####               >0 : can eat ghost  ==0 : dodge the ghost
    #scaredTimes = [state.scaredTimer for state in ghostState]
    #### scaredState:  1 : eat  0 : dodge      sum > 3 : To avoid too close. Since after eating a ghost, it will reborn.
    #scaredState = 1 if sum(scaredTimes) > 2 else 0
    # distance with pacman, ghost
    foodDis = [manhattanDistance(food, pos) for food in foodList]
    #ghostDis = [manhattanDistance(pos, ghost) for ghost in ghostPos]
    #capDis = [manhattanDistance(pos, capsule) for capsule in currentGameState.getCapsules()]
    # initial of score
    #score = gameState.getScore()
    score = 0

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

    ### situationi : ghost
    #for gD in ghostDis:
    #    fraction = 1.0/gD
    #    # eat ghost
    #    if scaredState == 1:
    #        score += fraction*8
    #    # dodge ghost
    #    elif scaredState == 0:
    #        score -= fraction

    ### food distance
    minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
    fraction=1.0 / minDistance
    score+=fraction*1000

    #### situation : food amount
    #for fD in foodDis:
    #    fraction = 1.0/fD
    #    if len(foodList)==1 and len(capDis)==2:
    #        score += fraction*0.1
    #    else:
    #        score += fraction*3

    #### situation : capsule   fraction*3 for avoiding to hesitate
    #for cD in capDis:
    #    fraction = 1.0/cD
    #    if len(foodList)<=1 and len(capDis)==2:
    #        score += fraction*5
    #    else:
    #        score += fraction*3

    return score



class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def evaluationFunction(self, gameState):
      return 1;

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 2
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
