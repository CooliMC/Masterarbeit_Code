# Import necesarry Modules
from osm.Element import Element
from .Building import Building
 
class District(Element):
    # Constructor of District, takes osm elements and converts them
    def __init__(self, osmElements: [dict]):
        # Filter the district elements from the osmElement list
        districtElements = Element.filterBoundaryElements(osmElements)

        # Check if there are multiple districts in the osmElement list and raise an error
        if len(districtElements) != 1: raise ValueError('No Boundary element found.')

        # Use the built in osmElement constructor
        super().__init__(districtElements[0])

        # Filter the buildings from the osmElements and convert them to building objects
        self.buildings = District.convertOsmDistrict(Element.filterBuildingElements(osmElements))

    # Get the list of district building elements
    def getBuildingList(self) -> [Building]:
        # Return the building list parameter
        return self.buildings

    # Overwrite the string representation
    def __str__(self):
        return f'District(id={self.sourceElement["id"]}, buildingCount={len(self.buildings)})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'District(id={self.sourceElement["id"]}, buildingCount={len(self.buildings)})'

    # Take a list of osm json elements and convert them to buildings
    @staticmethod
    def convertOsmDistrict(districtElements: [dict]) -> [Building]:
        # Createn an empty list for the converted buildings
        convertedBuildings = []

        # Loop through the list of district elements
        for element in districtElements:
            # Try to convert and append the osm element building
            try: convertedBuildings.append(Building(element))

            # Catch the exception and inform the user about the raised error
            except Exception as ex: print(f'Coversion of osm element failed: {ex}')
        
        # Return the list of converted buildings
        return convertedBuildings
    
    