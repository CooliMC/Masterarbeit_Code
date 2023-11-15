from copy import copy
from typing import Self

from simulation.Drone import Drone
from simulation.Order import Order

from model.Depot import Depot
from model.Building import Building
from model.ChargingStation import ChargingStation

from .ExitCode import ExitCode

class Solution():
    # Constructor the order with a given arguemnts
    def __init__(self, droneList: list[Drone], depot: Depot, chargingStationList: list[ChargingStation], orderList: list[Order]):
        # Save the list of drones
        self.droneList = droneList

        # Save the depot
        self.depot = depot

        # Save the list of charging stations
        self.chargingStationList = chargingStationList

        # Save the list of orders
        self.orderList = orderList

        # Merged building list of depot, charging stations and order destinations for distance precalculation
        self.buildingList = [depot] + chargingStationList + [order.getDestination() for order in orderList]

        # Precalculate the distance matrix between the different buildings 
        self.distanceMatrix = Solution.CalculateDistanceMatrix(self.buildingList)
        
        # Create and prefilled solution matrix with the drones as key and value list of orders
        self.solutionMatrix = dict(map(lambda drone: (drone, [Order(depot)]), self.droneList))

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
    
    def getBuildingList(self) -> list[Building]:
        # Return the buildingList
        return self.buildingList
    
    def getDistanceMatrix(self) -> dict[Building, dict[Building, float]]:
        # Return the distanceMatrix
        return self.distanceMatrix
    
    def getSolutionMatrix(self) -> dict[Drone, list[Order]]:
        # Return the solutionMatrix
        self.solutionMatrix

    ################################################################################
    ############################### SCORE FUNCTIONS ################################
    ################################################################################

    def getTimeScore(self) -> float:
        return sum()
        # Calculate the score of the by the time with a formular like this:
        # sum(time of each drone) * (1 + (longestDroneTime - shortestDroneTime))

    ################################################################################
    ############################ NEIGHBORHOOD FUNCTIONS ############################
    ################################################################################

    def getTwoOptSolutions(self, drone: Drone, maximumLengthDelta: float = 0) -> list[Self]:
        # Resolve the tour (length) and range of the given drone
        orderTour = self.getDroneTour(drone, False)
        tourLength = self.getTourDistance(orderTour)
        droneRange = drone.getRemainingFlightDistance()

        # Create an empty solution list for the two-opt
        twoOptSolutionList = []

        # Loop over the tour of the drone for potential edges
        for outerTourIndex in range(0, len(orderTour) - 2, 1):
            # Loop over the rest of the tours after this to check for potential swaps
            for innerTourIndex in range(outerTourIndex + 1, len(orderTour) -1, 1):
                # Use a dedicated function to calculate the path delta for the two-opt
                lengthDelta = self.calculateTwoOptPathLengthDelta(
                    (orderTour[outerTourIndex], orderTour[outerTourIndex + 1]), 
                    (orderTour[innerTourIndex], orderTour[innerTourIndex + 1])
                )

                # Check if the lengthDelta is smaller then the upper boundary
                if (lengthDelta <= maximumLengthDelta):
                    # Create the two-opt solution by changing the given paths
                    twoOptSolutionList.append(self.createTwoOptSolution(
                        drone, outerTourIndex, innerTourIndex, orderTour))
                    
                    # Calculate the new tour length with the delta
                    twoOptTourLength = tourLength + lengthDelta

                    

                    # TODO: Calc new length with delta, calc charging stops and add them

        # Return the two-opt solution list
        return twoOptSolutionList

    def getRelocateSolutions(self, order: Order) -> list[Self]:
        # Resolve the drone of the given order
        orderDrone = self.getDroneByOrder(order)

        # Create an empty solution list for the relocates
        relocateSolutionList = []

        # Loop through the list of drones
        for partnerDrone in self.droneList:
            # Check if the relocate partner is the same drone and continue
            if (partnerDrone == orderDrone): continue

            # Resolve the tour of the partner drone without recharges
            partnerTour = self.getDroneTour(partnerDrone, False)

            # Loop over the tour of the partner drone for relocates
            for partnerTourIndex in range(0, len(partnerTour) -1, 1):
                1

            # TODO: Implement the shift

        # Return the relocateSolutionList
        return relocateSolutionList

    def getExchangeSolutions(self, orderIndex: int) -> list[Self]:
        # Resolve the order form the list of orders to compare
        currentOrder = self.orderList[orderIndex]

        # Create an empty solution list for the swaps
        exchangeSolutionList = []

        # Loop through all orders to search for swap partners
        for swapPartnerOrder in self.orderList:
            # Check if the swap partner is the current order and continue

            if (swapPartnerOrder == currentOrder): continue

            # TODO: Implement the swap

        # Return the exchangeSolutionList
        return exchangeSolutionList

    def getCrossSolutions(self, orderIndex: int) -> list[Self]:
        return []
    
    ################################################################################
    ############################### Two-Opt FUNCTIONS ##############################
    ################################################################################

    def calculateTwoOptPathLengthDelta(self, firstPath: tuple[Order, Order], secondPath: tuple[Order, Order]) -> float:
        # Use the precalculation to get the path delta for two-opt swap
        return (
            self.getOrderDistance(firstPath[0], secondPath[0])
            + self.getOrderDistance(firstPath[1], secondPath[1])
            - self.getOrderDistance(firstPath[0], firstPath[1])
            - self.getOrderDistance(secondPath[0], secondPath[1])
        )
    
    def createTwoOptSolution(self, drone: Drone, firstPathIndex: int, secondPathIndex: int, droneTour: list[Order] = None) -> Self:
        # Check if the droneTour parameter is set or resolve it
        if droneTour is None: droneTour = self.getDroneTour(drone)

        # Reconstruct the droneTour by performing the two-opt swap with the pathIndex
        droneTour = droneTour[:(firstPathIndex + 1)] + droneTour[
            secondPathIndex:firstPathIndex:-1] + droneTour[(secondPathIndex + 1):]

        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy(True)

        # Update the orderList of the drone with the droneTour
        solutionCopy.solutionMatrix[drone] = droneTour

        # Return the modified solution copy
        return solutionCopy

    ################################################################################
    ############################### SUPPORT FUNCTIONS ##############################
    ################################################################################

    def getSolutionCopy(self) -> Self:
        # Use the built-in function to copy the solution
        solutionCopy = copy(self)

        # Create a shallow copy of the solution matrix with dict function
        solutionCopy.solutionMatrix = dict(solutionCopy.solutionMatrix)

        # Loop over the shallow copy of the solution matrix
        for drone, orderList in solutionCopy.solutionMatrix:
            # Create a shallow copy of the orderList with the list function
            solutionCopy.solutionMatrix[drone] = list(orderList)

        # Return the solution copy
        return solutionCopy

    def getOrderDistance(self, sourceOrder: Order, destinationOrder: Order) -> float:
        # Use the precalculated distanceMatrix to get the distance between the orders
        return self.distanceMatrix[sourceOrder.getDestination()][destinationOrder.getDestination()]

    def getDroneByOrder(self, order: Order) -> Drone:
        # Use the built-in function to get the drone that has the given order in its orderList
        return next((drone for drone, orderList in self.solutionMatrix.items() if order in orderList), None)

    def getDroneTour(self, drone: Drone, includeChargingOrders: bool = True) -> list[Order]:
        # Check if the drone tour list should include the charging orders (default)
        if includeChargingOrders: return self.solutionMatrix[drone]

        # Use the built in filter function to check if the order destination is no charging station
        return [droneOrder for droneOrder in self.solutionMatrix[drone] 
                if droneOrder.getDestination() not in self.chargingStationList]
    
    def getDroneTourDistance(self, drone: Drone, includeChargingOrders: bool = True) -> float:
        # Use the getDroneTour and getTourDistance function to get the drone tour distance
        return self.getTourDistance(self.getDroneTour(drone, includeChargingOrders))

    def getTourDistance(self, tour: list[Order]) -> float:
        # Initialize the tour distance
        tourDistance = 0

        # Loop over the tour in stepped pairs
        for index in range(0, len(tour) - 1, 1):
            # Calculate and add the distance between the current and next order
            tourDistance += self.getOrderDistance(tour[index], tour[index + 1])

        # Return the summed up destinations
        return tourDistance

    ################################################################################
    ############################### SUPPORT FUNCTIONS ##############################
    ################################################################################

    @staticmethod
    def CalculateDistanceMatrix(buildingList: list[Building]) -> dict[Building, dict[Building, float]]:
        # Use built-in python functions to convert the the buildingList into a 2D dictionary with the Building as the keys and distance as the value
        distanceMatrix = dict([(outerBuilding, dict([(innerBuilding, 0) for innerBuilding in buildingList])) for outerBuilding in buildingList])

        # Loop through the complete building list once
        for outerIndex in range(0, len(buildingList), 1):
            # Resolve the outerBuilding from the buildingList
            outerBuilding = buildingList[outerIndex]

            # Loop through all building after the outer index in the list
            for innerIndex in range(outerIndex + 1, len(buildingList), 1):
                # Resolve the innerBuilding from the buildingList
                innerBuilding = buildingList[innerIndex]

                # Calculate the distance between the buildings for the matrix
                calculatedDistance = innerBuilding.getDistanceTo(outerBuilding)

                # Set the calculated distance for both buillding combinations
                distanceMatrix[innerBuilding][outerBuilding] = calculatedDistance
                distanceMatrix[outerBuilding][innerBuilding] = calculatedDistance

        # Return the distance matrix
        return distanceMatrix