# myTeam.py
# ---------
# Licensing Information: You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# python capture.py -r 00_myTeam -b stopTeam

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def manhattanDistance(x, y ):
  return abs( x[0] - y[0] ) + abs( x[1] - y[1] )

def createTeam(firstIndex, secondIndex, thirdIndex, isRed,
                         first = 'ABAgent', second = 'ABAgent', third = 'ABAgent'):
    """
    This function should return a list of three agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex), eval(third)(thirdIndex)]

##########
# Agents #
##########
class ABAgent(CaptureAgent):
    def transIndex(self, pos):
        return int(pos[1]*self.width+pos[0])

    def transXY(self, index):
        return index%self.width, index//self.width

    # Translate red (x,y) to blue (x,y)
    def transMapCoord(self, pos):
        if not self.red:
            return (self.width//2+self.height-1-pos[0],self.height-1-pos[1])
        return pos

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

        self.width = gameState.data.layout.width
        self.height = gameState.data.layout.height
        pointsNum = self.width*self.height
        
        try:
          distanceMap
        except:
            globals()['distanceMap'] = [ [float("inf") for x in xrange(pointsNum)] for x in xrange(pointsNum) ]
            globals()['questMap'] = [ 2, 1, 2 ] # := [ Defence, Flag, Capsule ]
            globals()['targetState'] = [(13, 12), (7, 5), (6, 10), (13, 7)]

            for i in xrange(pointsNum):
                x, y = self.transXY(i)
                if gameState.hasWall(x, y):
                    continue
                distanceMap[i][i] = 0
                que = list([(x, y)])
                while len(que)>0:
                    x, y = que[0]
                    que.pop(0)
                    if not gameState.hasWall(x+1, y) and distanceMap[i][self.transIndex((x+1, y))]==float("inf"):
                        distanceMap[i][self.transIndex((x+1, y))] = distanceMap[i][self.transIndex((x, y))] + 1
                        que.append((x+1, y))
                    if not gameState.hasWall(x-1, y) and distanceMap[i][self.transIndex((x-1, y))]==float("inf"):
                        distanceMap[i][self.transIndex((x-1, y))] = distanceMap[i][self.transIndex((x, y))] + 1
                        que.append((x-1, y))
                    if not gameState.hasWall(x, y+1) and distanceMap[i][self.transIndex((x, y+1))]==float("inf"):
                        distanceMap[i][self.transIndex((x, y+1))] = distanceMap[i][self.transIndex((x, y))] + 1
                        que.append((x, y+1))
                    if not gameState.hasWall(x, y-1) and distanceMap[i][self.transIndex((x, y-1))]==float("inf"):
                        distanceMap[i][self.transIndex((x, y-1))] = distanceMap[i][self.transIndex((x, y))] + 1
                        que.append((x, y-1))

    def chooseAction(self, gameState):
        
        if True: #gameState.getAgentPosition(self.index) == self.transMapCoord((1,3)):
            
            assignment = []
            
            for agent in self.getTeam(gameState):
                flagScore = float('inf')
                capsuleScore = float('inf')
                if len(self.getFlags(gameState)) > 0:
                    flagScore = distanceMap[self.transIndex(self.getFlags(gameState)[0])][self.transIndex(gameState.getAgentPosition(agent))]
                if gameState.getAgentState(agent).ownFlag:
                    flagScore = float('-inf')
                if True in [True in row for row in self.getFood(gameState)]:
                    capsuleScore = distanceMap[self.transIndex((24,7))][self.transIndex(gameState.getAgentPosition(agent))]

                #print agent, flagScore, capsuleScore
                assignment.append( (agent, flagScore, capsuleScore) )
            
            bestFlagCatcher = min( assignment, key=lambda t: t[1] )
            hasFlagCatcher = False
            if bestFlagCatcher[1] != float('inf'):
                questMap[ bestFlagCatcher[0]//2 ] = (1, targetState[3]) # [defence, flag, capsule]
                if bestFlagCatcher[1] != float('-inf'):
                    hasFlagCatcher = True
                assignment.remove( bestFlagCatcher )
            
            hasDefender = 0
            for agent in assignment[:]:
                if hasDefender == 0:
                    questMap[ agent[0]//2 ] = (0, targetState[1]) # [defence, flag, capsule]
                    hasDefender = 1
                elif hasFlagCatcher:
                    questMap[ agent[0]//2 ] = (2, targetState[2]) # [defence, flag, capsule]
                    hasFlagCatcher = False
                elif hasDefender == 1:
                    questMap[ agent[0]//2 ] = (0, targetState[0]) # [defence, flag, capsule]
                    hasDefender = 2
                else:
                    questMap[ agent[0]//2 ] = (2, targetState[2])

                assignment.remove( agent )
            #print 'reassignment', questMap
        
        actions = gameState.getLegalActions(self.index)
        score, action = self.alphaBetaSearch(gameState, 1, self.index, self.index, float("-inf"), float("inf"))
        return action

    def alphaBetaSearch(self, gameState, depth, agentIndex, originIndex, alpha, beta):
        if depth > 6:
            return self.evaluationFunction(gameState, agentIndex), Directions.STOP

        myAction = Directions.STOP
        if agentIndex in self.getTeam(gameState):
            if agentIndex != originIndex:
                return self.alphaBetaSearch(gameState, depth+1, (agentIndex+1)%6, originIndex, alpha, beta)
                
            value = float("-inf")
            actions = gameState.getLegalActions(agentIndex)
            random.shuffle(actions)
            for action in actions:
                newScore, newAction = self.alphaBetaSearch(gameState.generateSuccessor(agentIndex, action), depth+1, (agentIndex+1)%6, originIndex, alpha, beta)
                if newScore > value:
                    myAction = action
                    value = newScore
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value, myAction
        else:
            value = float("inf")
            if gameState.getAgentPosition(agentIndex) == None:
                return self.alphaBetaSearch(gameState, depth+1, (agentIndex+1)%6, originIndex, alpha, beta)
            else:
                ghostPos = gameState.getAgentPosition(agentIndex)
                distGhost = distanceMap[originIndex][self.transIndex(ghostPos)]
                if distGhost > 1:
                    return self.alphaBetaSearch(gameState, depth+1, (agentIndex+1)%6, originIndex, alpha, beta)
                    
                for action in gameState.getLegalActions(agentIndex):
                    newScore, newAction = self.alphaBetaSearch(gameState.generateSuccessor(agentIndex, action), depth+1, (agentIndex+1)%6, originIndex, alpha, beta)
                    if newScore < value:
                        myAction = action
                        value = newScore
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            return value, myAction

    def evaluationFunction(self, gameState, agentIndex):
        myIndex = self.transIndex(gameState.getAgentPosition(agentIndex))

        def isPacman(pos):
            x, y = pos
            if self.red and x < 16:
                return True
            if not self.red and x >= 16:
                return True
            return False

        def danger(gameState, ownFlag=False):
            dangerVal = 0
            freedom = True
            myState = gameState.getAgentState(agentIndex)
            myPos = gameState.getAgentPosition(agentIndex)

            for ghostIndex in self.getOpponents(gameState):
                ghostState = gameState.getAgentState(ghostIndex)
                ghostPos = ghostState.getPosition()
                if ghostPos == None:
                    continue
                distGhost = distanceMap[myIndex][self.transIndex(ghostPos)]
                if (ghostState.isPacman and myState.scaredTimer != 0) \
                    or myState.ownFlag \
                    or ( (not ghostState.ownFlag) and myState.isPacman and ghostState.scaredTimer == 0):
                    if distGhost <= 5:
                        if distGhost <= 1:
                            dangerVal += 30
                        freedom = False
            if not freedom:
                actions = gameState.getLegalActions(self.index)
                dangerVal += (5-len(actions))*12.5

            if myPos[0] == 1:
                dangerVal += 500
            return dangerVal

        def happiness(gameState):
            happyVal = 0
            myState = gameState.getAgentState(agentIndex)
            myPos = gameState.getAgentPosition(agentIndex)

            for ghostIndex in self.getOpponents(gameState):
                ghostState = gameState.getAgentState(ghostIndex)
                ghostPos = ghostState.getPosition()
                if ghostPos == None:
                    continue
                distGhost = distanceMap[myIndex][self.transIndex(ghostPos)]
                if ghostState.isPacman and myState.scaredTimer == 0 and (not myState.ownFlag) and distGhost <= 3:
                    happyVal += (4-distGhost)*24/3.0
                elif myState.isPacman and ghostState.scaredTimer != 0 and (not myState.ownFlag) and distGhost <= 3:
                    happyVal += (4-distGhost)*49/3.0
                elif (not myState.ownFlag) and (ghostState.ownFlag) and distGhost <= 3:
                    happyVal += (4-distGhost)*24/3.0
                
            return happyVal
            
        def evalFuncOppo(gameState):
            return 1

        def evalFuncDef(gameState, goalState):
            myPos = gameState.getAgentPosition(agentIndex)
            if self.red:
                return gameState.getScore() + goToPos(gameState, goalState, False)
            else:
                return -gameState.getScore() + goToPos(gameState, goalState, False)
        
        def goToPos(gameState, pos, ownFlag=True):
            myPos = gameState.getAgentPosition(agentIndex)
            #totalCost = distanceMap[self.transIndex(myPos)][self.transIndex(pos)]
            totalCost = distanceMap[self.transIndex(myPos)][self.transIndex(self.transMapCoord(pos))]/50.0
            if ownFlag:
                totalCost = totalCost + danger(gameState, ownFlag) + happiness(gameState)
            else:
                totalCost = totalCost + danger(gameState, ownFlag) - happiness(gameState)

            return -totalCost

        def evalFuncFlag(gameState, goalState):
            flagPos = self.getFlags(gameState)
            if gameState.getAgentState(agentIndex).ownFlag:
                return goToPos(gameState, goalState) + 500
            elif len(flagPos)==0:
                return evalFuncCapsule(gameState, targetState[2])

            totalCost = distanceMap[self.transIndex((flagPos[0]))][myIndex] * 10
            totalCost += danger(gameState)
            if self.red:
                return gameState.getScore() - totalCost
            else:
                return -gameState.getScore() - totalCost

        def evalFuncCapsule(gameState, goalState):
            minCost = float("inf")
            foodMap = self.getFood(gameState)
            foodNum = 0
            for x in xrange(self.width):
                for y in xrange(self.height):
                    if foodMap[x][y]:
                        foodNum += 1
                        minCost = min(minCost, distanceMap[self.transIndex((x, y))][myIndex]/50.0)

            if foodNum == 0:
                return evalFuncDef(gameState, goalState) + 50
            else:
                minCost += danger(gameState) - happiness(gameState)

            if self.red:
                return gameState.getScore() - minCost
            else:
                return -gameState.getScore() - minCost
            
        role = [ evalFuncDef, evalFuncFlag, evalFuncCapsule ]
        
        if agentIndex % 2 != self.getTeam(gameState)[0]:
            return evalFuncOppo(gameState)
        
        return role[ questMap[ agentIndex//2 ][0] ](gameState, questMap[agentIndex//2][1])
        
#        if agentIndex // 2 == 0:
#            return evalFuncCapsule(gameState)
#            return evalFuncDef(gameState)
#        if agentIndex // 2 == 1:
#            return evalFuncFlag(gameState)
#        if agentIndex // 2 == 2:
#            return evalFuncCapsule(gameState)

