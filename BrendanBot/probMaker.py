class probArr:
    #File format:
    #Number of states
    #Number of actions
    #UpperBoundBucket0,UpperBoundBucket1,...,UpperBoundBucketN-1,LowerBoundBucketN repeated number of states times
    #UpperBoundBucket0,UpperBoundBucket1,...,UpperBoundBucketN-1,LowerBoundBucketN repeated number of actions times
    #Then the data should follow, formatted as time,state0|state1|...|stateN,action0|action1|...|actionN
    def __init__(self,filename, typeDelimiter='|', delimiter='@'):
        self.states = 0
        self.actions = 0
        self.disc = []
        self.priorCount = {}
        self.probMatr = []
        self.filename = filename

        self.datFile = open(self.filename,'r')
        self.typeDelimiter = typeDelimiter
        self.delimiter = delimiter
        self.createDiscretizations()
        self.buildProbMatr()

    def getIndex(self,value,discretization):
        #Could switch to binary search
        index = 0
        while index < len(discretization) and value != discretization[index]:
            index += 1
        return index

    def createDiscretizations(self):
        self.states = int(self.datFile.readline())
        self.actions = int(self.datFile.readline())
        for _ in range(0,self.states+self.actions):
            toAppend = [i.strip() for i in self.datFile.readline().split(self.typeDelimiter)]
            self.disc.append(toAppend)

    def buildProbMatr(self):
        lastState = None
        lastAction = None
        for line in self.datFile:
            parsed = line.split(self.delimiter)
            lastState = parsed[0].split(self.typeDelimiter)
            if(len(parsed) > 2):
                lastAction = parsed[2].split(self.typeDelimiter)
                thisState = parsed[1].split(self.typeDelimiter)
            else:
                thisState = parsed[1].split(self.typeDelimiter)

            indices = []
            probPointer = self.probMatr

            #State Prime
            for i in range(0,len(thisState)):
                if(len(probPointer) != len(self.disc[i])+1):
                    for _ in range(len(self.disc[i])+1):
                        probPointer.append([])
                probPointer = probPointer[self.getIndex(thisState[i],self.disc[i])]

            #State
            for i in range(0,len(lastState)):
                if(len(probPointer) != len(self.disc[i])+1):
                    for _ in range(len(self.disc[i])+1):
                        probPointer.append([])
                index = self.getIndex(lastState[i],self.disc[i])
                indices.append(index)
                probPointer = probPointer[index]

            #Action
            if(lastAction != None):
                for i in range(0,len(lastAction)):
                    dimension = i + len(lastState)
                    if(len(probPointer) != len(self.disc[dimension])+1):
                        for _ in range(len(self.disc[dimension])+1):
                            probPointer.append([])
                    index = self.getIndex(lastAction[i],self.disc[dimension])
                    indices.append(index)
                    probPointer = probPointer[index]

            self.priorCount[repr(indices)] = self.priorCount.get(repr(indices),0) + 1

            #If this statePrime,state,action hasn't been seen before, add an entry for it
            if(len(probPointer) == 0):
                probPointer.append(0)
            probPointer[0] += 1

        #Normalize the probMatrix
        self.normalize()

    def normalize(self,indices=[]):
        dimension = len(indices)
        if(dimension == 2*self.states+self.actions):
            probPointer = self.probMatr
            for i in range(len(indices)):
                probPointer = probPointer[indices[i]]
            if(len(probPointer)):
                probPointer[0] /= self.priorCount[repr(indices[self.states:])]
        else:
            if(dimension >= self.states):
                dimension -= self.states
            probPointer = self.probMatr
            for i in range(len(indices)):
                probPointer = probPointer[indices[i]]
            for i in range(len(probPointer)):
                if(len(probPointer[i])):
                    self.normalize(indices + [i])
    
    def printProbMatr(self,indices=[]):
        dimension = len(indices)
        if(dimension == 2*self.states+self.actions):
            #We have reached the end and can print out the probability now
            probPointer = self.probMatr
            for i in range(len(indices)):
                probPointer = probPointer[indices[i]]
            if(len(probPointer)):
                for _ in range(dimension):
                    print("\t",end='')
                print("Prob is: " + str(probPointer[0]))
        else:
            #We haven't reached the probability yet, so we need to keep traversing
            #through state prime, state, and action possibilities in a depth first
            #traversal
            if(dimension >= self.states):
                #Correct for the case of making it through the elements of state prime
                dimension -= self.states
            probPointer = self.probMatr
            for i in range(len(indices)):
                #Move down to the proper sub list in our probability matrix
                probPointer = probPointer[indices[i]]
            for i in range(len(probPointer)):
                if(len(probPointer[i])):
                    for _ in range(len(indices)):
                        print("\t",end='')
                    if(i == len(probPointer)-1):
                        print("Greater than " + str(self.disc[dimension][i-1]) + ":")
                    else:
                        print(str(self.disc[dimension][i]) + ":")
                    self.printProbMatr(indices + [i])
