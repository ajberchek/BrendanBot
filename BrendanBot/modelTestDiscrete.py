import random
from probMaker import probArr
from modelMaker import Model

valid = {}
with open("../data/trainingData.txt", 'r') as f:
    numState = int(f.readline())
    numAction = int(f.readline())
    for i in range(numState+numAction):
        f.readline()
    for line in f:
        builtStr = ""
        words = line.strip().split(",")
        for i in range(numState):
            if(len(builtStr) != 0):
                builtStr += ","
            builtStr += words[i]
        for i in range(2*numState,len(words)-1):
            builtStr += "," + words[i]

        valid[builtStr] = words[-1]

def wordToReward(state,disc):
    if(len(state)):
        return disc[0][state[0]]
    else:
        return None

def rewardFunc(finalWordReward,initWordReward,action):
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