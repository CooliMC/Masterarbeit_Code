from model.Building import Building

class Order():
    # Define static parameter for the order class
    orderInstanceCounter = 0

    # Constructor the order with a given arguemnts
    def __init__(self, destination: Building, weight: int = 0, dwellTime: int = 0):
        # Increment the order instance counter
        Order.orderInstanceCounter += 1
        
        # Set the order instance count as the unique order id 
        self.id = Order.orderInstanceCounter

        # Save the destination [Building]
        self.destination = destination

        # Save the weight [g]
        self.weight = weight

        # Save the dwell time [s]
        self.dwellTime = dwellTime

    ################################################################################
    ############################### GETTER FUNCTIONS ###############################
    ################################################################################

    # Getter function for the id [int]
    def getId(self) -> int:
        return self.id

    # Getter function for the destiantion [Building]
    def getDestination(self) -> Building:
        return self.destination
    
    # Getter function for the weight [g]
    def getWeight(self) -> int:
        return self.weight
    
    # Getter function for the dwell time [s]
    def getDwellTime(self) -> int:
        return self.dwellTime
    
    ################################################################################
    ################################ CLASS FUNCTIONS ###############################
    ################################################################################

    # Overwrite the string representation
    def __str__(self):
        return f'Order(id={self.id}, destination={self.destination}, weight={self.weight}, dwellTime={self.dwellTime})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Order(id={self.id}, destination={self.destination}, weight={self.weight}, dwellTime={self.dwellTime})'