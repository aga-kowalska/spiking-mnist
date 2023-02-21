"""
It's the 64 input MNIST task from CST 3170.  Read in a csv input file.
Setup a network of 64 input neurons, many category neurons, and an
inhibtory layer.  The input to category is plastic.  Save the
synapses at the end. 

call with 
    python mnist6.py 
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
    params = {'b':0.1}
    cells=sim.Population(numberNeurons,sim.EIF_cond_exp_isfa_ista,cellparams=params)
    return cells

def setAdaptationValues(simCells,fileName):
    adaptationValues = []
    fileHandle=open(fileName,'r')
    
    for neuron in range (0,neuronsInCategoryLayer):
        inputString = fileHandle.readline()
        args = inputString.split(' ')
        adaptationValue = float(args[1])
        adaptationValues = adaptationValues+[adaptationValue]
    fileHandle.close()

    #print(adaptationValues)
    simCells.initialize(w=adaptationValues)   


def setupRecording(cells):
    cells.record({'spikes'})

def setupAdaptiveRecording(cells):
    cells.record({'spikes','w'})

def printResults(simCells,file):
    simCells.write_data(file+".pkl",'spikes')
    #simCells.write_data(file+"V.pkl",'v')
    #simCells.write_data(file+"W.pkl",'w')

#write the final adaptation value to file
def storeFinalAdaptation(simCells,fileName):
    neoObj = simCells.get_data('w')
    #print (neoObj)
    segments = neoObj.segments
    segment=segments[0]
    analogSignals=segment.analogsignals
    adaptationMatrix=analogSignals[0]
    lastStep = len (adaptationMatrix) -1
    finalAdapatationValues = adaptationMatrix[lastStep]
    #print(finalAdapatationValues)
    #print(len(finalAdapatationValues))

    fileHandle=open(fileName,'w')
    for neuron in range (0, len(finalAdapatationValues)):
        #outputString = str(neuron) + " "+finalAdapatationValues[neuron]
        fileHandle.write (str(neuron))
        fileHandle.write (" ")
        fileHandle.write (str(finalAdapatationValues[neuron]))
        fileHandle.write ("\n")
    fileHandle.close()
    

    
def storeAdaptation(simCells,file):
    simCells.write_data(file,'w')
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

##--main---
args = sys.argv
numberArgs = args.__len__()
fInitWithStoredSynapses = False
synapseFileName = ""
outputSynapseFileName = "initialSynapseWeights.pkl"
plasticSynapses = True
useOldAdaptationValues = True

print(numberArgs,args)
if (numberArgs == 2):
    inputFileName = args[1]    
    plasticSynapses = True
    outputSynapseFileName = "output/initialSynapseWeights.pkl"
elif (numberArgs == 3):
    inputFileName = args[1]
    synapseFileName = args[2]
    fInitWithStoredSynapses = True
#Standard way to call during training.
#Call with input, inputSyn, outputSyn
elif (numberArgs == 5):
    #maybe I can do something better here, but
    runMode = int(args[1])
    inputFileName = args[2]
    synapseFileName = args[3]
    outputSynapseFileName = args[4]
    if (runMode == 1):
        print("test run no synaptic change")
        plasticSynapses = False
        fInitWithStoredSynapses = True
        useOldAdaptationValues = False
    elif (runMode == 2):
        print("unspecified error run")
    elif (runMode == 3):
        print("STDP run")
        plasticSynapses = True
        fInitWithStoredSynapses = True
    elif (runMode == 4):
        print("init synapses with STDP")
        plasticSynapses = True
        fInitWithStoredSynapses = False
        useOldAdaptationValues = False
    elif (runMode == 5):
        print("init synapses run")
        plasticSynapses = False
        fInitWithStoredSynapses = False
        useOldAdaptationValues = True
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
if (useOldAdaptationValues):
    setAdaptationValues(categoryCells,"output/adaptationValues.w")
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
setupAdaptiveRecording(categoryCells)
setupRecording(inhibLayerCells)

duration = (numberInputs+1)*EPOCH_LENGTH
print ("start", len(initialSynapseWeights))
sim.run(duration)

printResults(inputCells,"output/input")
printResults(categoryCells,"output/category")
printResults(inhibLayerCells,"output/inhib")

#storeAdaptation(categoryCells,"output/adaptation.pkl")
storeFinalAdaptation(categoryCells,"output/adaptationValues.w")

if (plasticSynapses):
    finalSynapseWeights = inputToCategorySynapses.get(["weight"],format="list")
    saveSynapses(finalSynapseWeights,outputSynapseFileName)

#printPlasticSynapticPairWeights(initialSynapseWeights,finalSynapseWeights)
else: #original weights
    finalSynapseWeights = inputToCategorySynapses.get(["weight"],format="list")
    saveSynapses(finalSynapseWeights,outputSynapseFileName)


