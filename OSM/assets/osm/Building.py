from .ElementType import ElementType

class Building():
    def __init__(self, id: int, type: ElementType, sourceElement: dict = {}):
        # Set the building parameters
        self.id = id
        self.type = type
        self.sourceElement = sourceElement

        #
        self.latitude = latitude
        self.longitude = logitude
    

    # Overwrite the string representation
    def __str__(self):
        return f'Building(id={self.id}, type={self.type})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Building(id={self.id}, type={self.type})'

    # Take a the osm building element and convert it to a building
    @staticmethod
    def convertOsmBuilding(buildingElement: dict) -> 'Building':
        # Check if the element has a necesarry parameters
        if 'id' and 'type' not in buildingElement:
            # If not return None
            return None
        
        # Resolve the parameters and create the building
        return Building(
            id = buildingElement['id'],
            type = ElementType.from_str(buildingElement['type']),
            sourceElement = buildingElement
        )