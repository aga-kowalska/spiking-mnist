import sys



#catTranslate = [[0,1], [1,1], [2,1], [3,1], [4,1],[5,1], [6,1], [7,8], [8,1], [9,1],[10,1],[11,1],[12,1],[13,1],[14,6],[15,1],[16,1],[17,0],[18,4],[19,9]]

def getCorrectResults(catTranslate,catResults):
    correct = 0;
    for oneResult in catResults:
        correctAnswer = oneResult[0]
        catNeuron = oneResult[1]
        translatePair = catTranslate[catNeuron]
        systemAnswer = translatePair[1]
        if (systemAnswer == correctAnswer):
            correct += 1
    return correct

def translateListString(input):
    answerList = []

    #Trim off the first [, and the last] with the eol
    input = input[1:len(input)-2]

    args = input.split(',')

    numberPairs = len(args)/2
    numberPairs = int(numberPairs)
    print (numberPairs)
    for offset in range (0,numberPairs):
        
        answerString = args[offset*2]
        answerString = answerString.strip()
        answerString = answerString[1:len(answerString)] #remove the [
        answerString = answerString.strip()
        answer = int(answerString)
        
        neuronString = args[(offset*2)+1]
        neuronString = neuronString[0:len(neuronString) -1] #temove the]
        neuronString = neuronString.strip()
        neuron = int (neuronString)
        #print (answerString,neuronString)
        pair = [answer,neuron]
        answerList = answerList+[pair]
                                    

    #print (answerList)
    return answerList

def readCats(answerFileName):
    fileHandle = open(answerFileName,'r')
    input = fileHandle.readline()
    fileHandle.close()
    answerCats = translateListString(input)
    return answerCats

def readTranslationPairs(pairFileName):
    fileHandle = open(pairFileName,'r')
    input = fileHandle.readline()
    fileHandle.close()
    answerCats = translateListString(input)
    #print (answerCats)
    return answerCats


##--main---
args = sys.argv
numberArgs = args.__len__()
print (numberArgs,args)
if (numberArgs == 3):
    catNeuronToCatFileName = args[1]
    answerFileName = args[2]
else:
    print("need translationTableFile and answerFile")

catResults = readCats(answerFileName)
catTranslate = readTranslationPairs(catNeuronToCatFileName)

correct=getCorrectResults(catTranslate,catResults)
correct = correct *1.0 
print (len (catResults),correct, correct/len(catResults))

