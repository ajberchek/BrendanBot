import random
from probMaker import probArr
from modelMaker import Model

def wordToReward(state,disc):
    if(len(state)):
        return disc[0][state[0]]
    else:
        return None

def rewardFunc(finalWordReward,initWordReward,action):
    valid = {}
    valid["the,dog"] = 1
    valid["dog,goes"] = 1
    valid["goes,meow"] = 1
    valid["meow,the"] = 1
    return (initWordReward+","+action) in valid

def getIndicesArray(valsArray, probObj):
    toRet = []
    for i in range(len(valsArray)):
        toRet.append(probObj.getIndex(valsArray[i],probObj.disc[i]))
    return toRet


prob = probArr("../data/trainingData.txt")
mdp = Model(prob,wordToReward,rewardFunc)
mdp.printPolicy()

state = ["the"]
print(state[-1], end = ' ')
#for i in range(2*prob.states):
#    state.append(prob.disc[-1][random.randint(0,prob.actions-1)])
#    print("State: " + str(state))
#    print(state[-1], end = ' ')

numWords = 100

while(numWords):
    indices = getIndicesArray(state, mdp.prob)
    chosenWord = mdp.policy.get(repr(indices))
    state = state[1:] + [chosenWord]

    print(state[-1], end = ' ')
    numWords -= 1