# Import necesarry Modules
from osm.Element import Element
from .Building import Building
 
class District(Element):
    # Constructor of District, takes osm elements and converts them
    def __init__(self, osmElements: [dict]):
        # Filter the district elements from the osmElement list
        districtElements = Element.FilterBoundaryElements(osmElements)

        # Check if there are multiple districts in the osmElement list and raise an error
        if len(districtElements) != 1: raise ValueError('No Boundary element found.')

        # Use the built in osmElement constructor
        super().__init__(districtElements[0])

        # Filter the buildings from the osmElements and convert them to building objects
        self.buildings = District.ConvertOsmDistrict(Element.FilterBuildingElements(osmElements))

        # Set the optional district element parameters
        self.name = District.GetName(self.sourceElement)
        self.population = District.GetPopulation(self.sourceElement)

    # Get the district element name
    def getName(self) -> str:
        # Return the district name parameter
        return self.name
    
    # Get the district element population
    def getPopulation(self) -> int:
        # Return the district population parameter
        return self.population
    
    # Get the list of district building elements
    def getBuildingList(self) -> [Building]:
        # Return the building list parameter
        return self.buildings

    # Get the number of district building elements
    def getBuildingCount(self, excludeNoBaseArea: bool = False) -> int:
        # Check if node filtering not necesarry and return the length
        if not excludeNoBaseArea: return len(self.buildings)

        # Filter all the element without a baseArea and count the list of element
        return len(list(filter(lambda x: x.getBaseArea() != 0, self.buildings)))

    def getLivingSpace(self, fallbackBuildingBaseArea: float = None) -> float:
        # Check if the fallbackBuildingBaseArea is set
        if (fallbackBuildingBaseArea is None):
            # Fallback to the built-in getAvarageBuildingBaseArea function
            fallbackBuildingBaseArea = self.getAvarageBuildingBaseArea(True)

        # Sum up the living space of all buildings in the area with a given fallback and return the area
        return round(sum(building.getLivingSpace(fallbackBuildingBaseArea) for building in self.buildings), 2)

    # Get the avarage baseArea of the district buildings
    def getAvarageBuildingBaseArea(self, excludeNoBaseArea: bool = True) -> float:
        # Parameter to hold the baseAreaSum and buildingCounter
        baseAreaSum = buildingCounter = 0
        
        # Loop through the list of district building
        for building in self.buildings:
            # Check if the building has a base area and excludeNoBaseArea
            if ((building.getBaseArea() != 0) or (not excludeNoBaseArea)):
                # Addd the building baseArea to the sum
                baseAreaSum += building.getBaseArea()

                # Increase the count of added buildings
                buildingCounter += 1
        
        # Calculate the avarage baseArea of the district
        return round(baseAreaSum / buildingCounter, 2)
    
    # Get the avarage livingSpace of the district buildings
    def getAvarageBuildingLivingSpace(self, fallbackBuildingBaseArea: float = None) -> float:
        # Use the already implemented functions to calculate the avarage living space of district buildings
        return round(self.getLivingSpace(fallbackBuildingBaseArea) / self.getBuildingCount(False), 2)

    def getAvarageResidentLivingSpace(self, fallbackBuildingBaseArea: float = None) -> float:
        # Use the already implemented functions to calculate the avarage living space of district residents
        return round(self.getLivingSpace(fallbackBuildingBaseArea) / self.getPopulation(), 2)

    # Overwrite the string representation
    def __str__(self):
        return f'District(id={self.sourceElement["id"]}, name={self.name}, population={self.population}, buildingCount={self.getBuildingCount()}, livingSpace={self.getLivingSpace()}, avarageBuildingBaseArea={self.getAvarageBuildingBaseArea()}, avarageBuildingLivingSpace={self.getAvarageBuildingLivingSpace()}, avarageResidentLivingSpace={self.getAvarageResidentLivingSpace()})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'District(id={self.sourceElement["id"]}, name={self.name}, population={self.population}, buildingCount={self.getBuildingCount()}, livingSpace={self.getLivingSpace()}, avarageBuildingBaseArea={self.getAvarageBuildingBaseArea()}), avarageBuildingLivingSpace={self.getAvarageBuildingLivingSpace()}, avarageResidentLivingSpace={self.getAvarageResidentLivingSpace()})'

    #################################################################
    #################### Public Static Functions ####################
    #################################################################

    # Utils function to get the name of the osm element tags
    @staticmethod
    def GetName(districtElement: dict) -> str:
        # Check if the district element has a name tag
        if District.HasTag(districtElement, 'name'):
            # Resolve and return the elements name tage
            return districtElement['tags']['name']
        
        # Return a default fallback
        return 'N/A'
    
    # Utils function to get the name of the osm element tags
    @staticmethod
    def GetPopulation(districtElement: dict) -> int:
        # Check if the district element has a population tag
        if District.HasTag(districtElement, 'population'):
            # Resolve and return the elements population tage
            try: return int(districtElement['tags']['population'])

            # Except a ValueError and print out a message to explain the error
            except ValueError: print("District tag 'population' is no valid number.")
        
        # Return a default fallback
        return 0

    # Utils function convert osm elements into buildings
    @staticmethod
    def ConvertOsmDistrict(districtElements: [dict]) -> [Building]:
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
    