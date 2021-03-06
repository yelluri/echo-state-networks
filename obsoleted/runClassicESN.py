#Run this script to run the experiment
#Steps to follow are:
# 1. Preprocessing of data
# 2. Give the data to the reservoir
# 3. Plot the performance (such as error rate/accuracy)

from reservoir import EchoStateNetwork as ESN, Tuner as tuner, ReservoirTopology as topology
from plotting import OutputPlot as outputPlot
import numpy as np
import os
from datetime import datetime
from sklearn import preprocessing as pp

# Read data from the file
data = np.loadtxt('MackeyGlass_t17.txt')

# Normalize the raw data
minMax = pp.MinMaxScaler((-1,1))
data = minMax.fit_transform(data)

#Training Input data - get 2000 points
nTraining = 3000
nTesting = 2000
inputTrainingData = np.hstack((np.ones((nTraining, 1)),data[:nTraining].reshape((nTraining, 1))))
outputTrainingData = data[1:nTraining+1].reshape((nTraining, 1))

#Testing Input and output data
testInputData = np.hstack((np.ones((nTesting, 1)),data[nTraining:nTraining+nTesting].reshape((nTesting, 1))))
testActualOutputData = data[nTraining+1:nTraining+nTesting+1].reshape((nTesting, 1))

# Tune the network
size = 256
initialTransient = 50
inputConnectivity = 0.8
reservoirConnectivity = 0.7
reservoirTopology = topology.RandomTopology(size=size, connectivity=reservoirConnectivity)


res = ESN.EchoStateNetwork(size=size,
                               inputData=inputTrainingData,
                               outputData=outputTrainingData,
                               reservoirTopology=reservoirTopology,
                               spectralRadius=0.67,
                               inputScaling=0.87,
                               reservoirScaling=0.44,
                               leakingRate=0.9,
                               initialTransient=initialTransient,
                               inputConnectivity=inputConnectivity)
res.trainReservoir()


#Warm up
predictedTrainingOutputData = res.predict(inputTrainingData)


#Predict future values
predictedTestOutputData = []
lastAvailableData = testInputData[0,1]
for i in range(nTesting):
    query = [1.0]
    query.append(lastAvailableData)

    #Predict the next point
    nextPoint = res.predict(np.array(query).reshape((1,2)))[0,0]
    predictedTestOutputData.append(nextPoint)

    lastAvailableData = nextPoint

predictedTestOutputData = np.array(predictedTestOutputData).reshape((nTesting, 1))

#Plotting of the prediction output and error
outputFolderName = "Outputs/Outputs" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
os.mkdir(outputFolderName)
outplot = outputPlot.OutputPlot(outputFolderName + "/Prediction.html", "Mackey-Glass Time Series", "Prediction of future values", "Time", "Output")
outplot.setXSeries(np.arange(1, nTesting + 1))
outplot.setYSeries('Actual Output', minMax.inverse_transform(testActualOutputData[:nTesting, 0]))
outplot.setYSeries('Predicted Output', minMax.inverse_transform(predictedTestOutputData[:nTesting, 0]))
outplot.createOutput()
print("Done!")