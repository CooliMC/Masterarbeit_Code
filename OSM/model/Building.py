from osm.Element import Element

class Building(Element):
    # Define the class constants
    BASE_TO_LIVING_AREA_FACTOR = 0.8

    # Define the class constructor
    def __init__(self, buildingElement: dict):
        # Use the built in osmElement constructor
        super().__init__(buildingElement)

    def getLivingSpace(self, fallbackBaseArea: float = None) -> float:
        # Resolve the baseArea and levelCount
        tBaseArea = self.getBaseArea()
        tLevelCount = self.getLevelCount()

        # Check if the area is zero and fallback is defined
        if ((tBaseArea == 0) and (fallbackBaseArea != None)):
            # Use the fallback for the area
            tBaseArea = fallbackBaseArea

        # Calculate the living space with the baseArea, levelCount and baseToLivingAreaFactor
        return round(tBaseArea * float(tLevelCount) * Building.BASE_TO_LIVING_AREA_FACTOR, 2)
    
    # Overwrite the string representation
    def __str__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount}, livingSpace={self.getLivingSpace()})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount}, livingSpace={self.getLivingSpace()})'