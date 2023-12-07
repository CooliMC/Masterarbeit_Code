from copy import copy
from typing import Self

from simulation.Drone import Drone
from simulation.Order import Order

from model.Depot import Depot
from model.Building import Building
from model.ChargingStation import ChargingStation

class Solution():
    # Define constants for the solution class
    FLOAT_POSITIVE_INFINITY = float('+inf')
    FLOAT_NEGATIVE_INFINITY = float('-inf')

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
        return self.solutionMatrix

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

    def getTwoOptSolutions(self, drone: Drone, maximumLengthDelta: float = 0, insertChargingOrders: bool = False) -> list[Self]:
        # Resolve the tour and tour length with and without recharges
        tourOrders = self.getDroneTour(drone, False)
        tourLength = self.getTourDistance(tourOrders)
        tourDistance = self.getDroneTourDistance(drone, True)

        # Create an empty solution list for the two-opt
        twoOptSolutionList = []

        # Loop over the tour of the drone for potential edges
        for outerTourIndex in range(0, len(tourOrders) - 3, 1):
            # Loop over the rest of the tours after this to check for potential swaps
            for innerTourIndex in range(outerTourIndex + 2, len(tourOrders) - 1, 1):
                # Use a dedicated function to calculate the path delta for the two-opt
                lengthDelta = self.calculateTwoOptPathLengthDelta(
                    (tourOrders[outerTourIndex], tourOrders[outerTourIndex + 1]), 
                    (tourOrders[innerTourIndex], tourOrders[innerTourIndex + 1])
                )

                # Check the lengthDelta against the upper boundary
                if (lengthDelta >= maximumLengthDelta): continue

                # Create the two-opt solution by changing the given paths
                twoOptSolution = self.createTwoOptSolution(
                    drone, outerTourIndex, innerTourIndex, tourOrders)
                
                # Check if the new solution should have reinserted charging orders
                if insertChargingOrders:
                    # Calculate the new tour length with the delta
                    twoOptTourLength = tourLength + lengthDelta

                    # Insert charging orders back into the drone tour, if not possible continue
                    if not twoOptSolution.insertChargingOrders(drone, None, twoOptTourLength): continue

                    # Get the length of the extended tour and recalculate the length delta
                    lengthDelta = twoOptSolution.getDroneTourDistance(drone, True) - tourDistance

                    # Check the recalculated lengthDelta against the upper boundary
                    if (lengthDelta >= maximumLengthDelta): continue

                # All checks done so save the solution
                twoOptSolutionList.append(twoOptSolution)

        # Return the two-opt solution list
        return twoOptSolutionList

    def getRelocateSolutions(self, relocateOrder: Order, maximumLengthDelta: float = FLOAT_POSITIVE_INFINITY, insertChargingOrders: bool = False) -> list[Self]:
        # Resolve the drone, tour, index and tour distance of the relocate order
        relocateOrderDrone = self.getDroneByOrder(relocateOrder)
        relocateTourOrders = self.getDroneTour(relocateOrderDrone, False)
        relocateOrderIndex = relocateTourOrders.index(relocateOrder)
        relocateTourDistance = self.getDroneTourDistance(relocateOrderDrone, True)

        # Create an empty solution list for the relocates
        relocateSolutionList = []

        # Check if the relocate order is shiftable (not first order)
        if (relocateOrderIndex == 0): return relocateSolutionList

        # Check if the relocate order is shiftable (not last order)
        if (relocateOrderIndex == (len(relocateTourOrders) - 1)): return relocateSolutionList

        # Loop through the list of drones
        for partnerDrone in self.droneList:
            # Check if the relocate partner is the same drone
            if (partnerDrone == relocateOrderDrone): continue

            # Resolve the tour and tour length with recharges
            partnerTourOrders = self.getDroneTour(partnerDrone, False)
            partnerTourDistance = self.getDroneTourDistance(partnerDrone, True)

            # Loop over the tour of the partner drone for relocates
            for partnerTourIndex in range(0, len(partnerTourOrders) -1, 1):
                # Use a dedicated function to calculate the path delta for the relocate shift
                lengthDelta = self.calculateRelocatePathLengthDelta(
                    (relocateTourOrders[relocateOrderIndex - 1], relocateTourOrders[relocateOrderIndex], relocateTourOrders[relocateOrderIndex + 1]), 
                    (partnerTourOrders[partnerTourIndex], partnerTourOrders[partnerTourIndex + 1])
                )

                # Check the lengthDelta against the upper boundary
                if (lengthDelta >= maximumLengthDelta): continue

                # Create the relocate solution by changing the given paths
                relocateSolution = self.createRelocateSolution(
                    relocateOrderDrone, partnerDrone, relocateOrder, partnerTourIndex + 1)
                
                # Check if the new solution should have reinserted charging orders
                if insertChargingOrders:
                    # Insert charging orders back into the drone tours, if not possible continue
                    if not relocateSolution.insertChargingOrders(relocateOrderDrone): continue
                    if not relocateSolution.insertChargingOrders(partnerDrone): continue

                    # Resolve the updated tour distance of the reloacate order and partner tour
                    updatedRelocateTourDistance = relocateSolution.getDroneTourDistance(relocateOrderDrone, True)
                    updatedPartnerTourDistance = relocateSolution.getDroneTourDistance(partnerDrone, True)

                    # Get the length of the extended tours and recalculate the length delta with the length of the pre relocate tours
                    lengthDelta = (updatedRelocateTourDistance + updatedPartnerTourDistance - relocateTourDistance - partnerTourDistance)

                    # Check the recalculated lengthDelta against the upper boundary
                    if (lengthDelta >= maximumLengthDelta): continue

                # All checks done so save the solution
                relocateSolutionList.append(relocateSolution)

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
        lengthDelta = (
            self.getOrderDistance(firstPath[0], secondPath[0])
            + self.getOrderDistance(firstPath[1], secondPath[1])
            - self.getOrderDistance(firstPath[0], firstPath[1])
            - self.getOrderDistance(secondPath[0], secondPath[1])
        )
    
        # Return the rounded result
        return round(lengthDelta, 2)
    
    def createTwoOptSolution(self, drone: Drone, firstPathIndex: int, secondPathIndex: int, droneTour: list[Order] = None) -> Self:
        # Check if the droneTour parameter is set or resolve it
        if droneTour is None: droneTour = self.getDroneTour(drone)

        # Reconstruct the droneTour by performing the two-opt swap with the pathIndex
        droneTour = droneTour[:(firstPathIndex + 1)] + droneTour[
            secondPathIndex:firstPathIndex:-1] + droneTour[(secondPathIndex + 1):]

        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy()

        # Update the orderList of the drone with the droneTour
        solutionCopy.solutionMatrix[drone] = droneTour

        # Return the modified solution copy
        return solutionCopy
    
    ################################################################################
    ############################### Relocate FUNCTIONS #############################
    ################################################################################

    def calculateRelocatePathLengthDelta(self, firstPath: tuple[Order, Order, Order], secondPath: tuple[Order, Order]) -> float:
        # Use the precalculation to get the path delta for relocate shift
        lengthDelta = (
            self.getOrderDistance(secondPath[0], firstPath[1])
            + self.getOrderDistance(firstPath[1], secondPath[1])
            + self.getOrderDistance(firstPath[0], firstPath[2])
            - self.getOrderDistance(firstPath[0], firstPath[1])
            - self.getOrderDistance(firstPath[1], firstPath[2])
            - self.getOrderDistance(secondPath[0], secondPath[1])
        )
    
        # Return the rounded result
        return round(lengthDelta, 2)

    def createRelocateSolution(self, sourceDrone: Drone, destinationDrone: Drone, relocateOrder: Order, destinationTourIndex: int) -> Self:
        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy()

        # Remove the relocate order from the source drone tour
        solutionCopy.solutionMatrix[sourceDrone].remove(relocateOrder)

        # Add the relocate order to the destination drone tour at the given destination tour index
        solutionCopy.solutionMatrix[destinationDrone].insert(destinationTourIndex, relocateOrder)

        # Return the modified solution copy
        return solutionCopy

    ################################################################################
    ############################### SUPPORT FUNCTIONS ##############################
    ################################################################################

    def insertChargingOrders(self, drone: Drone, droneTour: list[Order] = None, droneTourLength: float = None) -> bool:
        # Check if the droneTour parameter is set or resolve it
        if droneTour is None: droneTour = self.getDroneTour(drone, False)

        # Check if the droneTourLength parameter is set or resolve it
        if droneTourLength is None: droneTourLength = self.getTourDistance(droneTour)

        # Resolve the remaining distance of the drone
        droneDistance = drone.getRemainingFlightDistance()

        # Not recharge if drone tour shorter then drone range
        if droneTourLength <= droneDistance: return True

        # Save the insert positions
        chargeOrderIndexList = []

        # Save the remaining tour range
        remainingTourRange = droneDistance

        # Loop over the drone tour to insert charging orders
        for droneTourIndex in range(0, len(droneTour) - 1, 1):
            # Get the current trip length
            tripLength = self.getOrderDistance(
                droneTour[droneTourIndex], 
                droneTour[droneTourIndex + 1]
            )

            # Check if the drone has not enought range after the current trip to reach a charging station with the remaning power
            if not self.isChargingStationInRange(droneTour[droneTourIndex + 1], remainingTourRange - tripLength):
                
                # Check if any charging station is in range to split the current trip with a recharge in between the orders
                if not self.isChargingStationInRange(droneTour[droneTourIndex], remainingTourRange): return False

                # Resolve the closest charging station to the current order
                nextChargingStation = self.getClosestChargingStation(droneTour[droneTourIndex])
                
                # Insert a position of the charging order in the list
                chargeOrderIndexList.insert(0, (droneTourIndex + 1, Order(nextChargingStation, 0, 900)))

                # Reset the remaining tour range
                remainingTourRange = droneDistance

                # Recalculate the trip length
                tripLength = self.getOrderBuildingDistance(
                    droneTour[droneTourIndex + 1],
                    nextChargingStation
                )

            # Remove the trip length from the remaining tour range
            remainingTourRange -= tripLength

        # Loop through the charge order index list to insert them
        for chargeOrderTuple in chargeOrderIndexList:
            # Inset the charge order at the given index (back to front)
            droneTour.insert(chargeOrderTuple[0], chargeOrderTuple[1])

        # Replace the drone tour in the solution matrix
        self.solutionMatrix[drone] = droneTour

        # Charge order insert worked
        return True

    def getSolutionCopy(self) -> Self:
        # Use the built-in function to copy the solution
        solutionCopy = copy(self)

        # Create a shallow copy of the solution matrix with dict function
        solutionCopy.solutionMatrix = dict(solutionCopy.solutionMatrix)

        # Loop over the shallow copy of the solution matrix
        for drone, orderList in solutionCopy.solutionMatrix.items():
            # Create a shallow copy of the orderList with the list function
            solutionCopy.solutionMatrix[drone] = list(orderList)

        # Return the solution copy
        return solutionCopy

    def getBuildingDistance(self, sourceBuilding: Building, destinationBuilding: Building) -> float:
        # Use the precalculated distanceMatrix to get the distance between the buildings
        return self.distanceMatrix[sourceBuilding][destinationBuilding]

    def getOrderDistance(self, sourceOrder: Order, destinationOrder: Order) -> float:
        # Use the precalculated distanceMatrix to get the distance between the orders
        return self.distanceMatrix[sourceOrder.getDestination()][destinationOrder.getDestination()]

    def getOrderBuildingDistance(self, sourceOrder: Order, destinationBuilding: Building) -> float:
        # Use the precalculated distanceMatrix to get the distance between the order and building
        return self.distanceMatrix[sourceOrder.getDestination()][destinationBuilding]

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
    

    # TODO: Idea - Cache the closest charging station to each order for O(1) instead of O(n) lookup
    
    ################################################################################
    ####################### CHARGING STATION SUPPORT FUNCTIONS #####################
    ################################################################################

    def isChargingStationInRange(self, order: Order, range: float) -> bool:
        # Use the built-in filter function to check if a charging station is in range of the current order
        return next((True for x in self.chargingStationList if self.getOrderBuildingDistance(order, x) <= range), False)
    
    def getChargingStationsInRange(self, order: Order, range: float) -> list[ChargingStation]:
        # Use the built-in filter function to get all charging stations that are in range
        return [x for x in self.chargingStationList if self.getOrderBuildingDistance(order, x) <= range]
    
    def getClosestChargingStation(self, order: Order) -> ChargingStation:
        # Use the built-in min function to return the closest charging station from the list
        return min(self.chargingStationList, key=lambda x: self.getOrderBuildingDistance(order, x))
        
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