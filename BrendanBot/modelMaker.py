import ast
from probMaker import probArr

class Model:
    #stateToBtc should take state and discretizations as parameters and return the correspoinding bitcion state as a float
    #rewardFunc should take btcPrime,btcInit,action as input in that order and return a float
    #action is "buy","hold",or "sell"
    def __init__(self,prob,stateToReward,rewardFunc):
        self.prob = prob
        self.stateToReward = stateToReward
        self.rewardFunc = rewardFunc
        self.value = {}
        self.policy = {} 
        self.actions = [i/20 for i in range(-20,20)]
        # Assume the number of possible actions is less than 2
        assert(prob.actions < 2)
        if(prob.actions == 1):
            self.actions = prob.disc[-1]
        #self.actions = ["buy","hold","sell"]
        self.noAction = "NoDataToDetermineAction"
        self.discountFactor = 0.95
        #self.finishedDifference = 0.001
        self.finishedDifference = 0.001

        self.modelIterate()

    def sumStatePrimes(self,action,stateIndices,indices=[]):
        if(len(indices) == self.prob.states):
            nextState = repr(indices)
            indices += stateIndices

            probPointer = self.prob.probMatr
            for i in range(len(indices)):
                if(len(probPointer)):
                    probPointer = probPointer[indices[i]]

            if(len(probPointer)):
                btcFinal = self.stateToReward(indices[:self.prob.states],self.prob.disc)
                btcInit = self.stateToReward(indices[self.prob.states:2*self.prob.states],self.prob.disc)
                reward = self.rewardFunc(btcFinal,btcInit,action)
                #print("NextState: " + str(self.value.get(nextState,0)))
                # TODO change below for a multi dimensional action
                index = self.prob.getIndex(action,self.prob.disc[-1])
                probPointer = probPointer[index]
                if(len(probPointer)):
                    return probPointer[0]*(reward+(self.discountFactor*self.value.get(nextState,0)))
                else:
                    return 0
            else:
                return 0
        else:
            probPointer = self.prob.probMatr
            for i in range(len(indices)):
                if(len(probPointer)):
                    probPointer = probPointer[indices[i]]

            sumVal = 0
            for i in range(len(probPointer)):
                sumVal += self.sumStatePrimes(action,stateIndices,indices + [i])

            return sumVal

    def modelIteration(self,indices=[]):
        if(len(indices) == self.prob.states):
            thisState = repr(indices)
            if(self.policy.get(thisState,"") == self.noAction):
                return 0

            bestActionVal = -10000000
            bestAction = ""
            equalCount = 0
            for i in range(len(self.actions)):
                actionVal = self.sumStatePrimes(self.actions[i],indices)
                #print(self.actions[i] + ": " + str(actionVal))
                equalCount += bestActionVal == actionVal == 0
                if(bestActionVal < actionVal):
                    bestActionVal = actionVal
                    bestAction = self.actions[i]
            #print(bestActionVal)
            #print(bestAction)

            diff = abs(bestActionVal - self.value.get(thisState,0))
            self.value[thisState] = bestActionVal
            self.policy[thisState] = bestAction
            if(equalCount == len(self.actions)-1):
                self.policy[thisState] = self.noAction

            return diff
        else:
            worstDiff = 0
            for i in range(len(self.prob.disc[len(indices)])):
                worstDiff = max(worstDiff,self.modelIteration(indices + [i]))
            return worstDiff

    def modelIterate(self):
        diff = self.finishedDifference*42
        while diff > self.finishedDifference:
            diff = self.modelIteration()
            print("Evaluating - diff is " + str(diff))

    def printPolicy(self):
        for key in self.policy:
            state = ast.literal_eval(key)
            action = self.policy[key]

            for i in range(len(state)):
                print(self.prob.disc[i][state[i]], end=' ')
            print("- " + action,end='')
            print(": " + str(self.value[key]))
