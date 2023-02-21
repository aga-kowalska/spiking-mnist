synapseFileName="output/sTDPSynapses10.pkl"
trainDataFileName="data/dataSet1-1.csv"
testDataFilePrefix="data/dataSet2-"
categoryFilePrefix="output/category"
resultFileName="output/category.pkl"
resultSpikeFileName="output/category.sp"
categoryFilePrefix="output/category"
catWinnersFilePrefix="output/test1-"
translationPairFileName="output/translate1.pairs"
testDataFileName=$testDataFilePrefix"1.csv"

echo "Pairing category neurons with categories"
python3 mnist6.py "1" $trainDataFileName $synapseFileName "ign.pkl" 
python3 printPklSpikes.py $resultFileName > $resultSpikeFileName
python3 selectCategoryForNeuron.py $trainDataFileName $resultSpikeFileName > $translationPairFileName


for tenth in {1..10}
do
    testDataFileName=$testDataFilePrefix$tenth".csv"
    python3 mnist6.py "1" $testDataFileName $synapseFileName "ign.pkl" 
    python3 printPklSpikes.py $resultFileName > $resultSpikeFileName

    catWinnersFileName=$catWinnersFilePrefix$tenth".cats"
    python3 labelCategoryNeurons.py $testDataFileName $resultSpikeFileName > $catWinnersFileName
    python3 evalMnist5.py $translationPairFileName $catWinnersFileName
    
done


    
	     


