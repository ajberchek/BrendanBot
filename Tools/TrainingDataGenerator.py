from os import walk
import os.path
toExclude = ["TrainingDataGenerator.py", "trainingData.txt", "serializedPolicy.bin"]
words = set([])
stateCounts = {}
stateLength = 1
actionLength = 1
delimiter = '@'
typeDelimiter = '|'
trainingDataFile = "trainingData.txt"

def gatherData(filepath):
    state = []
    f = open(filepath, 'r')
    for line in f:
        if(line == "\n"):
            continue
        for word in line.split():
            words.add(word)
            state.append(word)
            if(len(state) >= stateLength+actionLength):
                stateRepr = typeDelimiter.join(state[:-actionLength])
                stateRepr += delimiter
                stateRepr += typeDelimiter.join(state[stateLength:])

                stateCounts[stateRepr] = stateCounts.get(stateRepr,0) + 1
                state = state[1:]
    f.close()

for root, dirs, files in walk("../data/"):
    for file in files:
        print("FILE: " + file)
        if not file in toExclude:
            gatherData(os.path.join(root,file))

with open("../data/" + trainingDataFile, 'w') as f:
    f.write(str(stateLength) + "\n")
    f.write(str(actionLength) + "\n")
    domain = typeDelimiter.join(words) + "\n"
    for _ in range(stateLength+actionLength):
        f.write(domain)
    for key,val in stateCounts.items():
        toWrite = [key.split(delimiter)[0], key, str(val)]
        f.write(delimiter.join(toWrite) + "\n")
