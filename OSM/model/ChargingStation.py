from osm.Element import Element

class ChargingStation(Element):
    # Define the class constructor
    def __init__(self, chargingStationElement: dict):
        # Use the built in osmElement constructor
        super().__init__(chargingStationElement)
    
    # Overwrite the string representation
    def __str__(self):
        return f'Charging Station(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Charging Station(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount})'