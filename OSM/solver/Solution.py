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

        # Precalculate the order neighborhood matrix with the distance matrix for improved neighborhood search alogirthms
        self.orderNeighborhoodMatrix = Solution.CalculateOrderNeighborhoodMatrix(self.orderList, self.distanceMatrix)
        
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
    
    def getOrderNeighborhoodMatrix(self) -> dict[Order, list[Order]]:
        # Return the orderNeighborhoodMatrix
        return self.orderNeighborhoodMatrix
    
    def getSolutionMatrix(self) -> dict[Drone, list[Order]]:
        # Return the solutionMatrix
        return self.solutionMatrix

    ################################################################################
    ############################### SCORE FUNCTIONS ################################
    ################################################################################

    def getDistanceScore(self) -> float:
        # Sum up the tour distance of all drones as a factor for the score calculation
        tourDistanceSum = sum(self.getDroneTourDistance(drone, True) for drone in self.droneList)

        return tourDistanceSum
        # Calculate the score of the drones by the distance with a formular like this:
        # sum(distance of each drone) * (1 + (longestDroneDistance - shortestDroneDistance))

    def getTimeScore(self) -> float:
        # Get the tour time list of all drones as a factor for the score calculation
        droneTourTimeList = [self.getDroneTourTime(drone, True) for drone in self.droneList]

        # Calculate the average drone tour time as a factor for the score calculation 
        avgDroneTourTime = (sum(droneTourTimeList) / len(droneTourTimeList))
        
        # Sum up the drone tour time and scale the score by the difference between the min/max and avg drone tour time
        return sum(droneTourTimeList) * (1 + ((max(droneTourTimeList) - min(droneTourTimeList)) / avgDroneTourTime) / 2)

    ################################################################################
    ####################### NEIGHBORHOOD SOLUTION FUNCTIONS ########################
    ################################################################################

    def getNeighborhoodSolutions(self, maximumLengthDelta: float = FLOAT_POSITIVE_INFINITY, insertChargingOrders: bool = False) -> list[Self]:
        # Create an empty solution list for the neighborhood
        neighborhoodSolutionList = []

        # Loop through the order list to calculate the neighborhood for each order
        for neighborhoodOrder in self.orderList:
            # Run the RelocateSolution algorithm to get all shifted solutions and add them to the neighborhoodSolutionList
            neighborhoodSolutionList.extend(self.getRelocateSolutions(neighborhoodOrder, maximumLengthDelta, insertChargingOrders))

            # Run the ExchangeSolution algorithm to get all swapped solutions and add them to the neighborhoodSolutionList
            neighborhoodSolutionList.extend(self.getExchangeSolutions(neighborhoodOrder, maximumLengthDelta, insertChargingOrders))

            # Run the CrossSolution algorithm to get all crossed solutions and add them to the neighborhoodSolutionList
            neighborhoodSolutionList.extend(self.getCrossSolutions(neighborhoodOrder, maximumLengthDelta, insertChargingOrders))

        # Return the neighborhoodSolutionList
        return neighborhoodSolutionList

    ################################################################################
    ####################### NEIGHBORHOOD ALGORITHM FUNCTIONS #######################
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
                    drone, outerTourIndex, innerTourIndex)
                
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
            for partnerTourIndex in range(0, len(partnerTourOrders) - 1, 1):
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

    def getExchangeSolutions(self, exchangeOrder: Order, maximumLengthDelta: float = FLOAT_POSITIVE_INFINITY, insertChargingOrders: bool = False) -> list[Self]:
        # Resolve the drone, tour, index and tour distance of the exchange order
        exchangeOrderDrone = self.getDroneByOrder(exchangeOrder)
        exchangeTourOrders = self.getDroneTour(exchangeOrderDrone, False)
        exchangeOrderIndex = exchangeTourOrders.index(exchangeOrder)
        exchangeTourDistance = self.getDroneTourDistance(exchangeOrderDrone, True)

        # Create an empty solution list for the exchanges
        exchangeSolutionList = []

        # Check if the exchange order is swapable (not first order)
        if (exchangeOrderIndex == 0): return exchangeSolutionList

        # Check if the exchange order is swapable (not last order)
        if (exchangeOrderIndex == (len(exchangeTourOrders) - 1)): return exchangeSolutionList

        # Loop through the list of drones
        for partnerDrone in self.droneList:
            # Check if the exchange partner is the same drone
            if (partnerDrone == exchangeOrderDrone): continue

            # Resolve the tour and tour length with recharges
            partnerTourOrders = self.getDroneTour(partnerDrone, False)
            partnerTourDistance = self.getDroneTourDistance(partnerDrone, True)

            # Loop over the tour of the partner drone for exchanges
            for partnerTourIndex in range(1, len(partnerTourOrders) - 1, 1):
                # Use a dedicated function to calculate the path delta for the exchange swap
                lengthDelta = self.calculateExchangePathLengthDelta(
                    (exchangeTourOrders[exchangeOrderIndex - 1], exchangeTourOrders[exchangeOrderIndex], exchangeTourOrders[exchangeOrderIndex + 1]), 
                    (partnerTourOrders[partnerTourIndex - 1], partnerTourOrders[partnerTourIndex], partnerTourOrders[partnerTourIndex + 1])
                )

                # Check the lengthDelta against the upper boundary
                if (lengthDelta >= maximumLengthDelta): continue

                # Create the exchange solution by changing the given paths
                exchangeSolution = self.createExchangeSolution(
                    exchangeOrderDrone, partnerDrone, exchangeOrderIndex, partnerTourIndex)
                
                # Check if the new solution should have reinserted charging orders
                if insertChargingOrders:
                    # Insert charging orders back into the drone tours, if not possible continue
                    if not exchangeSolution.insertChargingOrders(exchangeOrderDrone): continue
                    if not exchangeSolution.insertChargingOrders(partnerDrone): continue

                    # Resolve the updated tour distance of the reloacate order and partner tour
                    updatedExchangeTourDistance = exchangeSolution.getDroneTourDistance(exchangeOrderDrone, True)
                    updatedPartnerTourDistance = exchangeSolution.getDroneTourDistance(partnerDrone, True)

                    # Get the length of the extended tours and recalculate the length delta with the length of the pre exchange tours
                    lengthDelta = (updatedExchangeTourDistance + updatedPartnerTourDistance - exchangeTourDistance - partnerTourDistance)

                    # Check the recalculated lengthDelta against the upper boundary
                    if (lengthDelta >= maximumLengthDelta): continue

                # All checks done so save the solution
                exchangeSolutionList.append(exchangeSolution)

        # Return the exchangeSolutionList
        return exchangeSolutionList

    def getCrossSolutions(self, crossOrder: Order, maximumLengthDelta: float = FLOAT_POSITIVE_INFINITY, insertChargingOrders: bool = False) -> list[Self]:
        # Resolve the drone, tour, index and tour distance of the cross order
        crossOrderDrone = self.getDroneByOrder(crossOrder)
        crossTourOrders = self.getDroneTour(crossOrderDrone, False)
        crossOrderIndex = crossTourOrders.index(crossOrder)
        crossTourDistance = self.getDroneTourDistance(crossOrderDrone, True)

        # Create an empty solution list for the crosses
        crossSolutionList = []

        # Check if the cross order is swapable (not first order)
        if (crossOrderIndex == 0): return crossSolutionList

        # Check if the cross order is swapable (not last order)
        if (crossOrderIndex == (len(crossTourOrders) - 1)): return crossSolutionList

        # Loop through the list of drones
        for partnerDrone in self.droneList:
            # Check if the cross partner is the same drone
            if (partnerDrone == crossOrderDrone): continue

            # Resolve the tour and tour length with recharges
            partnerTourOrders = self.getDroneTour(partnerDrone, False)
            partnerTourDistance = self.getDroneTourDistance(partnerDrone, True)

            # Loop over the tour of the partner drone for crosses
            for partnerTourIndex in range(1, len(partnerTourOrders) - 1, 1):
                # Use a dedicated function to calculate the path delta for the cross swap
                lengthDelta = self.calculateCrossPathLengthDelta(
                    (crossTourOrders[crossOrderIndex], crossTourOrders[crossOrderIndex + 1]), 
                    (partnerTourOrders[partnerTourIndex], partnerTourOrders[partnerTourIndex + 1])
                )

                # Check the lengthDelta against the upper boundary
                if (lengthDelta >= maximumLengthDelta): continue

                # Create the cross solution by changing the given paths
                crossSolution = self.createCrossSolution(
                    crossOrderDrone, partnerDrone, crossOrderIndex, partnerTourIndex)
                
                # Check if the new solution should have reinserted charging orders
                if insertChargingOrders:
                    # Insert charging orders back into the drone tours, if not possible continue
                    if not crossSolution.insertChargingOrders(crossOrderDrone): continue
                    if not crossSolution.insertChargingOrders(partnerDrone): continue

                    # Resolve the updated tour distance of the cross order and partner tour
                    updatedCrossTourDistance = crossSolution.getDroneTourDistance(crossOrderDrone, True)
                    updatedPartnerTourDistance = crossSolution.getDroneTourDistance(partnerDrone, True)

                    # Get the length of the extended tours and recalculate the length delta with the length of the pre crossed tours
                    lengthDelta = (updatedCrossTourDistance + updatedPartnerTourDistance - crossTourDistance - partnerTourDistance)

                    # Check the recalculated lengthDelta against the upper boundary
                    if (lengthDelta >= maximumLengthDelta): continue
                
                # All checks done so save the solution
                crossSolutionList.append(crossSolution)

        # Return the crossSolutionList
        return crossSolutionList
    
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
    
    def createTwoOptSolution(self, drone: Drone, firstPathIndex: int, secondPathIndex: int) -> Self:
        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy()
        
        # Resolve the droneTour from the solution copy
        droneTour = solutionCopy.getDroneTour(drone, False)

        # Reconstruct the droneTour by performing the two-opt swap with the pathIndex
        droneTour = droneTour[:(firstPathIndex + 1)] + droneTour[
            secondPathIndex:firstPathIndex:-1] + droneTour[(secondPathIndex + 1):]

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

        # Resolve the source and destination drone tour
        sourceDroneTour = solutionCopy.getDroneTour(sourceDrone, False)
        destinationDroneTour = solutionCopy.getDroneTour(destinationDrone, False)

        # Remove the relocate order from the source drone tour
        sourceDroneTour.remove(relocateOrder)

        # Add the relocate order to the destination drone tour at the given destination tour index
        destinationDroneTour.insert(destinationTourIndex, relocateOrder)

        # Update the orderList of the source and destination drone
        solutionCopy.solutionMatrix[sourceDrone] = sourceDroneTour
        solutionCopy.solutionMatrix[destinationDrone] = destinationDroneTour

        # Return the modified solution copy
        return solutionCopy

    ################################################################################
    ############################### Exchange FUNCTIONS #############################
    ################################################################################

    def calculateExchangePathLengthDelta(self, firstPath: tuple[Order, Order, Order], secondPath: tuple[Order, Order, Order]) -> float:
        # Use the precalculation to get the path delta for exchange swap
        lengthDelta = (
            self.getOrderDistance(firstPath[0], secondPath[1])
            + self.getOrderDistance(secondPath[1], firstPath[2])
            + self.getOrderDistance(secondPath[0], firstPath[1])
            + self.getOrderDistance(firstPath[1], secondPath[2])
            - self.getOrderDistance(firstPath[0], firstPath[1])
            - self.getOrderDistance(firstPath[1], firstPath[2])
            - self.getOrderDistance(secondPath[0], secondPath[1])
            - self.getOrderDistance(secondPath[1], secondPath[2])
        )
    
        # Return the rounded result
        return round(lengthDelta, 2)
    
    def createExchangeSolution(self, sourceDrone: Drone, destinationDrone: Drone, exchangeOrderIndex: int, destinationTourIndex: int) -> Self:
        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy()

        # Resolve the source and destination drone tour
        sourceDroneTour = solutionCopy.getDroneTour(sourceDrone, False)
        destinationDroneTour = solutionCopy.getDroneTour(destinationDrone, False)

        # Remove the exchange orders from the source and destination drone tour
        exchangeOrder = sourceDroneTour.pop(exchangeOrderIndex)
        destinationTourOrder = destinationDroneTour.pop(destinationTourIndex)

        # Add the exchange orders to the source and destination drone tour at the given index
        sourceDroneTour.insert(exchangeOrderIndex, destinationTourOrder)
        destinationDroneTour.insert(destinationTourIndex, exchangeOrder)

        # Update the orderList of the source and destination drone
        solutionCopy.solutionMatrix[sourceDrone] = sourceDroneTour
        solutionCopy.solutionMatrix[destinationDrone] = destinationDroneTour

        # Return the modified solution copy
        return solutionCopy
    
    ################################################################################
    ############################### Cross FUNCTIONS ################################
    ################################################################################

    def calculateCrossPathLengthDelta(self, firstPath: tuple[Order, Order], secondPath: tuple[Order, Order]) -> float:
        # Use the precalculation to get the path delta for exchange swap
        lengthDelta = (
            self.getOrderDistance(firstPath[0], secondPath[1])
            + self.getOrderDistance(secondPath[0], firstPath[1])
            - self.getOrderDistance(firstPath[0], firstPath[1])
            - self.getOrderDistance(secondPath[0], secondPath[1])
        )
    
        # Return the rounded result
        return round(lengthDelta, 2)
    
    def createCrossSolution(self, sourceDrone: Drone, destinationDrone: Drone, crossOrderIndex: int, destinationTourIndex: int) -> Self:
        # Create a partly deep copy of the solution
        solutionCopy = self.getSolutionCopy()

        # Resolve the source and destination tour from the solution matrix
        sourceDroneTour = solutionCopy.getDroneTour(sourceDrone, False)
        destinationDroneTour = solutionCopy.getDroneTour(destinationDrone, False)

        # Create the crossover tour by slicing the drone tours after the order indexes and adding them back together
        sourceDroneCrossoverTour = sourceDroneTour[:(crossOrderIndex + 1)] + destinationDroneTour[(destinationTourIndex + 1):]
        destinationDroneCrossoverTour = destinationDroneTour[:(destinationTourIndex + 1)] + sourceDroneTour[(crossOrderIndex + 1):]

        # Set the crossover tours as the new solution tour for the drones
        solutionCopy.solutionMatrix[sourceDrone] = sourceDroneCrossoverTour
        solutionCopy.solutionMatrix[destinationDrone] = destinationDroneCrossoverTour

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

    def getSolutionCopy(self, includeChargingOrders: bool = True) -> Self:
        # Use the built-in function to copy the solution
        solutionCopy = copy(self)

        # Create a shallow copy of the solution matrix with dict function
        solutionCopy.solutionMatrix = dict(solutionCopy.solutionMatrix)
        # TODO: Check and remove charging orders if set
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
    
    def getClosestBuildings(self, sourceBuilding: Building) -> list[Building]:
        # Use the precalculated distanceMatrix to get the presorted keys building list
        return list(self.distanceMatrix[sourceBuilding].keys())

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
    
    def getDroneTourFlightTime(self, drone: Drone, includeChargingOrders: bool = True) -> float:
        # Use the getDroneTourDistance and calculateFlightTime function to get the drone tour flight time
        return drone.calculateFlightTime(self.getDroneTourDistance(drone, includeChargingOrders))
    
    def getDroneTourDwellTime(self, drone: Drone, includeChargingOrders: bool = True) -> int:
        # Use the getDroneTour and getDwellTime function to get the drone tour dwell time (sum)
        return sum(droneOrder.getDwellTime() for droneOrder in self.getDroneTour(drone, includeChargingOrders))
    
    def getDroneTourTime(self, drone: Drone, includeChargingOrders: bool = True) -> float:
        # Use the getDroneTourFlightTime and getDroneTourDwellTime function to get the drone tour time (flight + dwell time)
        return self.getDroneTourFlightTime(drone, includeChargingOrders) + self.getDroneTourDwellTime(drone, includeChargingOrders)

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

        # Loop through the complete building list to sort the inner dict by distance
        for building in buildingList:
            # Since python 3.7 dicts preserve the insertion order so we can use this to save the buildings sorted by distance
            distanceMatrix[building] = dict(sorted(distanceMatrix[building].items(), key=lambda x: x[1]))

        # Return the distance matrix
        return distanceMatrix
    
    @staticmethod
    def CalculateOrderNeighborhoodMatrix(orderList: list[Order], distanceMatrix: dict[Building, dict[Building, float]]) -> dict[Order, list[Order]]:
        # Create a dictionary to look up the corresponding order for each building in a constant time
        buildingOrderDictionary = dict(map(lambda order: (order.getDestination(), order), orderList))

        # Create an empty dictionary for the order neighborhood
        orderNeighborhoodMatrix = dict()

        # Loop through the order list once
        for order in orderList:
            # Resolve the neighborhood building list from the distance matrix by the order destination
            neighborhoodBuildingList = list(distanceMatrix[order.getDestination()].keys())

            # Use the built-in list conversion to check all neighborhood buildings and convert them back to orders
            orderNeighborhoodMatrix[order] = [buildingOrderDictionary[neighborBuilding] for 
                neighborBuilding in neighborhoodBuildingList if neighborBuilding in buildingOrderDictionary]
        
        # Return the order neighborhood matrix
        return orderNeighborhoodMatrix