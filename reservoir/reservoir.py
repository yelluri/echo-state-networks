
import numpy as np
import scipy.linalg as la
import scipy.sparse.linalg as sla

class Reservoir:
    def __init__(self, size, spectralRadius, inputScaling, leakingRate, initialTransient, inputData, outputData):
        """

        :param Nx: size of the reservoir
        :param spectralRadius: spectral radius for reservoir weight matrix
        :param inputScaling: scaling for input weight matrix - the values are chosen from [-inputScaling, +inputScaling]
                                1 X D - For each parameter
        :param leakingRate: leaking rate of the reservoir
        :param data: input data (N X D)
        """
        self.Nx = size
        self.spectralRadius = spectralRadius
        self.inputScaling = inputScaling
        self.leakingRate = leakingRate
        self.initialTransient = initialTransient
        self.inputData = inputData
        self.outputData = outputData

        #Initialize weights
        self.inputN, self.inputD = self.inputData.shape
        self.outputN, self.outputD = self.outputData.shape
        self.Nu = self.inputD
        self.Ny = self.outputD
        self.inputWeight = np.zeros((self.Nx, self.Nu))
        self.reservoirWeight = np.zeros((self.Nx, self.Nx))
        self.outputWeight = np.zeros((self.Ny, self.Nx))

        #Generate the input and reservoir weights
        self.__generateInputWeight()
        self.__generateReservoirWeight()

        #Internal states
        self.internalState = np.zeros((self.inputN-self.initialTransient, self.Nx))


    def __generateInputWeight(self):
        #Choose a uniform distribution and adjust it according to the input scaling
        #ie. the values are chosen from [-inputScaling, +inputScaling]
        #TODO: Normalize ?
        self.inputWeight = np.random.rand(self.Nx, self.Nu)
        self.inputWeight = self.inputWeight - self.inputScaling


    def __generateReservoirWeight(self):
        #Choose a uniform distribution
        #TODO: Normalize ?
        self.reservoirWeight = np.random.rand(self.Nx, self.Nx)
        self.reservoirWeight = self.reservoirWeight - self.inputScaling

        # # simulate an Erdos Ryeni network by creating matrix of probabilities
        # # and use these probabilities to suppress weights in W
        # M = np.random.rand(self.Nx,self.Nx)
        # self.reservoirWeight[M>0.1] = 0.

        #Make the reservoir weight matrix - a unit spectral radius
        rad = np.max(np.abs(la.eigvals(self.reservoirWeight)))
        self.reservoirWeight = self.reservoirWeight / rad

        #Force spectral radius
        self.reservoirWeight = self.reservoirWeight * self.spectralRadius

    def trainReservoir(self):

        internalState = np.zeros(self.Nx)

        #Compute internal states of the reservoir
        for t in range(self.inputN):
            term1 = np.dot(self.inputWeight,self.inputData[t])
            term2 = np.dot(self.reservoirWeight,internalState)
            internalState = (1-self.leakingRate)*internalState + self.leakingRate*np.tanh(term1 + term2)
            if t >= self.initialTransient:
                self.internalState[t-self.initialTransient] = internalState

        #Learn the output weights
        A = self.internalState
        B = self.outputData[self.initialTransient:, :]

        #Solve for x in Ax = B
        self.outputWeight = sla.lsmr(A, B, damp=1e-8)[0]

    def predict(self, testInputData):

        testInputN, testInputD = testInputData.shape
        statesN, resD = self.internalState.shape
        internalState = self.internalState[statesN -1]

        testOutputData = []

        for t in range(testInputN):
            #reservoir activation
            term1 = np.dot(self.inputWeight,testInputData[t])
            term2 = np.dot(self.reservoirWeight,internalState)
            internalState = (1-self.leakingRate)*internalState + self.leakingRate*np.tanh(term1 + term2)

            #compute output
            output = np.dot(self.outputWeight, internalState)
            testOutputData.append(output)

        return testOutputData






