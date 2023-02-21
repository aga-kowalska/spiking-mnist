import sys

NUMBER_CATEGORY_NEURONS = 100
EPOCH_LENGTH = 100.0

def readSpikeFile(fileName):
    spikeMatrix = []
    for catNeuron in range (0,NUMBER_CATEGORY_NEURONS):
        spikeMatrix = spikeMatrix + [[]]
    fileHandle = open(fileName)
    inputLine = " "
    startNeuron = -1
    while (inputLine.__len__() > 0):
        inputLine = fileHandle.readline()
        if (inputLine.__len__() > 0):
            args = inputLine.split(' ')
            neuron = int(args[0])
            if (neuron > startNeuron):
                if (startNeuron >= 0):
                    spikeMatrix[startNeuron] =  neuronSpikeVector
                if (neuron != (startNeuron+1)):
                    print("error no spikes from cat", neuron)
                startNeuron = neuron
                neuronSpikeVector = []
            time = float(args[1])
            neuronSpikeVector = neuronSpikeVector + [time]
            #print (inputLine)

    fileHandle.close()
    
    spikeMatrix[startNeuron] = neuronSpikeVector
    return spikeMatrix
    
def readCSVFile(fileName):
    categories = []
    fileHandle = open(fileName)
    inputLine = " "
    while (inputLine.__len__() > 0):
        inputLine = fileHandle.readline()
        if (inputLine.__len__() > 0):
            args = inputLine.split(',')
            category = int(args[64])
            categories=categories + [category]

    fileHandle.close()
    return categories

def getWinner(time, spikeMatrix):
    numberCategoryNeurons = len (spikeMatrix)
    firstCategoryToSpike = -1
    firstSpikeTime = time + EPOCH_LENGTH
    countUncategorised = 0
    for neuron in range (0,numberCategoryNeurons):
        neuronSpikeVector = spikeMatrix[neuron]
        spikeNumber = 0
        while ((len(neuronSpikeVector) > spikeNumber) and
               (neuronSpikeVector[spikeNumber] < time)):
                spikeNumber += 1

        #If there is a spike in this epoch
        if (len(neuronSpikeVector) > spikeNumber):
            thisFirstSpikeTime = neuronSpikeVector[spikeNumber]
            if (thisFirstSpikeTime < firstSpikeTime):
                firstCategoryToSpike = neuron
                firstSpikeTime = thisFirstSpikeTime
        
    
    return firstCategoryToSpike

def getWinners(categories, spikeMatrix):
    winners = []
    epochLength = EPOCH_LENGTH 

    for input in range (0, len(categories)):
        time = input*epochLength
        winner = getWinner(time,spikeMatrix)
        winners = winners + [[categories[input],winner]]

    return winners
    
def calcWinsPerCatNeuron(winners,numberCatNeurons):
    overallWins = []
    for neuron in range (0,numberCatNeurons):
        wins = 0
        for winner in winners:
            if (winner[1] == neuron):
                wins += 1
        overallWins = overallWins + [[neuron,wins]]
    return overallWins

##--main---
args = sys.argv
numberArgs = args.__len__()
#print (numberArgs,args)
if (numberArgs == 3):
    csvFileName = args[1]
    spikeFileName = args[2]
else:
    print("need csv file and spike file")

categories = readCSVFile(csvFileName)
#print (categories)
spikeMatrix=readSpikeFile(spikeFileName)
#print(spikeMatrix)
#print(len(spikeMatrix))
winners = getWinners(categories,spikeMatrix)
print (winners)
numberWinsPerCatNeuron = calcWinsPerCatNeuron(winners,NUMBER_CATEGORY_NEURONS)
#print(numberWinsPerCatNeuron)
