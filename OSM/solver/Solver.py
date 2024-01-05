import math
import random

from collections import deque

from simulation.Drone import Drone
from simulation.Order import Order

from model.Depot import Depot
from model.Building import Building
from model.ChargingStation import ChargingStation

from .ExitCode import ExitCode
from .Solution import Solution

class Solver():
    # Define constants for the solver class
    FLOAT_POSITIVE_INFINITY = float('+inf')
    FLOAT_NEGATIVE_INFINITY = float('-inf')

    # Constructor the solver with given arguemnts
    def __init__(self, droneList: list[Drone], depot: Depot, chargingStationList: list[ChargingStation], orderList: list[Order]):
        # Save the list of drones
        self.droneList = droneList

        # Save the depot
        self.depot = depot

        # Save the list of charging stations
        self.chargingStationList = chargingStationList

        # Save the list of orders
        self.orderList = orderList

    ################################################################################
    ############################### GETTER FUNCTIONS ###############################
    ################################################################################

    def getDroneList(self) -> list[Drone]:
        # Return the droneList
        return self.droneList
    
    def getDepot(self) -> Depot:
        # Return the depot
        return self.depot
    
    def getChargingStationList(self) -> list[ChargingStation]:
        # Return the chargingStationList
        return self.chargingStationList

    def getOrderList(self) -> list[Order]:
        # Return the districtList
        return self.orderList

    ################################################################################
    ############################### SOLVER FUNCTIONS ###############################
    ################################################################################

    def getInitialOrder(self):
        return None

    def getNextOrder(self, drone: Drone) -> Order:
        return None
    
    def getInitialSolution(self, allowRecharge: bool = True) -> Solution|None:
        # Create solution with the given parameters from the solver class to hold the final solution
        solution = Solution(self.droneList, self.depot, self.chargingStationList, self.orderList)

        # Call the internal generateInitialSolution function with the solution and save the error code
        errorCode = Solver.GenerateInitialSolution(self.droneList, self.orderList, solution, allowRecharge)

        # Check the error code for no success and overwrite the solution
        if (errorCode != ExitCode.SUCCESS): solution = None

        # Return the solution
        return solution
    
    def getStageTwoSolution(self, initialSolution: Solution, allowRecharge: bool = True) -> Solution:
        return None
    
    ################################################################################
    ########################## IMPROVEMENT METHOD FUNCTIONS ########################
    ################################################################################

    def performRandomWalk(self, currentSolution: Solution, maxIterationsOverall: int, maxIterationsWithoutImprovement: int) -> Solution:
        # Set the current solution as the best solution
        bestSolution = currentSolution
        
        # Initialize the RandomWalk algorithm parameters
        iterationsWithoutImprovement = 0
        currentIteration = 0

        # Run the algorithm until the termination criteria are fulfilled
        while True:
            # Increase the algorithm counter
            iterationsWithoutImprovement += 1
            currentIteration += 1
            
            # Check if the number of iterations exceeds the limit
            if currentIteration > maxIterationsOverall: break

            # Check if the number of iterations withouth improvements exceedes the limit
            if iterationsWithoutImprovement > maxIterationsWithoutImprovement: break

            # Randomly select a neighborhood solution from the current solutions neighborhood list
            neighborhoodSolution = random.choice(currentSolution.getNeighborhoodSolutions())

            # Check if the neighborhood solution has better time score the the best solution 
            if (neighborhoodSolution.getTimeScore() < bestSolution.getTimeScore()):
                # Replace the best solution with the neighborhood solution
                bestSolution = neighborhoodSolution

                # Reset the iterationsWithoutImprovement counter
                iterationsWithoutImprovement = 0

            # Replace the current solution with the neighborhood solution
            currentSolution = neighborhoodSolution

        # Return the best solution
        return bestSolution
    
    def performThresholdAccepting(self, currentSolution: Solution, alphaFactor: float = 0.75, sizeFactor: int = 2, minimumThreshold: float = 15, initialThreshold: float = 3600) -> Solution:
        # Set the current solution as the best solution
        bestSolution = currentSolution

        # Initialize the ThresholdAccepting algorithm parameters
        maxIterations = sizeFactor * len(currentSolution.getOrderList())
        threshold = initialThreshold
        currentIteration = 0

        # Run the algorithm until the termination criteria are fulfilled
        while True:
            # Increase the algorithm counter
            currentIteration += 1

            # Select the best neighborhood solution from the current solutions neighborhood list
            neighborhoodSolution = min(currentSolution.getNeighborhoodSolutions(), key=lambda x: x.getTimeScore())
            
            # Check if the neighborhood solution has better time score the the best solution 
            if (neighborhoodSolution.getTimeScore() < bestSolution.getTimeScore()):
                # Replace the best solution with the neighborhood solution
                bestSolution = neighborhoodSolution
            
            # Check if the delta between neighborhood and current solution time score is lower then the threshold
            if (neighborhoodSolution.getTimeScore() - currentSolution.getTimeScore()) < threshold:
                # Replace the current solution with the neighborhood solution
                currentSolution = neighborhoodSolution

            # Check if the threshold exceeds the limit and the neighborhood solution is worse then the current solution
            if threshold < minimumThreshold and currentSolution.getTimeScore() <= neighborhoodSolution.getTimeScore(): break

            # Check if the number of iterations exceeds the limit
            if currentIteration > maxIterations:
                # Reset the iterations counter
                currentIteration = 0

                # Recalculate the threshold
                threshold *= alphaFactor

        # Return the best solution
        return bestSolution

    def performSimulatedAnnealing(self, currentSolution: Solution, alphaFactor: float = 0.95, betaFactor: float = 1.15, sizeFactor: int = 16, initialAcceptanceRate: float = 30.0, frozenAcceptanceFraction: float = 0.1, frozenParameter: int = 5) -> Solution:
        # Set the current solution as the best solution
        bestSolution = currentSolution

        # Initialize the SimulatedAnnealing algorithm parameters
        maxIterations = sizeFactor * len(currentSolution.getOrderList())
        temperature = initialAcceptanceRate
        currentIteration = 0

        # Run the algorithm until the termination criteria are fulfilled
        while True:
            # Increase the algorithm counter
            currentIteration += 1

            # Check if the temperature exceeds the frozenAcceptanceFraction and the current iteration the frozenParameter
            if temperature < frozenAcceptanceFraction and currentIteration > frozenParameter: break

            # Randomly select a neighborhood solution from the current solutions neighborhood list
            neighborhoodSolution = random.choice(currentSolution.getNeighborhoodSolutions())

            # Check if the neighborhood solution has better time score the the best solution 
            if (neighborhoodSolution.getTimeScore() < bestSolution.getTimeScore()):
                # Replace the best solution with the neighborhood solution
                bestSolution = neighborhoodSolution

            # Check if the neighborhood solution has better time score the the current solution 
            if (neighborhoodSolution.getTimeScore() < currentSolution.getTimeScore()):
                # Replace the current solution with the neighborhood solution
                currentSolution = neighborhoodSolution
            
            # Check if the acceptance probability is greater then a random uniform number
            elif random.uniform(0, 1) < math.exp((currentSolution.getTimeScore() - neighborhoodSolution.getTimeScore()) / temperature):
                currentSolution = neighborhoodSolution

            # Check if the number of iterations exceeds the limit
            if currentIteration > maxIterations:
                # Recalculate the maxIterations
                maxIterations *= betaFactor

                # Recalculate the temperature
                temperature *= alphaFactor

        # Return the best solution
        return bestSolution
    
    def performReactiveTabuSearch(self, currentSolution: Solution, initialTabuListLength: int = 10, minTabuListLength: int = 5, maxTabuListLength: int = 5000, deltaOne: float = 1.2, deltaTwo: float = 2, maxIterationsOverall: int = 5000, maxIterationsWithoutImprovement: int = 5000, iterationsForListShortening: int = 10) -> Solution:
        # Set the current solution as the best solution
        bestSolution = currentSolution

        # Initialize the ReactiveTabuSearch algorithm parameters
        tabuList = deque([currentSolution], initialTabuListLength)
        longTermMemory = set([currentSolution])
        iterationsWithoutRepetition = 0
        iterationsWithoutImprovement = 0
        currentIteration = 0

        # Run the algorithm until the termination criteria are fulfilled
        while True:
            # Increase the algorithm counter
            iterationsWithoutImprovement += 1
            currentIteration += 1

            # Check if the number of iterations exceeds the limit
            if currentIteration > maxIterationsOverall: break

            # Check if the number of iterations withouth improvements exceedes the limit
            if iterationsWithoutImprovement > maxIterationsWithoutImprovement: break
            
            # Resolve all neighborhood solutions of the current solution
            neighborhoodSolutionList = currentSolution.getNeighborhoodSolutions()

            # Inizialize the NeighborhoodSearch parameters
            bestNotAllowedNeighborhoodSolution = None
            bestAllowedNeighborhoodSolution = None
            foundAlreadySeenSolution = 0

            # Loop over the neighborhoodSolutionList to check each entry
            for neighborhoodSolution in neighborhoodSolutionList:
                # Create a TabuKey for the neighborhoodSolution
                neighborhoodSolutionKey = TabuKey(neighborhoodSolution)

                # Check neighborhoodSolutionKey against the longTermMemory
                if neighborhoodSolutionKey in longTermMemory:
                    # Increase the foundAlreadySeenSolution
                    foundAlreadySeenSolution += 1

                # Check if the neighborhoodSolution is not blocked
                if neighborhoodSolutionKey not in tabuList:
                    # Check if the bestAllowedNeighborhoodSolution is set
                    if bestAllowedNeighborhoodSolution is not None:
                        # Check the score of the neighborhoodSolution against the bestAllowedNeighborhoodSolution
                        if neighborhoodSolution.getTimeScore() < bestAllowedNeighborhoodSolution.getTimeScore():
                            # Set the neighborhoodSolution as the bestAllowedNeighborhoodSolution
                            bestAllowedNeighborhoodSolution = neighborhoodSolution

                    # Set the neighborhoodSolution as the bestAllowedNeighborhoodSolution
                    else: bestAllowedNeighborhoodSolution = neighborhoodSolution


                # Check if the bestNotAllowedNeighborhoodSolution is set
                elif bestNotAllowedNeighborhoodSolution is not None:
                    # Check the score of the neighborhoodSolution against the bestNotAllowedNeighborhoodSolution
                    if neighborhoodSolution.getTimeScore() < bestNotAllowedNeighborhoodSolution.getTimeScore():
                        # Set the neighborhoodSolution as the bestNotAllowedNeighborhoodSolution
                        bestNotAllowedNeighborhoodSolution = neighborhoodSolution
                
                # Set the neighborhoodSolution as the bestNotAllowedNeighborhoodSolution
                else: bestNotAllowedNeighborhoodSolution = neighborhoodSolution

            # Get the best neighborhood solution that is allowed, otherwise the best not allowed one
            currentSolution = bestAllowedNeighborhoodSolution or bestNotAllowedNeighborhoodSolution

            # Blocke Best Moves
            currentSolutionTabuKey = TabuKey(currentSolution)

            # Check if there were already seen solutions
            if foundAlreadySeenSolution > 0:
                # Hint: Increase tabu list length because we saw an already seen solution
                # Resolve the current max tabu list length (with fallback if None)
                targetTabuListLength = tabuList.maxlen or len(tabuList)

                # Check if the targetTabuListLength is smaller then the maxTabuListLength
                if targetTabuListLength < maxTabuListLength:
                    # Use the reactive tabu search deltas to calculate the new targetTabuListLength
                    targetTabuListLength = math.ceil(max(targetTabuListLength * deltaOne, targetTabuListLength + deltaTwo))

                    # Check if the targetTabuListLength exceeds the maxTabuListLength
                    targetTabuListLength = min(targetTabuListLength, maxTabuListLength)

                    # Replace the tabuList to increase the max list length
                    tabuList = deque(tabuList, targetTabuListLength)

                # Reset the iterationsWithoutRepetition counter 
                iterationsWithoutRepetition = 0

            # Check if there were enought iterations without repetitions
            elif iterationsWithoutRepetition >= iterationsForListShortening:
                # Hint: Decrease tabu list because we did not see some already seen solutions for a while
                # Resolve the current max tabu list length (with fallback if None)
                targetTabuListLength = tabuList.maxlen or len(tabuList)

                 # Check if the targetTabuListLength is greater then the minTabuListLength
                if targetTabuListLength > minTabuListLength:
                    # Use the reactive tabu search deltas to calculate the new targetTabuListLength
                    targetTabuListLength = math.ceil(max(targetTabuListLength / deltaOne, targetTabuListLength - deltaTwo))

                    # Check if the targetTabuListLength subceed the minTabuListLength
                    targetTabuListLength = max(targetTabuListLength, minTabuListLength)

                    # Replace the tabuList to decrease the max list length
                    tabuList = deque(tabuList, targetTabuListLength)

                # Reset the iterationsWithoutRepetition counter 
                iterationsWithoutRepetition = 0

            # Increase the iterationsWithoutRepetition counter 
            else: iterationsWithoutRepetition += 1

            # Add the currentSolutionTabuKey to the tabuList
            tabuList.append(currentSolutionTabuKey)

            # Add the currentSolutionTabuKey to the longTermMemory
            longTermMemory.add(currentSolutionTabuKey)

            # Check if the current solution solution has better time score the the best solution 
            if (currentSolution.getTimeScore() < bestSolution.getTimeScore()):
                # Replace the best solution with the current solution
                bestSolution = currentSolution

                # Reset the iterationsWithoutImprovement counter
                iterationsWithoutImprovement = 0
                
        # Return the best solution
        return bestSolution

    ################################################################################
    ############################ STATIC SOLVER FUNCTIONS ###########################
    ################################################################################

    @staticmethod
    def GenerateInitialSolution(droneList: list[Drone], orderList: list[Order], solution: Solution, allowRecharge: bool = True, orderIndex: int = 0, orderMilageCache: dict[Order, float] = dict()) -> ExitCode:
         #Resolve the solution matrix for easier access
        solutionMatrix = solution.getSolutionMatrix()
        
        # Check if all orders are assigned to a drone
        if (orderIndex == len(orderList)):
            # Try to close the route by inserting the return-to-start (depot) order
            for drone in droneList:
                # Close the route by inserting the return-to-start (depot) order
                currentOrder = Order(solutionMatrix[drone][0].getDestination(), 0, 0)

                # Resolve the milage of the current drones last order if available
                lastDroneMilage = orderMilageCache.get(solutionMatrix[drone][-1], 0)
                
                # Resolve the distance between the last and current order from the precalculated solution
                lastToCurrentOrderDistance = solution.getOrderDistance(solutionMatrix[drone][-1], currentOrder)

                # Calculate the drone milage after the current order for constraint checks
                currentDroneMilage = lastDroneMilage + lastToCurrentOrderDistance

                # Constraint: Remaining range of the drone to reach the desired target
                if (currentDroneMilage > drone.getRemainingFlightDistance()):
                    # Get the closest charging station for the drone by its last order in the list
                    targetChargingStation = solution.getClosestChargingStation(solutionMatrix[drone][-1])
                    
                    # Create a charging order for the current drone
                    chargingOrder = Order(targetChargingStation, 0, 900)

                    # Add the charging station as next order of the drone
                    solutionMatrix[drone].append(chargingOrder)

                    # Reset the order milage cache to zero
                    orderMilageCache[chargingOrder] = 0

                # Drone has enough capacity add the current order
                solutionMatrix[drone].append(currentOrder)

                # Update the order milage cache for the current order
                orderMilageCache[currentOrder] = currentDroneMilage

            # Return exit code for success
            return ExitCode.SUCCESS
        
        # Define the constraint failure level exit code
        constrainFailureLevel = ExitCode.NO_SOLUTION

        # Resolve the current order by the index
        currentOrder = orderList[orderIndex]

        # Loop over the sorted list of drones to check the drones from the closest to farest one
        for drone in sorted(droneList, key=lambda x: solution.getOrderDistance(solutionMatrix[x][-1], currentOrder)):
            # Resolve the milage of the current drones last order if available
            lastDroneMilage = orderMilageCache.get(solutionMatrix[drone][-1], 0)
            
            # Resolve the distance between the last and current order from the precalculated solution
            lastToCurrentOrderDistance = solution.getOrderDistance(solutionMatrix[drone][-1], currentOrder)

            # Calculate the drone milage after the current order for constraint checks
            currentDroneMilage = lastDroneMilage + lastToCurrentOrderDistance

            # Constraint: Remaining range of the drone to reach the desired target
            if (currentDroneMilage > drone.getRemainingFlightDistance()):
                # Set the constrainFailureLevel exit code
                constrainFailureLevel = ExitCode.ORDER_NOT_IN_RANGE
                
                # Goto next drone
                continue

            # Calculate the remaining range of the drone after the current order 
            remainingDroneRange = drone.getRemainingFlightDistance() - currentDroneMilage

            # Constraint: Check if after the current order enough charge is left to reach a charging stations
            if not solution.isChargingStationInRange(currentOrder, remainingDroneRange):
                # Set the constrainFailureLevel exit code
                constrainFailureLevel = ExitCode.NO_CHARGING_STATION_IN_RANGE

                # Goto next drone
                continue
            
            # Drone has enough capacity add the current order
            solutionMatrix[drone].append(currentOrder)

            # Update the order milage cache for the current order
            orderMilageCache[currentOrder] = currentDroneMilage

            # Check the recursive alogrithms backtracking response code
            recursiveResponseCode = Solver.GenerateInitialSolution(
                droneList, orderList, solution, allowRecharge, orderIndex + 1, orderMilageCache)

            # Check if the order fails because no charging station in range
            if (allowRecharge and (recursiveResponseCode == ExitCode.NO_CHARGING_STATION_IN_RANGE)):
                # Order the drones to the closest charging station
                for subDrone in droneList:
                    # Get the closest charging station for the subDrone by its last order in the list
                    targetChargingStation = solution.getClosestChargingStation(solutionMatrix[subDrone][-1])
                    
                    # Create a charging order for the current subdrone
                    chargingOrder = Order(targetChargingStation, 0, 900)

                    # Add the charging station as next order of the subDrone
                    solutionMatrix[subDrone].append(chargingOrder)

                    # Reset the order milage cache to zero
                    orderMilageCache[chargingOrder] = 0
                
                # Check the recursive alogrithms backtracking response code
                recursiveResponseCode = Solver.GenerateInitialSolution(
                    droneList, orderList, solution, allowRecharge, orderIndex + 1, orderMilageCache)

                # Check if the recursive algorithm was no success
                if (recursiveResponseCode != ExitCode.SUCCESS):
                    # Remove the charging order from all drones
                    for subDrone in droneList:
                        # Remove the charging order of the drone (del from both dicts)
                        removedChargingOrder = solutionMatrix[drone].pop()
                        del orderMilageCache[removedChargingOrder]

            # Check if the recursive algorithm was a success to end it
            if (recursiveResponseCode == ExitCode.SUCCESS):
                # Return exit code for success
                return ExitCode.SUCCESS
            
            # Revert the changes of the current stage (del from both dicts)
            removedChargingOrder = solutionMatrix[drone].pop()
            del orderMilageCache[removedChargingOrder]

        # Return the last given constrainFailureLevel exit code
        return constrainFailureLevel
    
################################################################################
################################ SUPPORT CLASSES ###############################
################################################################################

class TabuKey():
    # Constructor the tabu key with given arguemnts
    def __init__(self, solution: Solution):
        # Save the drone list for equality checks
        self.droneList = solution.getDroneList()

        # Save the drone order dict as the unique parameter
        self.droneOrders = solution.getSolutionMatrix()

    ################################################################################
    ################################ CLASS FUNCTIONS ###############################
    ################################################################################

    def __eq__(self, other):
        # Check if the have the same reference
        if self is other: return True

        # Check if the are the same class instance
        if not isinstance(other, TabuKey): return False

        # Check if the drone orders are initialized in both tabu keys
        if self.droneOrders is None or other.droneOrders is None: return False

        # Check if the drone orders have the same reference
        if self.droneOrders is other.droneOrders: return True

        # Check if the drone orders have the same keys and key values
        if self.droneOrders == other.droneOrders: return True

        # Check if the length of the drone orders is equal
        if len(self.droneOrders) != len(other.droneOrders): return False

        # Check if the length of the drone list is equal
        if len(self.droneList) != len(other.droneList): return False

        # Loop through the list of drones to compare the 
        for drone in self.droneList:
            # Check if the drone orders are equal in size, content and order
            if self.droneOrders[drone] == other.droneOrders[drone]: continue
            
            # Check fi the drone orders have the same size before in depth comparison
            if len(self.droneOrders[drone]) != len(other.droneOrders[drone]): return False

            # Iterate over the list of the drone in both tabu keys by index
            for droneOrderIndex in range(len(self.droneOrders[drone])):
                # Check if the order id of the current drone order index is equal in this and the other tabu key
                if self.droneOrders[drone][droneOrderIndex].getId() != other.droneOrders[drone][droneOrderIndex].getId():
                    # Not equal so return False
                    return False

        # Default to True
        return True
    
    def __hash__(self):
        # Initialize the result hash
        resultHash = 1

        # Loop over the droneOrderDict for the drone and orderList
        for drone, orderList in self.droneOrders.items():
            # Iterate through the orderList of each drone
            for orderIndex in range(len(orderList)):
                # Calculate an orderHash with a magic number and the parameters
                orderHash = 31 * drone.getId() + (orderIndex + 1)
                orderHash = 31 * orderHash + orderList[orderIndex].getId()

                # Add the position based order hash to the result hash
                resultHash = (31 * resultHash + orderHash) % 4157396449

        # Return the result hash
        return resultHash