from .Drone import Drone
from .Order import Order

class Solver():
    # Constructor the order with a given arguemnts
    def __init__(self, droneList: [Drone], depot, orderList: [Order]):
        # Save the list of drones
        self.droneList = droneList

        # Save the list of orders
        self.orderList = orderList

        # Create and prefilled solution matrix with the drones as key and list of orders and distance
        self.solutionMatrix = dict(map(lambda drone: (drone, [(Order(depot), 0)]), self.droneList))

    def getInitialOrder(self):
        return None

    def getNextOrder(self, drone: Drone) -> Order:
        return None
    
    def getInitialSolution(self, orderIndex: int = 0) -> int:
        # Check if all orders are assigned to a drone
        if (orderIndex == len(self.orderList)):
            # Return exit code for success
            return 0 # Success (0)

        # Define the constraint failure level exit code
        constrainFailureLevel = 1 # NoSolution (1)

        # Resolve the current order from the list
        currentOrder = self.orderList[orderIndex]
        print(f'Calculation Order(index={orderIndex}, destination={currentOrder.getDestination()})')
        # Loop over the list of drones # GOTO: NextDrone
        for drone in self.droneList:
            # Resolve the last order and milage of the current drone
            lastDroneOrder = self.solutionMatrix[drone][-1][0]
            lastDroneMilage = self.solutionMatrix[drone][-1][1]
            
            # Calculate the distance between the last and current order
            lastToCurrentOrderDistance = lastDroneOrder.getDestination().getDistanceTo(currentOrder.getDestination())

            # Constraint: Remaining range of the drone to reach the desired target
            if ((lastDroneMilage + lastToCurrentOrderDistance) > drone.getRemainingFlightDistance()):
                # Set the constrainFailureLevel exit code
                constrainFailureLevel = 2 # NoDroneRange (2)
                print(f'NoDroneRange (currentMilage={lastDroneMilage}, necesarryDistance={lastToCurrentOrderDistance}, remainingFlightDistance={drone.getRemainingFlightDistance()})')
                # Goto next drone
                continue
            
            # Drone has enough capacity so give the order to the current drone
            self.solutionMatrix[drone].append((currentOrder, lastDroneMilage + lastToCurrentOrderDistance))

            # Check the recursive alogrithms backtracking response code
            recursiveResponseCode = self.getInitialSolution(orderIndex + 1)

            # Check if the recursive algorithm was a success to end it
            if (recursiveResponseCode == 0):
                # Return exit code for success
                return 0 # Success (0)
            
            # Revert the changes of the current stage
            self.solutionMatrix[drone].pop()


        # Return the last given constrainFailureLevel exit code
        return constrainFailureLevel
            