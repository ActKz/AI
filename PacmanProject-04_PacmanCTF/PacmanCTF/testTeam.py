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
               first = 'OffensivealphabetaAgent', second = 'DefensivealphabetaAgent',
               third = 'DefensivealphabetaAgent'):
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

class alphabetaCaptureAgent(CaptureAgent):
  """
  A base class for alphabeta agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    #print('mii')
    CaptureAgent.registerInitialState(self, gameState)

  def Max_Self(self,gameState,depth,alpha,beta):
      if depth == 0:
        return {"score":self.evaluationFunction(gameState),"action":"Self"}
      legalMoves = gameState.getLegalActions(self.index)
      if self.index ==0:
          print "legal moves ",legalMoves
      actions = [action for action in legalMoves if action != 'Stop' ]
      best={"action":Directions.STOP,"score":float('-inf')}
      for action in actions:
        if self.index ==0:
            print "index ",self.index,"looping...:",action
        node = self.Min_Enemy(gameState.generateSuccessor(self.index,action), depth-1, alpha, beta)
        if self.index ==0:
            print "index ",self.index,"looped...:",action,node,best
        #no enemy in sight
        if(node['score'] > best['score']):
          if self.index ==0:
            print "Comparing...current act",action," node ",node," best ",best
          best['score']=node['score']
          best['action']=action
        if best['score'] >= beta:
          return best
        alpha = max(alpha, best['score'])

      return best

  def Min_Enemy(self,gameState,depth,alpha,beta):
    enemies = self.getOpponents(gameState)
    enemies_inrange = [e for e in enemies if gameState.getAgentState(e).configuration != None ]
    if not enemies_inrange or depth==0:
      return {"score":self.evaluationFunction(gameState),"action":"Test"}
    best={"action":Directions.STOP,"score":float('inf')}
    for e in enemies_inrange:
      legalMoves = gameState.getLegalActions(e)
      actions = [action for action in legalMoves if action != 'Stop' ]
      for action in actions:
        node =  self.Max_Self(gameState.generateSuccessor(e,action), depth, alpha, beta)
        if(node['score'] < best['score']):
          best['score']=node['score']
          best['action']=action
        if best['score'] <= beta:
          return best
        beta = min (alpha, best['score'])

    return best


  def chooseAction(self, gameState):

    best=self.Max_Self(gameState,2,float("-inf"), float("inf"))
    if self.index ==0:
        print "returned action ", best
    return best['action']
    util.raiseNotDefined()

class OffensivealphabetaAgent(alphabetaCaptureAgent):
  """
  A alphabeta agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def evaluationFunction(self, gameState):
      enemies = self.getOpponents(gameState)
      enemies_inrange = [e for e in enemies if gameState.getAgentState(e).configuration != None ]
      pos = gameState.getAgentState(self.index).getPosition()
      foodmap = self.getFood(gameState)
      foodList = self.getFood(gameState).asList()
      #### scaredTimes : If pacman eat a capsule, then pacman can eat ghosts for a while. And scareTimes will start to count down to 0.
      ####               >0 : can eat ghost  ==0 : dodge the ghost
      #scaredTimes = [state.scaredTimer for state in ghostState]
      #### scaredState:  1 : eat  0 : dodge      sum > 3 : To avoid too close. Since after eating a ghost, it will reborn.
      #scaredState = 1 if sum(scaredTimes) > 2 else 0
      # distance with pacman, ghost
      foodDis = [manhattanDistance(food, pos) for food in foodList]
      #capDis = [manhattanDistance(pos, capsule) for capsule in currentGameState.getCapsules()]
      # initial of score
      score = gameState.getScore()
      ######################

      ## situationi : ghost
      #for e_dis in enemies_dist:
      #    fraction = -e
          # eat ghost
          #if scaredState == 1:
          #    score += fraction*8
          # dodge ghost
          #elif scaredState == 0:
      #    score -= fraction

      ### food distance
      if foodList:
          minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
          fraction=1.0/(minDistance+1)
          score+=fraction

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

      if self.index ==0:
          print "returned score ",score
      return score



class DefensivealphabetaAgent(alphabetaCaptureAgent):
  """
  A alphabeta agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def evaluationFunction(self, gameState):
      return 1

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
