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

    def getShiftSolutions(self, orderIndex: int) -> list[Self]:
        # Resolve the order form the list of orders to compare
        currentOrder = self.orderList[orderIndex]

        # Create an empty solution list for the shifts
        shiftSolutionList = []

        # Loop through the list of drones 

        # TODO: Implement the shift

    def getSwapSolutions(self, orderIndex: int) -> list[Self]:
        # Resolve the order form the list of orders to compare
        currentOrder = self.orderList[orderIndex]

        # Create an empty solution list for the swaps
        swapSolutionList = []

        # Loop through all orders to search for swap partners
        for swapPartnerOrder in self.orderList:
            # Check if the swap partner is the current order and continue
            if (swapPartnerOrder == currentOrder): continue


    def getCrossSolutions(self, orderIndex: int) -> list[Self]:
        return []
    
    ################################################################################
    ############################### SUPPORT FUNCTIONS ##############################
    ################################################################################

    def getDroneTour(self, drone: Drone, includeChargingOrders: bool = True) -> list[Order]:
        # Check if the drone tour list should include the charging orders and return the mapped list
        if includeChargingOrders: return [droneOrder[0] for droneOrder in self.solutionMatrix[drone]]

        # Use the built in filter function to check if the order destination is no charging station
        return [droneOrder[0] for droneOrder in self.solutionMatrix[drone] 
                if droneOrder[0].getDestination() not in self.chargingStationList]
    
    def getDroneTourDistance(self, drone: Drone, includeChargingOrders: bool = True) -> float:
        # Resolve the droneTour by using the getDroneTour function
        droneTour = self.getDroneTour(drone, includeChargingOrders)

        return sum()

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