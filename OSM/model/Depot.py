from osm.Element import Element

class Depot(Element):
    # Define the class constructor
    def __init__(self, depotElement: dict):
        # Use the built in osmElement constructor
        super().__init__(depotElement)
    
    # Overwrite the string representation
    def __str__(self):
        return f'Depot(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Depot(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea}, levelCount={self.levelCount})'