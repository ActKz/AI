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
inEye  = [0,0,0,0,0,0]
class mode:
    defend = 1
    attack = 2
    ownFlag = 3
    aggressive = 4
agentMode = [mode.attack,mode.defend,mode.defend,mode.defend,mode.defend,mode.attack]
#agentMode = [mode.attack,mode.attack,mode.attack,mode.attack,mode.attack,mode.attack]

def createTeam(firstIndex, secondIndex, thirdIndex, isRed,
                 first = 'HybridAgent1', second = 'HybridAgent1',
                 third = 'HybridAgent1'):
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

class AlphaBetaCaptureAgent(CaptureAgent):
    """
    A base class for AlphaBeta agents that chooses score-maximizing actions
    """
 
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        #print('mii')
        CaptureAgent.registerInitialState(self, gameState)
        self.defense_pos=[(12,13),(20,12),(14,7),(17,8),(11,3),(19,2)]
        #self.defense_pos=[(28,10),(21,12),(15,7),(16,8),(10,3),(19,3)]
        self.death=[0,0,0,0,0,0]
        self.dead_road=[(28,10),(24,6)]
        self.must_eat = [(18,14),(),(),(),(),(13,1)]
        self.try_attack = [False,False,False,False,False,False]
    def Max_Self(self,gameState,depth,alpha,beta):
        if depth == 0:
          return {"score":self.evaluationFunction(gameState),"action":"Self"}
        legalMoves = gameState.getLegalActions(self.index)
        #actions = [action for action in legalMoves if action != 'Stop' ]
        actions = legalMoves
        best={"action":Directions.STOP,"score":float('-inf')}
        for action in actions:
            node = self.Min_Enemy(gameState.generateSuccessor(self.index,action), depth-1, alpha, beta)
            #no enemy in sight
            if(node['score'] > best['score']):
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
            return {"score":self.evaluationFunction(gameState),"action":None}
        best={"action":Directions.STOP,"score":float('inf')}
        for e in enemies_inrange:
            legalMoves = gameState.getLegalActions(e)
            #actions = [action for action in legalMoves if action != 'Stop' ]
            actions = legalMoves
            for action in actions:
                node =  self.Max_Self(gameState.generateSuccessor(e,action), depth, alpha, beta)
                if(node['score'] < best['score']):
                    best['score']=node['score']
                    best['action']=action
                if best['score'] <= alpha:
                    return best
                beta = min (beta, best['score'])
       
        return best
 
 
    def chooseAction(self, gameState):
 
      best=self.Max_Self(gameState,2,float("-inf"), float("inf"))
      selfState = gameState.getAgentState(self.index).getPosition()
      return best['action']
      util.raiseNotDefined()

class OffensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
  """
  A AlphaBeta agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def evaluationFunction(self, gameState):
      selfState = gameState.getAgentState(self.index)
      pos = selfState.getPosition()
      isPacman = selfState.isPacman
      enemies = self.getOpponents(gameState)
      #in range I can see
      enemies_inrange = [e for e in enemies if gameState.getAgentState(e).configuration != None ]
      #position
      enemies_pos = [gameState.getAgentState(e).getPosition() for e in enemies_inrange]
      #in range enemies distance
      enemies_dist = [self.getMazeDistance(pos,ePos) for ePos in enemies_pos]
      #enemies who can see me
      enemies_nearby = [dis for dis in enemies_dist if dis < 5]
      foodmap = self.getFood(gameState)
      foodList = self.getFood(gameState).asList()
      foodDis = [manhattanDistance(food, pos) for food in foodList]
      flagMap = self.getFlags(gameState)
      flagList = flagMap
      #### scaredTimes : If pacman eat a capsule, then pacman can eat ghosts for a while. And scareTimes will start to count down to 0.
      ####               >0 : can eat ghost  ==0 : dodge the ghost
      #scaredTimes = [state.scaredTimer for state in ghostState]
      #### scaredState:  1 : eat  0 : dodge      sum > 3 : To avoid too close. Since after eating a ghost, it will reborn.
      #scaredState = 1 if sum(scaredTimes) > 2 else 0
      # distance with pacman, ghost
      capDis = [self.getMazeDistance(pos, capsule) for capsule in self.getCapsules(gameState)]
      # initial of score
      score = self.getScore(gameState)
      ######################

      ## situationi : ghost
      if enemies_dist:
          for e_dis in enemies_dist:
              fraction = 1.0/e_dis
              if isPacman:
                  score -= fraction * 100
              else:
                  score += fraction * 2.0

      ### try to get flag
      if flagList:
          distance = self.getMazeDistance(pos, flagList[0])
          fraction=1.0/(distance+1)
          score+=fraction * 4

      #has flag!! return!!
      if selfState.ownFlag:
          feature= 1.0/(self.getMazeDistance(pos,(1,1))+1)
          score+= feature * 100
      else:
          if foodList and not enemies_dist:
              minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
              fraction=1.0/(minDistance+1)
              score+=fraction
          else:
              feature= 1.0/(self.getMazeDistance(pos,self.defense_pos[self.index])+1)
              score+= feature * 3



      #### situation : food amount
      #for fD in foodDis:
      #    fraction = 1.0/fD
      #    if len(foodList)==1 and len(capDis)==2:
      #        score += fraction*0.1
      #    else:
      #        score += fraction*3

      ### situation : capsule   fraction*3 for avoiding to hesitate

      return score



class DefensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
    """
    A AlphaBeta agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """
    def evaluationFunction(self, gameState):
        score = self.getScore(gameState)
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = self.getOpponents(gameState)
        enemy_snoar = [gameState.getAgentDistances()[e] for e in enemies]
        ourfoodmap = self.getFoodYouAreDefending(gameState)
        ourfoodList = ourfoodmap.asList()
 
        # Computes whether we're on defense (1) or offense (0)
        # Computes distance to invaders we can see
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            score +=1.0 / min(dists)
        else:
            score += 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)
 
        return score

class HybridAgent(AlphaBetaCaptureAgent):
  """
  A AlphaBeta agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def evaluationFunction(self, gameState):
      score = self.getScore(gameState)
      myState = gameState.getAgentState(self.index)
      myPos = myState.getPosition()
      enemies = self.getOpponents(gameState)
      enemy_snoar = [gameState.getAgentDistances()[e] for e in enemies]

      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      if len(invaders) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          score +=1.0 / min(dists)
      elif myPos != self.defense_pos[self.index]: # get to defense point
          score += 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)

      return score

class HybridAgent1(AlphaBetaCaptureAgent):
    """
    A AlphaBeta agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """
    def evaluationFunction(self, gameState):
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = self.getOpponents(gameState) #all enemies
        #in range I can see
        enemies_inrange = [e for e in enemies if gameState.getAgentState(e).configuration != None ]
        #position
        enemies_pos = [gameState.getAgentState(e).getPosition() for e in enemies_inrange]
 
        check_ineye = [manhattanDistance(myPos,ePos) for ePos in enemies_pos if manhattanDistance(myPos,ePos)<=3 ]
        #update share information
        inEye[self.index] = len(check_ineye)
        #in range enemies distance
        enemies_dist = [self.getMazeDistance(myPos,ePos) for ePos in enemies_pos]
        score = float(self.getScore(gameState))
        ourfoodmap = self.getFoodYouAreDefending(gameState)
        ourfoodList = ourfoodmap.asList()
        foodmap = self.getFood(gameState)
        foodList = self.getFood(gameState).asList()
        foodDis = [manhattanDistance(food, myPos) for food in foodList]
        foodMazeDis = [self.getMazeDistance(myPos,food) for food in foodList]
        capsulesList = [self.getMazeDistance(myPos, capsule) for capsule in self.getCapsules(gameState)]
 
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        defendingFlag = self.getFlagsYouAreDefending(gameState)

        #agentMode define in the beginning
        if myState.ownFlag:
            agentMode[self.index] = mode.ownFlag

        if agentMode[self.index] == mode.ownFlag:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
            if dists:
                feature = min(dists)
                score += feature * 5
            if foodMazeDis:
                feature = 1.0/min(foodMazeDis)
                score+=feature

        elif agentMode[self.index] == mode.defend:
            #changing to attack mode if our two ghost are defending three pacman
            if sum(inEye) == 3 and inEye[self.index] == 0:
                if self.getFlags(gameState):
                    feature = 1.0/self.getMazeDistance(myPos, self.getFlags(gameState)[0])
                    score+=feature*2
                feature = 1.0/min(foodMazeDis)
                score+=feature
                agentMode[self.index] == mode.attack
                #check whether the flag is eaten
                #our flag is eaten, chase the opponent who own the flag
            elif self.getOwnFlagOpponent(gameState) != None:
                feature = 1.0/self.getMazeDistance(myPos, self.getOwnFlagOpponent(gameState))
                score+=feature*10
            elif len(invaders) > 0 and inEye[self.index] > 0:
                #if i see one, chase
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                feature = 1.0/(min(dists)+1)
                score +=feature*5
            elif myPos != self.defense_pos[self.index]: # get to defense point
                feature = 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)
                score+=feature * 2
            elif myPos == self.defense_pos[self.index]: # stay
                feature = 1
                score+=feature * 2
            #if score is Lose, changing to attack mode(? together and attack specific entry
            #else:
#           print self.index,inEye[self.index]
            if len(invaders) == sum(inEye) and inEye[self.index] == 0:
                agentMode[self.index] = mode.attack
                self.try_attack[self.index] = True
                

        elif agentMode[self.index] == mode.attack:
            if self.index == 0:
                print agentMode[self.index]
            if self.must_eat[self.index] in foodList:
                feature = 1.0/self.getMazeDistance(myPos,self.must_eat[self.index])
                score+=feature * 5
            #draw or win(positive score and isRed OR negative score and isBlue)
#           elif not self.try_attack[self.index] and (gameState.getScore() == 0 or (gameState.getScore()>0 and self.getTeam(gameState)[0]==0) or (gameState.getScore()<0 and self.getTeam(gameState)[0]==1)):
            elif (gameState.getScore() == 0 or (gameState.getScore()>0 and self.getTeam(gameState)[0]==0) or (gameState.getScore()<0 and self.getTeam(gameState)[0]==1)):

                feature = 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)
                score+=feature * 2
                agentMode[self.index] = mode.defend
            #lose state
            else:

                #no one chasing
                if len(ghosts) == 0:
                    if self.getFlags(gameState):
                        feature = 1.0/self.getMazeDistance(myPos, self.getFlags(gameState)[0])
                        score+=feature*2
                    if foodMazeDis:
                        feature = 1.0/min(foodMazeDis)
                        score+=feature
                #you are ghost and someone is chasing you, runaway or eat capsules
                elif myState.isPacman == False:
                    dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
                    if dists:
                        feature = min(dists)
                        score += feature * 5
                    feature = 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)
                    score+=feature * 4
                    if capsulesList:
                        feature = 1.0/min(capsulesList)
                        score += feature * 3
                    if foodMazeDis:
                        feature = 1.0/min(foodMazeDis)
                        score += feature
                else:
                    feature = 1.0/(self.getMazeDistance(myPos,self.defense_pos[self.index])+1)
                    score+=feature * 2
                    agentMode[self.index] = mode.defend

        if enemies_dist:
            for e_dis in enemies_dist:
                fraction = 1.0/(e_dis+1)
                if myState.isPacman:
                    score -= fraction * 10
                else:
                    score += fraction * 2.0
 
        return score

