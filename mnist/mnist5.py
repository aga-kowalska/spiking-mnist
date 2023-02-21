"""
It's the 64 input MNist task from CST 3170.  Read in a csv input file.
Setup a network of 64 input neurons, many category neurons, and an
inhibtory layer.  The input to category is plastic.  Save the
synapses at the end. 

call with 
    python mnist4.py (optional csv input file name)
    python mnist4.py (csv synapseInputFile)
    python mnist4.py (csv synapseInputFile synapseOutputFile)
"""
import sys
import pickle as Pickle
import random

import pyNN.nest as sim


TIME_STEP = 0.1

neuronsInInputLayer = 64
neuronsInCategoryLayer = 100
neuronsInInhibitoryLayer = 2
EPOCH_LENGTH = 100.0

W_MAX = 0.01
TOP_TARGET_FIRING = 281
BOTTOM_TARGET_FIRING = 100
systemMadeCompensatoryChange = False

#initialize the simulator. 
def init(): 
    sim.setup(timestep=TIME_STEP,min_delay=TIME_STEP,
                    max_delay=TIME_STEP, debug=0)

def createDCSource(inputWeight,startTime):
    duration = 60.0
    stopTime = startTime+duration
    base = 0.7
    increment = 0.1
    myAmplitude = base + (increment*inputWeight)
    dCSource = sim.DCSource(amplitude=myAmplitude, start=startTime,
                            stop=stopTime)
    return dCSource

def createSourcesForInputLine(startTime,inputLine):
    dCSources = []
    for inputOffset in range (0,neuronsInInputLayer):
        if (inputLine[inputOffset] > 0):
            dCSource = createDCSource(inputLine[inputOffset],startTime)
        else:
            dCSource = 0
        dCSources = dCSources + [dCSource]
    return dCSources

def createDCSources(inputValueMatrix):
    allDCSources = []
    numberInputs = len(inputValueMatrix)
    startTime = 20.0
    epochLength = EPOCH_LENGTH

    for line in range (0,numberInputs): 
        dCSources = createSourcesForInputLine(startTime,inputValueMatrix[line])
        allDCSources = allDCSources + dCSources
        startTime = startTime+epochLength

    return allDCSources


#There should be numberInputs*neuronsInInputLayer sources
def connectInput(dCSources, cells,numberInputs):
    for input in range (0, numberInputs):
        for source in range (0, neuronsInInputLayer):
            sourceNumber = source+(neuronsInInputLayer*input)
            #For 0 input no dcsource is made in createSourcesForInputLine.
            if (dCSources[sourceNumber] != 0):
                dCSources[sourceNumber].inject_into(cells[source:(source+1)])


def printPlasticSynapticPairWeights(initialList,finalList):
    if (initialList.__len__() != finalList.__len__()): 
        print ("error ppspw")

    #print(initialList.__len__())
    totalDiff = 0.0
    for offset in range (0,initialList.__len__()):
        initialSynapse = initialList[offset]
        finalSynapse = finalList[offset]
        if (initialSynapse[0] != finalSynapse[0]): 
            print ("error ppspwFrom")
        if (initialSynapse[1] != finalSynapse[1]): 
            print ("error ppspwTo")

        difference = initialSynapse[2]-finalSynapse[2]
        initialWeight = "{:.5f}".format(initialSynapse[2])
        finalWeight = "{:.5f}".format(finalSynapse[2])
        formDiff = "{:.5f}".format(difference)
        print (initialSynapse[0],initialSynapse[1],initialWeight,
               finalWeight,formDiff)
        totalDiff += difference
    print ("total change", totalDiff, totalDiff/initialList.__len__())        
    
def printPlasticSynapticWeights(synapseList):
    for synapse in synapseList:
        print (synapse[0],synapse[1],synapse[2])

def readSynapses(numberFromCells,numberToCells,fileName):
    fileHandle=open(fileName,'rb')
    synapseWeightList = Pickle.load(fileHandle)
    fileHandle.close()

    connector = []
    for synapse in synapseWeightList:
        fromNeuron = synapse[0]
        toNeuron = synapse[1]
        weight = synapse[2]
        if (weight < 0):
            print ("negative", synapse)
        elif (weight > W_MAX):
            print ("too big", synapse)
        connector = connector + [(fromNeuron,toNeuron,weight,TIME_STEP)]
        
    return connector
    
        
def getNewSynapses(numberFromCells,numberToCells):
    random.seed(1)

    #setup initial weights
    connector = []
    mu = 0.0014
    sigma = 0.0002
    for fromNeuron in range(0,numberFromCells):
        for toNeuron in range(0,numberToCells):
            weight = random.gauss(mu,sigma)
            if (weight < 0):
                weight = 0.0
            
            connector = connector + [(fromNeuron,toNeuron,weight,TIME_STEP)]
    return connector

def staticConnectInputToCategoryLayer(fromCells,toCells,numberFromCells,
                                      numberToCells,useStoredSynapses,
                                      synapseFileName):

    if (useStoredSynapses):
        connector = readSynapses(numberFromCells,numberToCells,synapseFileName)
    else:
        connector = getNewSynapses(numberFromCells,numberToCells)
    listConnector = sim.FromListConnector(connector)

    inputToCategorySynapses = sim.Projection(fromCells,toCells, listConnector)
    
    return inputToCategorySynapses


def connectInputToCategoryLayer(fromCells, toCells,numberFromCells,
                            numberToCells,useStoredSynapses,synapseFileName):

    stdp_model = sim.STDPMechanism(
        timing_dependence=sim.SpikePairRule(tau_plus=5.0,tau_minus=5.0,
                                            A_plus=0.0001, A_minus=0.0001),
        weight_dependence=sim.MultiplicativeWeightDependence(w_min=0.0,
                                                             w_max=W_MAX),
        weight=0.0, delay=TIME_STEP, dendritic_delay_fraction=float(1))

    if (useStoredSynapses):
        connector = readSynapses(numberFromCells,numberToCells,synapseFileName)
    else:
        connector = getNewSynapses(numberFromCells,numberToCells)

    listConnector = sim.FromListConnector(connector)


    inputToCategorySynapses = sim.Projection(fromCells,toCells,
                   listConnector, synapse_type = stdp_model)
    
    return inputToCategorySynapses

def connectCategoryToInhibLayer(categoryCells, inhibCells):
    categoryToInhibConnector = []
    weight = 0.01
    for fromNeuron in range(0,neuronsInCategoryLayer):

########??? why (0.002*toNeuron) is added to the weight???

        for toNeuron in range(0,neuronsInInhibitoryLayer):
            thisWeight = weight+(0.002*toNeuron) 
            categoryToInhibConnector = categoryToInhibConnector + [
                (fromNeuron,toNeuron,thisWeight,TIME_STEP)]
    categoryToInhibListConnector = sim.FromListConnector(categoryToInhibConnector)


    sim.Projection(categoryCells,inhibCells, categoryToInhibListConnector)

def connectInhibToCategory(categoryCells, inhibCells):
    inhibToCategoryConnector = []
    weight = -0.01
    for fromNeuron in range(0,neuronsInInhibitoryLayer):
        for toNeuron in range(0,neuronsInCategoryLayer):
            varWeight = weight - (fromNeuron*0.001)
            inhibToCategoryConnector = inhibToCategoryConnector + [
                (fromNeuron,toNeuron,varWeight,TIME_STEP)]
    inhibToCategoryListConnector = sim.FromListConnector(inhibToCategoryConnector)

    sim.Projection(inhibCells,categoryCells, inhibToCategoryListConnector)

def connectCategoryAndInhibLayers(categoryCells, inhibCells):
    connectCategoryToInhibLayer(categoryCells,inhibCells)
    connectInhibToCategory(categoryCells,inhibCells)


def createDefaultNeurons(numberNeurons):
    cells=sim.Population(numberNeurons,sim.IF_cond_exp,cellparams={})
    return cells

def createCategoryNeurons(numberNeurons):
    #params = {'v_reset':-700.0}
    params = {}
    cells=sim.Population(numberNeurons,sim.IF_cond_exp,cellparams=params)
    return cells

def setupRecording(cells):
    cells.record({'spikes'})

def printResults(simCells,file):
    simCells.write_data(file+".pkl",'spikes')
    #simCells.write_data(file+"V.pkl",'v')
    #simCells.write_data(file+"W.pkl",'w')

def saveSynapses(synapseWeights,outputFileName):
    #synapseWeights = synapses.get(["weight"],format="list")
    fileHandle=open(outputFileName,'wb')
    Pickle.dump(synapseWeights,fileHandle)
    fileHandle.close()

#Read in a csv file and return a numLines by 64 matrix
def readMNistFile(fileName):
    line = " "
    resultMatrix = []
    fileHandle=open(fileName,'r')
    while (line.__len__() > 0):
        line = fileHandle.readline()
        if (line.__len__() > 0):
            args = line.split(",")
            vector = []
            for offset in range (0,64): #ignore the answer
                input = int (args[offset])
                vector = vector + [input]
            resultMatrix = resultMatrix+[vector]
            
    fileHandle.close()
    
    return resultMatrix

def getSpikesPerNeuron(cells):
    spikesPerNeuron = []
    
    spikeData = categoryCells.get_data('spikes')
    segments = spikeData.segments
    segment = segments[0]
    spikeTrains = segment.spiketrains
    #print (spikeTrains)
    for neuron in range (0,len(spikeTrains)):
        #print(spikeTrains[neuron],len(spikeTrains[neuron]))
        spikesPerNeuron = spikesPerNeuron + [len(spikeTrains[neuron])]

    return spikesPerNeuron

def getNewWeight(oldWeight,spikes):
    rateOfPositiveChange = .000001
    rateOfNegativeChange = .0000007
    w_max=W_MAX
    if (spikes > TOP_TARGET_FIRING):
        newWeight = oldWeight - ((spikes-TOP_TARGET_FIRING)*rateOfNegativeChange)
        if (newWeight < 0.0):
            newWeight = 0.0
        #print ("dec", newWeight,oldWeight)
    elif (spikes < BOTTOM_TARGET_FIRING):
        newWeight = oldWeight + ((BOTTOM_TARGET_FIRING-spikes)*rateOfPositiveChange)
        if (newWeight > w_max):
            newWeight = w_max
        #print ("inc", newWeight,oldWeight)
    else:
        newWeight = oldWeight

    return newWeight
    
def postCompensatoryChange(finalSynapseWeights, categoryCells):
    global systemMadeCompensatoryChange
    newWeights = []
    neuronsIncreasing=0
    neuronsDecreasing=0

    spikesPerNeuron = getSpikesPerNeuron(categoryCells)
    #print (spikesPerNeuron)

    for neuron in range (0,len(categoryCells)):
        if (spikesPerNeuron[neuron] > TOP_TARGET_FIRING):
            print("compensatory decrease to neuron ",neuron,
                  spikesPerNeuron[neuron])
            neuronsDecreasing+=1
            systemMadeCompensatoryChange = True

        elif (spikesPerNeuron[neuron] <  BOTTOM_TARGET_FIRING):
            print("compensatory increase to neuron ",neuron,
                  spikesPerNeuron[neuron])
            neuronsIncreasing+=1
            systemMadeCompensatoryChange = True

        for synapse in finalSynapseWeights:
            if (synapse[1] == neuron):
                newWeight = getNewWeight(synapse[2],spikesPerNeuron[neuron])
                newSynapse = [synapse[0],synapse[1],newWeight]
                newWeights = newWeights+[newSynapse]
    
    
    #print (finalSynapseWeights,len(categoryCells))
    print ("Neurons decreasing ", neuronsDecreasing, " increasing",
           neuronsIncreasing)

    return newWeights

    
##--main---
args = sys.argv
numberArgs = args.__len__()
fInitWithStoredSynapses = False
synapseFileName = ""
outputSynapseFileName = "initialSynapseWeights.pkl"
plasticSynapses = True

print(numberArgs,args)
if (numberArgs == 2):
    inputFileName = args[1]    
elif (numberArgs == 3):
    inputFileName = args[1]
    synapseFileName = args[2]
    fInitWithStoredSynapses = True
#Standard way to call during training.
#Call with input, inputSyn, outputSyn
elif (numberArgs == 4):
    inputFileName = args[1]
    synapseFileName = args[2]
    outputSynapseFileName = args[3]
    fInitWithStoredSynapses = True
#maybe I can do something better here, but
elif (numberArgs == 5):
    runMode = int(args[1])
    inputFileName = args[2]
    synapseFileName = args[3]
    outputSynapseFileName = args[4]
    if (runMode == 1):
        print("test run no synaptic change")
        plasticSynapses = False
        compensatoryChange = False
        fInitWithStoredSynapses = True
    elif (runMode == 2):
        print("compensatory run")
        plasticSynapses = False
        compensatoryChange = True
        fInitWithStoredSynapses = True
    elif (runMode == 3):
        print("STDP run")
        plasticSynapses = True
        compensatoryChange = False
        fInitWithStoredSynapses = True
    elif (runMode == 4):
        print("init synapses with compensatory run")
        plasticSynapses = False
        compensatoryChange = True
        fInitWithStoredSynapses = False
    elif (runMode == 5):
        print("init synapses run")
        plasticSynapses = False
        compensatoryChange = False
        fInitWithStoredSynapses = False
    else:
        print("error:  wrong run mode")
        
else:
    #No args, just create an initial synapse net.
    inputFileName = ""

if (len(inputFileName) == 0):
    inputValueMatrix = []
else:
    inputValueMatrix = readMNistFile(inputFileName)
numberInputs=len(inputValueMatrix)

init()
inputCells = createDefaultNeurons(neuronsInInputLayer)
categoryCells = createCategoryNeurons(neuronsInCategoryLayer)
inhibLayerCells = createDefaultNeurons(neuronsInInhibitoryLayer)

sources = createDCSources(inputValueMatrix)

connectInput(sources,inputCells,numberInputs)

if (plasticSynapses):
    inputToCategorySynapses = connectInputToCategoryLayer(inputCells,
                    categoryCells,neuronsInInputLayer,neuronsInCategoryLayer,
                    fInitWithStoredSynapses,synapseFileName)
else:
    inputToCategorySynapses = staticConnectInputToCategoryLayer(inputCells,
                    categoryCells,neuronsInInputLayer,neuronsInCategoryLayer,
                    fInitWithStoredSynapses, synapseFileName)

initialSynapseWeights = inputToCategorySynapses.get(["weight"],format="list")

connectCategoryAndInhibLayers(categoryCells,inhibLayerCells)


setupRecording(inputCells)
setupRecording(categoryCells)
setupRecording(inhibLayerCells)

duration = (numberInputs+1)*EPOCH_LENGTH
print ("start", len(initialSynapseWeights))
sim.run(duration)

printResults(inputCells,"output/input")
printResults(categoryCells,"output/category")
printResults(inhibLayerCells,"output/inhib")

if (plasticSynapses):
    finalSynapseWeights = inputToCategorySynapses.get(["weight"],format="list")
    saveSynapses(finalSynapseWeights,outputSynapseFileName)

#printPlasticSynapticPairWeights(initialSynapseWeights,finalSynapseWeights)
elif (compensatoryChange):
    compensatoryWeights = postCompensatoryChange(initialSynapseWeights, 
                                                 categoryCells)
    #print (compensatoryWeights)
    saveSynapses(compensatoryWeights,outputSynapseFileName)

else: #original weights
    finalSynapseWeights = inputToCategorySynapses.get(["weight"],format="list")
    saveSynapses(finalSynapseWeights,outputSynapseFileName)

if (systemMadeCompensatoryChange):
    print("compensatory change made")
