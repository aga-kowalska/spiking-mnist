inputFilePrefix="data/dataSet1-"
initSynapseFileName="output/initSynapses.pkl"
initOutputFileName="output/initTemp"
synapseFilePrefix="output/firstTenthSynapses"

compensatoryFilePrefix="output/tempCompense"
outputRunFilePrefix="output/trainDump"
outputOffset=1
compensatoryOffset=1
result="compensatory change made"

sTDPFilePrefix="output/sTDPSynapses"

#First train, initialize new synapses and run one compense
python3 mnist5.py 4 $inputFile "output/ignore.pkl" $initSynapseFileName > $initOutputFileName

lastLine=$(tail -1 $initOutputFileName)
currentSynapseFileName=$initSynapseFileName
echo $lastLine
outputSynapseFileName=$compensatoryFilePrefix$compensatoryOffset".pkl"
echo "bob"
echo $outputSynapseFileName
echo $initSynapseFileName

for tenth in {1..10}
do 
    inputFile=$inputFilePrefix$tenth".csv"
    #loop until there is no compensatory change
    while [ "$lastLine" == "$result" ]
    do
	outputSynapseFileName=$compensatoryFilePrefix$compensatoryOffset".pkl"
	echo "fred"
	echo $currentSynapseFileName
	echo $outputSynapseFileName
	echo "$lastLine" == "$result"

	outputRunFile=$outputRunFilePrefix$outputOffset
	echo $outputRunFile

	python3 mnist5.py 2 $inputFile $currentSynapseFileName $outputSynapseFileName > $outputRunFile


	lastLine=$(tail -1 $outputRunFile)
	echo $lastLine

	currentSynapseFileName=$outputSynapseFileName
	outputOffset=$(( $outputOffset+1 ))
	compensatoryOffset=$(( $compensatoryOffset+1 ))
    
    done #while compensatory

    #try a run with STPD
    sTDPFileName=$sTDPFilePrefix$tenth".pkl"
    python3 mnist5.py 3 $inputFile $outputSynapseFileName $sTDPFileName

    #get ready for next compensatory run
    cp $sTDPFileName $compensatoryFilePrefix$compensatoryOffset".pkl"
    lastLine=$result #try compensatory
    echo "george"
    echo $lastLine
    
done #for each training tenth


    
	     


