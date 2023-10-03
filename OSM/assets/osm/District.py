# Import necesarry Modules
from .Building import Building
 
class District:
    # Constructor of District, takes osm elements and converts them
    def __init__(self, osmDistrictElements: [dict]):
        # Convert the osmDistritctElements to building objects and save them
        self.buildings = District.convertOsmDistrict(osmDistrictElements)
    
    # Take a list of osm json elements and convert them to buildings
    @staticmethod
    def convertOsmDistrict(districtElements: [dict]) -> [Building]:
        # Createn an empty list for the converted buildings
        convertedBuildings = []

        # Loop through the list of district elements
        for building in districtElements:
            # Try to convert the osm element into a building
            convertedBuilding = Building.convertOsmBuilding(building)
            
            # Check if the building could be converted
            if (convertedBuilding == None):
                # Continue with the next one
                continue
            
            # Add the building to the list of buildings
            convertedBuildings.append(convertedBuilding)
        
        # Return the list of converted buildings
        return convertedBuildings

    
    