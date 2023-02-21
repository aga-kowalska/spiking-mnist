import sys

NUMBER_CATEGORY_NEURONS = 100
GUESS_CATEGORY = 8
EPOCH_LENGTH = 100.0

#Read in a csv file and return a numLines by 64 matrix
def readMNISTFile(fileName):
    line = " "
    answerVector = []
    fileHandle=open(fileName,'r')

    while (line.__len__() > 0):
        line = fileHandle.readline()
        if (line.__len__() > 0):
            args = line.split(",")
            answer = int(args[64]) #the answer is the last in the vector
            answerVector = answerVector + [answer]
    fileHandle.close()
    
    return answerVector

def readCategorySpikeMatrix(spikeFileName):
    #print (spikeFileName)
    spikeMatrix = []
    for currentNeuron in range (0,NUMBER_CATEGORY_NEURONS):
        spikeMatrix = spikeMatrix + [[]]

    fileHandle=open(spikeFileName,'r')

    line = " "
    while (line.__len__() > 0):
        line = fileHandle.readline()
        if (line.__len__() > 0):
            args = line.split(" ")
            neuronNumber = int(args[0])
            time = float(args[1])
            neuronsSpikes = spikeMatrix[neuronNumber]
            neuronsSpikes = neuronsSpikes + [time]
            spikeMatrix[neuronNumber] = neuronsSpikes
            
    fileHandle.close()
    
    return spikeMatrix

def getNeuronWinner(testCycle,categorySpikeMatrix):
    startTime = testCycle*EPOCH_LENGTH

    winner = -1
    firstTime = startTime+EPOCH_LENGTH
    for neuron in range (0,NUMBER_CATEGORY_NEURONS):
        spikeTrain = categorySpikeMatrix[neuron]
        if (len(spikeTrain) > 0):
            spikeOffset = 0
            currentSpike = spikeTrain[spikeOffset]
            while ((currentSpike < startTime) and (spikeOffset < len(spikeTrain))):
                currentSpike = spikeTrain[spikeOffset]
                spikeOffset = spikeOffset + 1
            if  (currentSpike < firstTime):
                winner = neuron
                firstTime = currentSpike
    return winner

def getAnswerPairs(dataFileName,spikeFileName):
    actualAnswers = readMNISTFile(dataFileName)
    spikeMatrix = readCategorySpikeMatrix(spikeFileName)
    #print (spikeMatrix)

    answerPairs = []
    for answerNumber in range (0,len(actualAnswers)):
        actualAnswer = actualAnswers[answerNumber]
        neuronWinner=getNeuronWinner(answerNumber,spikeMatrix)
        answerPair = [actualAnswer,neuronWinner]
        answerPairs =     answerPairs  + [answerPair]
    return (answerPairs)

def calcWinsPerCatNeuron(winners,numberCatNeurons):
    overallWins = []
    for neuron in range (0,numberCatNeurons):
        wins = 0
        for winner in winners:
            if (winner[1] == neuron):
                wins += 1
        overallWins = overallWins + [[neuron,wins]]
    return overallWins

def initCategoryForNeuronPairs():
    categoryForNeuronPairs = []
    ignoreValue = -2;
    for neuron in range (0,NUMBER_CATEGORY_NEURONS):
        pair = [neuron,ignoreValue]
        categoryForNeuronPairs = categoryForNeuronPairs + [pair]

    return categoryForNeuronPairs

#Find the neurons that only win 1, and make their category that.
def setOnesAndZeros(winsPerCat,answerPairs,categoryForNeuronPairs):
    for catNeuron in range (0,NUMBER_CATEGORY_NEURONS):
        winPerCat = winsPerCat[catNeuron]

        if (winPerCat[1] == 0):
            answerCat = GUESS_CATEGORY
            categoryForNeuronPairs[catNeuron][1]= answerCat
        elif (winPerCat[1] == 1):
            #Look through the answer pairs to see when this catNeuron wins
            for answerPair in answerPairs:
                if (answerPair[1] == catNeuron):
                    answerCat = answerPair[0]
            categoryForNeuronPairs[catNeuron][1]= answerCat
            
    return categoryForNeuronPairs

def getMostFrequentAnswer(catNeuron, answerPairs):
    answerCat = -1
    mostAnswers = 0
    for category in range (0,9):
        answers = 0
        for answerPair in answerPairs:
            if ((answerPair[1] == catNeuron) and (answerPair[0] == category)):
                answers += 1
        if (answers > mostAnswers):
            answerCat = category
            mostAnswers = answers
    
    return answerCat

def setOtherPositives(winsPerCat,answerPairs,categoryForNeuronPairs):
    for catNeuron in range (0,NUMBER_CATEGORY_NEURONS):
        winPerCat = winsPerCat[catNeuron]

        if (winPerCat[1] > 1):
            answerCat = getMostFrequentAnswer(catNeuron,answerPairs)
            categoryForNeuronPairs[catNeuron][1]= answerCat
    return categoryForNeuronPairs

##--main---
args = sys.argv
numberArgs = args.__len__()
#print (numberArgs,args)
if (numberArgs == 3):
    csvFileName = args[1]
    spikeFileName = args[2]
#else:
#    print("need csv file and spike file")

categoryForNeuronPairs = initCategoryForNeuronPairs()
#print (categoryForNeuronPairs)

answerPairs = getAnswerPairs(csvFileName,spikeFileName)
#print ("answerPairs",answerPairs)

numberWinsPerCatNeuron = calcWinsPerCatNeuron(answerPairs,
                                              NUMBER_CATEGORY_NEURONS)
#print(numberWinsPerCatNeuron)

categoryForNeuronPairs = setOnesAndZeros(numberWinsPerCatNeuron,answerPairs, categoryForNeuronPairs)
categoryForNeuronPairs = setOtherPositives(numberWinsPerCatNeuron,answerPairs, categoryForNeuronPairs)
print(categoryForNeuronPairs)
