class Drone():
    # Define the number of seconds per hour
    SECONDS_PER_HOUR_FACTOR = 3600

    # Define the kilo factor
    KILO_FACTOR = 1000

    # Constructor the drone with a given arguemnts
    def __init__(self, tareWeight: int, batterySize: float, loadingCapacity: int, initialBatteryCharge: float = None, powerPerKilogram: int = 150, maxSpeed: int = 10, batteryReserve: float = 0.1):
        # Check if the tareWeight is a positive integer and if not raise a ValueError
        if (tareWeight <= 0): raise ValueError('Invalid non-positive drone weight.')

        # Save the tareWeight [g]
        self.tareWeight = tareWeight

        # Check if the batterySize is a positive integer and if not raise a ValueError
        if (batterySize <= 0): raise ValueError('Invalid non-positive battery size.')
        
        # Save the batterySize [W/h]
        self.batterySize = batterySize

        # Check if the loadingCapacity is a positive integer and if not raise a ValueError
        if (loadingCapacity <= 0): raise ValueError('Invalid non-positive loading capacity.')

        # Save the loadingCapacity [g]
        self.loadingCapacity = loadingCapacity

        # Save the batterySize as the currentBatteryCharge [Wh]
        self.currentBatteryCharge = batterySize

        # Check if the initialBatteryCharge is a valid float and between zero and batterySize
        if isinstance(initialBatteryCharge, float) and (0 <= initialBatteryCharge <= batterySize):
            # Set the currentBatteryCharge from the paramater
            self.currentBatteryCharge = initialBatteryCharge

        # Save the powerPerKilogram [W]
        self.powerPerKilogram = powerPerKilogram

        # Save the maxSpeed [m/s]
        self.maxSpeed = maxSpeed

        # Save the batteryReserve [Wh]
        self.batteryReserve = (batterySize * batteryReserve)

    ################################################################################
    ############################### GETTER FUNCTIONS ###############################
    ################################################################################

    # Getter function for the tare weight [g]
    def getTareWeight(self) -> int:
        return self.tareWeight 

    # Getter function for the battery size [W/h]
    def getBatterySize(self) -> int:
        return self.batterySize
    
    # Getter function for the loading capacity [g]
    def getLoadingCapacity(self) -> int:
        return self.loadingCapacity

    # Getter function for the current battery charge [W/h]
    def getCurrentBatteryCharge(self, includeReserve: bool = False) -> int:
        # Check if the battery reserve should be included
        if includeReserve: return self.currentBatteryCharge
        
        # The current available battery charge minus the reserve
        return (self.currentBatteryCharge - self.batteryReserve)
    
    # Getter function for the power per kilogram [W]
    def getPowerPerKilogram(self) -> int:
        return self.powerPerKilogram
    
    # Getter function for the maximum speed [m/s]
    def getMaximumSpeed(self) -> int:
        return self.maxSpeed
    
    # Getter function for the battery reserve size [W/h]
    def getBatteryReserveSize(self) -> int:
        return self.batteryReserve

    ################################################################################
    ################################ DRONE FUNCTIONS ###############################
    ################################################################################

    # Calculate the remaining flight time [s]
    def getRemainingFlightTime(self) -> float:
        return (self.getCurrentBatteryCharge() / (((self.tareWeight + self.loadingCapacity) / self.KILO_FACTOR) * self.powerPerKilogram))
    
    # Calculate the remaining flight distance [m]
    def getRemainingFlightDistance(self) -> float:
        return self.maxSpeed * self.getRemainingFlightTime() * self.SECONDS_PER_HOUR_FACTOR
    
    # Calculate the flight time for a given distance in meters [s]
    def calculateFlightTime(self, distance: float) -> float:
        return distance / self.maxSpeed
