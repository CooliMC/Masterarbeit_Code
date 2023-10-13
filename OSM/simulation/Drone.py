from .Delivery import Delivery

class Drone():
    # Constructor the drone with a given arguemnts
    def __init__(self, batterySize: int, loadingCapacity: int, initialDeliveryList: [Delivery] = [], initialBatteryCharge: int = None):
        # Check if the batterySize is a positive integer and if not raise a ValueError
        if (batterySize <= 0): raise ValueError('Invalid non-positive battery size.')
        
        # Save the batterySize [w/h]
        self.batterySize = batterySize

        # Check if the loadingCapacity is a positive integer and if not raise a ValueError
        if (loadingCapacity <= 0): raise ValueError('Invalid non-positive loading capacity.')

        # Save the loadingCapacity [g]
        self.loadingCapacity = loadingCapacity

        # Check if the sum of deliveries in the initialDeliveryList exceeds the loadingCapacity
        if (sum(delivery.getWeight() for delivery in initialDeliveryList) >= loadingCapacity):
            # Raise a ValueError to explain the problem with the total weight and the loadingCapacity
            raise ValueError('Total weight of initial delivery list exceeds the maximum loading capacity.')

        # Save the deliveryList [Delivery[]]
        self.deliveryList = initialDeliveryList

        # Save the batterySize as the currentBatteryCharge [w/h]
        self.currentBatteryCharge = batterySize

        # Check if the initialBatteryCharge is a valid int and between zero and batterySize
        if isinstance(initialBatteryCharge, int) and (0 <= initialBatteryCharge <= batterySize):
            # Set the currentBatteryCharge from the paramater
            self.currentBatteryCharge = initialBatteryCharge

    # Getter function for the battery size [w/h]
    def getBatterySize(self) -> int:
        return self.batterySize
    
    # Getter function for the loading capacity [g]
    def getLoadingCapacity(self) -> int:
        return self.loadingCapacity

    # Getter function for the delivery list [Delivery[]]
    def getDeliveryList(self) -> [Delivery]:
        return self.deliveryList

    # Getter function for the current battery charge [w/h]
    def getCurrentBatteryCharge(self) -> int:
        return self.currentBatteryCharge
    
    # Getter function for the occupied loading capacity [g]
    def getOccupiedLoadingCapacity(self) -> int:
        # Loop over the delivery list and sum up the weight of the deliveries
        return sum(delivery.getWeight() for delivery in self.deliveryList)
    
    # Getter function for the free loading capacity [g]
    def getFreeLoadingCapacity(self) -> int:
        # Use the built-in functions to calculate the free loading capcity
        return (self.getLoadingCapacity() - self.getOccupiedLoadingCapacity())
    
    # Check for constrains and pick up a new delivery for the drone
    def pickUpDelivery(self, delivery: Delivery, queueSpace: int = 0) -> bool:
        # Check if the drone has enough loading capacity for the delivery
        if (self.getFreeLoadingCapacity() < delivery.getWeight()):
            # Reject the delivery
            return False
        
        # Add the delivery to the list on the given space
        self.deliveryList.insert(queueSpace, delivery)

    #def dropDelivery(self, delivery)