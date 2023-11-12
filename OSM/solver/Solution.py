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
        
        # Create and prefilled solution matrix with the drones as key and list of orders and distance
        self.solutionMatrix = dict(map(lambda drone: (drone, [(Order(depot), 0)]), self.droneList))

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
    
    def getSolutionMatrix(self) -> dict[Drone, list[tuple[Order, int]]]:
        # Return the solutionMatrix
        self.solutionMatrix

    ################################################################################
    ############################## SOLUTION FUNCTIONS ##############################
    ################################################################################

    def getTimeScore(self) -> float:
        return sum()
        # Calculate the score of the by the time with a formular like this:
        # sum(time of each drone) * (1 + (longestDroneTime - shortestDroneTime))

    def getTwoOptSolutions(self, drone: Drone) -> list[Self]:
        # Resolve the tour of the given drone
        orderTour = self.getDroneTour(drone)

        # TODO: Dont know how to do this? Normally 2Opt is implemented in the solver? How to get a better neighborhood?

        # Loop over the tour of the drone for potential edges
        for tourIndex in range(0, len(orderTour) -1, 1):
            1

        return 1

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
    ############################### SUPPORT FUNCTIONS ##############################
    ################################################################################

    def getOrderDistance(self, sourceOrder: Order, destinationOrder: Order) -> float:
        # Use the precalculated distanceMatrix to get the distance between the orders
        return self.distanceMatrix[sourceOrder.getDestination()][destinationOrder.getDestination()]

    def getDroneByOrder(self, order: Order) -> Drone:
        # Use the built-in function to get the drone that has given order in its orderList
        return next(drone for drone, orderTuple in self.solutionMatrix.items() if orderTuple[0] == order)

    def getDroneTour(self, drone: Drone, includeChargingOrders: bool = True) -> list[Order]:
        # Check if the drone tour list should include the charging orders and return the mapped list
        if includeChargingOrders: return [droneOrder[0] for droneOrder in self.solutionMatrix[drone]]

        # Use the built in filter function to check if the order destination is no charging station
        return [droneOrder[0] for droneOrder in self.solutionMatrix[drone] 
                if droneOrder[0].getDestination() not in self.chargingStationList]
    
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