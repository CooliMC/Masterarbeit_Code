from osm.Element import Element

class Building(Element):
    def __init__(self, buildingElement: dict):
        # Use the built in osmElement constructor
        super().__init__(buildingElement)
    
    # Overwrite the string representation
    def __str__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Building(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'
    

    

    