import ast
from queue import Queue
from probMaker import probArr
import multiprocessing
from multiprocessing.pool import Pool
from threading import Lock
from functools import partial
POOL_SIZE = 8
hack = True

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
        self.finishedDifference = 0.8

        self.pool = Pool(processes=POOL_SIZE)
        self.guard = Lock()
        self.outQ = Queue(maxsize=POOL_SIZE)
        self.results = [0 for i in range(POOL_SIZE)]

        self.modelIterate()

    def sumStatePrimes(self,action,stateIndices,indices=[]):
        probPointer = self.prob.probMatr
        for i in range(len(indices)):
            if(len(probPointer)):
                probPointer = probPointer[indices[i]]
            else:
                return 0
        if(len(probPointer) == 0):
            return 0
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
                if(type(action) != type([])):
                    action = [action]
                reward = self.rewardFunc(btcFinal,btcInit,action)
                for i in range(len(action)):
                    index = self.prob.getIndex(action[i],self.prob.disc[-1])
                    if(len(probPointer)):
                        probPointer = probPointer[index]

                if(len(probPointer)):
                    # Protect value from concurrency
                    self.guard.acquire()
                    toRet = probPointer[0]*(reward+(self.discountFactor*self.value.get(nextState,0)))
                    self.guard.release()
                    return toRet
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

    def worker(self,indices):
        val = self.modelIteration(indices)
        self.results[indices[0]%POOL_SIZE] = val

    def modelIteration(self,indices=[]):
        if(len(indices) == self.prob.states):
            thisState = repr(indices)
            if(self.policy.get(thisState,"") == self.noAction):
                return 0

            bestActionVal = -10000000
            bestAction = ""
            equalCount = 0
            for i in range(len(self.actions)):
                actionVal = 0
                if hack:
                    actionVal = self.sumStatePrimes(self.actions[i],list(indices),list(indices))
                else:
                    actionVal = self.sumStatePrimes(self.actions[i],indices)
                #print(self.actions[i] + ": " + str(actionVal))
                equalCount += bestActionVal == actionVal == 0
                if(bestActionVal < actionVal):
                    bestActionVal = actionVal
                    bestAction = self.actions[i]
            #print(bestActionVal)
            #print(bestAction)

            self.guard.acquire()
            diff = abs(bestActionVal - self.value.get(thisState,0))
            self.value[thisState] = bestActionVal
            self.policy[thisState] = bestAction
            if(equalCount == len(self.actions)-1):
                self.policy[thisState] = self.noAction
            self.guard.release()

            return diff
        else:
            worstDiff = 0

            # Start up some threads
            if(len(indices) == 0):
                domainSize = len(self.prob.disc[0])
                for i in range(0,domainSize,POOL_SIZE):
                    threads = []
                    for j in range(i,min(domainSize,i+POOL_SIZE)):
                        threads.append(multiprocessing.Process(target=self.worker,args=(list(indices+[j]),)))
                        threads[-1].start()
                    for j in range(min(domainSize-i,POOL_SIZE)):
                        threads[j].join()
                    for j in range(min(domainSize-i,POOL_SIZE)):
                        val = self.results[j]
                        worstDiff = max(worstDiff,val)

                return worstDiff

            for i in range(len(self.prob.disc[len(indices)])):
                worstDiff = max(worstDiff,self.modelIteration(indices + [i]))

            if(len(indices)):
                print("\r" + str(indices[-1]/len(self.prob.disc[len(indices)])), end='')
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
