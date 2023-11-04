from simulation.Drone import Drone
from simulation.Order import Order

from model.Depot import Depot
from model.Building import Building
from model.ChargingStation import ChargingStation

from .ExitCode import ExitCode

class Solver():
    # Constructor the order with a given arguemnts
    def __init__(self, droneList: [Drone], depot: Depot, chargingStationList: [ChargingStation], orderList: [Order]):
        # Save the list of drones
        self.droneList = droneList

        # Save the depot
        self.depot = depot

        # Save the list of charging stations
        self.chargingStationList = chargingStationList

        # Save the list of orders
        self.orderList = orderList

        # Create and prefilled solution matrix with the drones as key and list of orders and distance
        self.solutionMatrix = dict(map(lambda drone: (drone, [(Order(depot), 0)]), self.droneList))

    ################################################################################
    ############################### GETTER FUNCTIONS ###############################
    ################################################################################

    def getDroneList(self) -> [Drone]:
        # Return the droneList
        return self.droneList
    
    def getDepot(self) -> [Depot]:
        # Return the depot
        return self.depot
    
    def getChargingStationList(self) -> [ChargingStation]:
        # Return the chargingStationList
        return self.chargingStationList

    def getOrderList(self) -> [Order]:
        # Return the districtList
        return self.orderList
    
    def getSolutionMatrix(self) -> dict:
        # Return the solutionMatrix
        self.solutionMatrix

    ################################################################################
    ############################### SOLVER FUNCTIONS ###############################
    ################################################################################

    def getInitialOrder(self):
        return None

    def getNextOrder(self, drone: Drone) -> Order:
        return None
    
    def generateInitialSolution(self, orderIndex: int = 0) -> ExitCode:
        # Check if all orders are assigned to a drone
        if (orderIndex == len(self.orderList)):
            # Return exit code for success
            return ExitCode.SUCCESS
        
        # Define the constraint failure level exit code
        constrainFailureLevel = ExitCode.NO_SOLUTION

        # Resolve the current order from the list
        currentOrder = self.orderList[orderIndex]
        
        # Loop over the list of drones
        for drone in sorted(self.droneList, key=lambda x: self.solutionMatrix[x][-1][0].getDestination().getDistanceTo(currentOrder.getDestination())):
            # Resolve the last order and milage of the current drone
            lastDroneOrder = self.solutionMatrix[drone][-1][0]
            lastDroneMilage = self.solutionMatrix[drone][-1][1]
            
            # Calculate the distance between the last and current order
            lastToCurrentOrderDistance = lastDroneOrder.getDestination().getDistanceTo(currentOrder.getDestination())

            # Constraint: Remaining range of the drone to reach the desired target
            if (lastDroneMilage + lastToCurrentOrderDistance) > drone.getRemainingFlightDistance():
                # Set the constrainFailureLevel exit code
                constrainFailureLevel = ExitCode.ORDER_NOT_IN_RANGE
                
                # Goto next drone
                continue

            # Calculate the remaining range of the drone after the current order 
            remainingDroneCharge = drone.getRemainingFlightDistance() - (lastDroneMilage + lastToCurrentOrderDistance)

            # Constraint: Check if after the current order enough charge is left to reach a charging stations
            if not self.isChargingStationInRange(currentOrder.getDestination(), remainingDroneCharge):
                # Set the constrainFailureLevel exit code
                constrainFailureLevel = ExitCode.NO_CHARGING_STATION_IN_RANGE

                # Goto next drone
                continue
            
            # Drone has enough capacity so give the order to the current drone
            self.solutionMatrix[drone].append((currentOrder, lastDroneMilage + lastToCurrentOrderDistance))

            # Check the recursive alogrithms backtracking response code
            recursiveResponseCode = self.generateInitialSolution(orderIndex + 1)

            # Check if the order fails because no charging station in range
            if (recursiveResponseCode == ExitCode.NO_CHARGING_STATION_IN_RANGE):
                # Order the drones to the closest charging station
                for subDrone in self.droneList:
                    # Resolve the last order of the current subDrone
                    lastSubDroneOrder = self.solutionMatrix[subDrone][-1][0]

                    # Get the closest charging station for the subDrone by its last order in the list
                    targetChargingStation = self.getClosestChargingStation(lastSubDroneOrder.getDestination())

                    # Add the charging station as next order of the subDrone and reset its available milage
                    self.solutionMatrix[subDrone].append((Order(targetChargingStation, 0, 900), 0))
                
                # Check the recursive alogrithms backtracking response code
                recursiveResponseCode = self.generateInitialSolution(orderIndex + 1)

                # Check if the recursive algorithm was no success
                if (recursiveResponseCode != ExitCode.SUCCESS):
                    # Remoe the charging station orders from the drons order list
                    for subDrone in self.droneList: self.solutionMatrix[subDrone].pop()

            # Check if the recursive algorithm was a success to end it
            if (recursiveResponseCode == ExitCode.SUCCESS):
                # Return exit code for success
                return ExitCode.SUCCESS
            
            # Revert the changes of the current stage
            self.solutionMatrix[drone].pop()

        # Return the last given constrainFailureLevel exit code
        return constrainFailureLevel

    def isChargingStationInRange(self, location: 'Building | (float, float)', range: float) -> bool:
        # Use the built-in filter function to check if a charging station is in range
        return next((True for x in self.chargingStationList if x.getDistanceTo(location) <= range), False)

    def getChargingStationsInRange(self, location: 'Building | (float, float)', range: float) -> [ChargingStation]:
        # Use the built-in filter function to get all charging stations that are in range
        return [x for x in self.chargingStationList if x.getDistanceTo(location) <= range]

    def getClosestChargingStation(self, location: 'Building | (float, float)') -> ChargingStation:
        # Use the built-in min function to return the closest charging station from the list
        return min(self.chargingStationList, key=lambda x: x.getDistanceTo(location))
            