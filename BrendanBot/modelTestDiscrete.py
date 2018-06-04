import random
from probMaker import probArr
from modelMaker import Model

valid = {}
numState = 0
numAction = 0
with open("../data/trainingData.txt", 'r') as f:
    numState = int(f.readline())
    numAction = int(f.readline())
    for i in range(numState+numAction):
        f.readline()
    for line in f:
        builtStr = ""
        opts = line.strip().split("@")
        words = []
        for opt in opts:
            words += opt.split("|")

        for i in range(numAction, numState):
            if(len(builtStr) != 0):
                builtStr += "|"
            builtStr += words[i]
        for i in range(2*numState,len(words)-1):
            builtStr += "|"
            builtStr += words[i]

        valid[builtStr] = words[-1]

def wordToReward(state,disc):
    toRet = []
    for i in range(len(state)):
        toRet.append(disc[i][state[i]])
    return toRet

def rewardFunc(finalWordReward,initWordReward,action):
    builtStr = "|".join(initWordReward[len(action):] + action)
    return builtStr in valid

def getIndicesArray(valsArray, probObj):
    toRet = []
    for i in range(len(valsArray)):
        toRet.append(probObj.getIndex(valsArray[i],probObj.disc[i]))
    return toRet


prob = probArr("../data/trainingData.txt")
mdp = Model(prob,wordToReward,rewardFunc)

state = ["the", "dog"]
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