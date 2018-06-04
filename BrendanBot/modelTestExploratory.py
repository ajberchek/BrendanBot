import random
import pickle
from probMaker import probArr
from modelMaker import Model
import os.path
import os

TRAINING_DATA = "../data/trainingData.txt"
POLICY_PICKLED = "../data/serializedPolicy.bin"
EXPLORE_PROB = 0.2

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

        for i in range(0, numState):
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
    builtStr = "|".join(initWordReward + action)
    return builtStr in valid

def getIndicesArray(valsArray, probObj):
    toRet = []
    for i in range(len(valsArray)):
        toRet.append(probObj.getIndex(valsArray[i],probObj.disc[i]))
    return toRet


policy = None
prob = None
if(os.path.exists(POLICY_PICKLED) and os.path.getmtime(TRAINING_DATA) >= os.path.getmtime(POLICY_PICKLED)):
    prob = probArr("../data/trainingData.txt")
    mdp = Model(prob,wordToReward,rewardFunc)
    policy = mdp.policy
    f = open(POLICY_PICKLED, 'wb')
    pickle.dump(policy,f)
    f.close()
else:
    if(not os.path.exists(POLICY_PICKLED)):
        fd = open(POLICY_PICKLED, 'a')
        fd.close()

        prob = probArr("../data/trainingData.txt")
        mdp = Model(prob,wordToReward,rewardFunc)
        policy = mdp.policy
        f = open(POLICY_PICKLED, 'wb')
        pickle.dump(policy,f)
        f.close()
    else:
        print("LOAD")
        prob = probArr("../data/trainingData.txt")
        f = open(POLICY_PICKLED, 'rb')
        policy = pickle.load(f)
        f.close()


state = ["sun"]
print(state[-1], end = ' ')
#for i in range(2*prob.states):
#    state.append(prob.disc[-1][random.randint(0,prob.actions-1)])
#    print("State: " + str(state))
#    print(state[-1], end = ' ')

numWords = 100

while(numWords):
    indices = getIndicesArray(state, prob)
    chosenWord = policy.get(repr(indices))
    if(random.uniform(0,1) < EXPLORE_PROB):
        # Attempts to find a word that works with the list of seen word pairs, even
        # if that word pair is suboptimal, in order to break out of loops
        tries = 0
        while(tries < len(prob.disc[-1])):
            trialWord = prob.disc[-1][random.randint(0,len(prob.disc[-1])-1)]
            if '|'.join(state + [trialWord]) in valid:
                chosenWord = trialWord
                break
            tries += 1

    state = state[1:] + [chosenWord]

    print(state[-1], end = ' ')
    numWords -= 1