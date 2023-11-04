from model.Building import Building

class Order():
    # Constructor the order with a given arguemnts
    def __init__(self, destination: Building, weight: int = 0, dwellTime: int = 0):
        # Save the destination [Building]
        self.destination = destination

        # Save the weight [g]
        self.weight = weight

        # Save the dwell time [s]
        self.dwellTime = dwellTime

    # Getter function for the destiantion [Building]
    def getDestination(self) -> Building:
        return self.destination
    
    # Getter function for the weight [g]
    def getWeight(self) -> int:
        return self.weight
    
    # Getter function for the dwell time [s]
    def getDwellTime(self) -> int:
        return self.dwellTime
    
    # Overwrite the string representation
    def __str__(self):
        return f'Order(destination={self.destination}, weight={self.weight}, dwellTime={self.dwellTime})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Order(destination={self.destination}, weight={self.weight}, dwellTime={self.dwellTime})'