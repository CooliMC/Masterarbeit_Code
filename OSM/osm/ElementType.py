from enum import Enum

class ElementType(Enum):
    # Define common element types
    RELATION = ('R')
    WAY = ('W')
    NODE = ('N')

    # Constructor for setting custom parameter
    def __init__(self, abbreviation):
        # Set the type parameters
        self.abbreviation = abbreviation

    # Define a getByName function for conversion
    @staticmethod
    def from_str(label: str) -> 'ElementType':
        # Check if the element is a relation
        if label.upper() in ('R', 'RELATION'):
            # Return the relation enum type
            return ElementType.RELATION
        
        # Check if the element is a way
        if label.upper() in ('W', 'WAY'):
            # Return the way enum type
            return ElementType.WAY
        
        # Check if the element is a node
        if label.upper() in ('N', 'NODE'):
            # Return the node enum type
            return ElementType.NODE
        
        # If no match is found throw an error
        raise NotImplementedError
