synapseFileName="output/testC1.pkl"
dataFilePrefix="data/dataSet2-"
categoryFilePrefix="output/category"
resultFileName="output/category.pkl"
resultSpikeFileName="output/category.sp"
categoryFilePrefix="output/category"
catWinnersFilePrefix="output/test1-"
translationPairFileName="output/translate1.pairs"
dataFileName=$dataFilePrefix"1.csv"
trainDataFileName="data/dataSet1-1.csv"

echo "Pairing category neurons with categories"
python3 mnist5.py "1" $trainDataFileName $synapseFileName "ign.pkl" 
python3 printPklSpikes.py $resultFileName > $resultSpikeFileName
python3 selectCategoryForNeuron.py $trainDataFileName $resultSpikeFileName > $translationPairFileName


for tenth in {1..10}
do
    dataFileName=$dataFilePrefix$tenth".csv"
    python3 mnist5.py "1" $dataFileName $synapseFileName "ign.pkl" 
    python3 printPklSpikes.py $resultFileName > $resultSpikeFileName

    catWinnersFileName=$catWinnersFilePrefix$tenth".cats"
    python3 labelCategoryNeurons.py $dataFileName $resultSpikeFileName > $catWinnersFileName
    python3 evalMnist5.py $translationPairFileName $catWinnersFileName
    
done


    
	     


