class Drone():
    # Constructor the drone with a given arguemnts
    def __init__(self, droneWeight: int, batterySize: float, loadingCapacity: int, initialBatteryCharge: float = None, powerPerKilogram: int = 150, maxSpeed: int = 10, batteryReserve: float = 0.1):
        # Check if the droneWeight is a positive integer and if not raise a ValueError
        if (droneWeight <= 0): raise ValueError('Invalid non-positive drone weight.')

        # Save the droneWeight [g]
        self.droneWeight = droneWeight

        # Check if the batterySize is a positive integer and if not raise a ValueError
        if (batterySize <= 0): raise ValueError('Invalid non-positive battery size.')
        
        # Save the batterySize [w/h]
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

        # Save the powerPerKilogram [W/kg]
        self.powerPerKilogram = powerPerKilogram

        # Save the maxSpeed [m/s]
        self.maxSpeed = maxSpeed

        # Save the batteryReserve [Wh]
        self.batteryReserve = (batterySize * batteryReserve)
        

    # Getter function for the battery size [w/h]
    def getBatterySize(self) -> int:
        return self.batterySize
    
    # Getter function for the loading capacity [g]
    def getLoadingCapacity(self) -> int:
        return self.loadingCapacity

    # Getter function for the current battery charge [w/h]
    def getCurrentBatteryCharge(self) -> int:
        return self.currentBatteryCharge

    # Calculate the remaining flight time [h]
    def getRemainingFlightTime(self) -> float:
        return ((self.currentBatteryCharge - self.batteryReserve) / (((self.droneWeight + self.loadingCapacity) / 1000) * self.powerPerKilogram))
    
    # Calculate the remaining flight distance [m]
    def getRemainingFlightDistance(self) -> float:
        return self.maxSpeed * self.getRemainingFlightTime() * 3600