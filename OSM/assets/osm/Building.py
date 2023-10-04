from .ElementUtils import ElementUtils

class Building():
    def __init__(self, buildingElement: dict):
        # Set the mandatory building parameters
        self.id = ElementUtils.getIdentifier(buildingElement)
        self.type = ElementUtils.getType(buildingElement)
        self.coordinates = ElementUtils.getGeographicCoordinates(buildingElement)
        self.baseArea = ElementUtils.getBaseArea(buildingElement)

        # Save the raw osm element for later use
        self.sourceElement = buildingElement
                
        
    # Overwrite the string representation
    def __str__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'
    

    

    