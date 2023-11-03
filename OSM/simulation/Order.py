from model.Building import Building

class Order():
    # Constructor the order with a given arguemnts
    def __init__(self, destination: Building, weight: int = 0):
        # Save the destination [Building]
        self.destination = destination

        # Save the weight [g]
        self.weight = weight

    # Getter function for the destiantion [Building]
    def getDestination(self) -> Building:
        return self.destination
    
    # Getter function for the weight [g]
    def getWeight(self) -> int:
        return self.weight