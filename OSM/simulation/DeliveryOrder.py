from model.Building import Building

class DeliveryOrder():
    # Constructor the delivery with a given arguemnts
    def __init__(self, weight: int, destination: Building):
        # Save the weight [g]
        self.weight = weight

        # Save the destination [Building]
        self.destination = destination

    # Getter function for the weight [g]
    def getWeight(self) -> int:
        return self.weight

    # Getter function for the destiantion [Building]
    def getDestination(self) -> Building:
        return self.destination