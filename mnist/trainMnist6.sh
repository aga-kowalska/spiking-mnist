inputFilePrefix="data/dataSet1-"
initOutputFileName="output/initTemp"
synapseFilePrefix="output/firstTenthSynapses"

outputRunFilePrefix="output/trainDump"
outputOffset=1

sTDPFilePrefix="output/sTDPSynapses"

inputFile=$inputFilePrefix"1.csv"
initSynapseFileName=$sTDPFilePrefix"1.pkl"

#First train, initialize new synapses and run one compense
python3 mnist6.py 4 $inputFile "output/ignore.pkl" $initSynapseFileName 

currentSynapseFileName=$initSynapseFileName
echo "bob"

for tenth in {2..10}
do 
    inputFile=$inputFilePrefix$tenth".csv"
    outputSynapseFileName=$sTDPFilePrefix$tenth".pkl"
    python3 mnist6.py 3 $inputFile $currentSynapseFileName $outputSynapseFileName
    currentSynapseFileName=$outputSynapseFileName
    
done #for each training tenth


    
	     


