from .ElementType import ElementType

from geographiclib.polygonarea import PolygonArea
from geographiclib.geodesic import Geodesic

class Element():
    def __init__(self, osmElement: dict):
        # Set the mandatory element parameters
        self.id = Element.getIdentifier(osmElement)
        self.type = Element.getType(osmElement)
        self.coordinates = Element.getGeographicCoordinates(osmElement)
        self.baseArea = Element.getBaseArea(osmElement)

        # Save the raw osmElement for further use
        self.sourceElement = osmElement

    # Getter function for the building identifier
    def getIdentifier(self) -> int:
        return self.id

    # Getter function for the building elementType
    def getType(self) -> ElementType:
        return self.type

    # Getter function for the building coordinates
    def getCoordinates(self) -> tuple:
        return self.coordinates
    
    # Getter function for the building baseArea
    def getBaseArea(self) -> float:
        return self.baseArea
    
    # Getter function for the building sourceElement
    def getSourceElement(self) -> dict:
        return self.sourceElement
    
    # Overwrite the string representation
    def __str__(self):
        return f'Element(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'
    
    # Overwrite the class representation
    def __repr__(self):
        return f'Element(id={self.id}, type={self.type}, coordinates={self.coordinates}, baseArea={self.baseArea})'

    #################################################################
    #################### Public Static Functions ####################
    #################################################################

    # Utils function to extract the id from the osmElement
    @staticmethod
    def getIdentifier(osmElement: dict) -> tuple:
        # Check for mandatory id property
        if 'id' not in osmElement:
            # If the manadatory property is missing, raise a ValueError
            raise ValueError("Madatory paramater 'id' is missing.")
        
        # Resolve and return the id
        return osmElement['id']

    # Utils function to extract the type from the osmElement
    @staticmethod
    def getType(osmElement: dict) -> tuple:
        # Check for mandatory type property
        if 'type' not in osmElement:
            # If the manadatory property is missing, raise a ValueError
            raise ValueError("Madatory paramater 'type' is missing.")
        
        # Try to resolve the type by its string represenation
        return ElementType.from_str(osmElement['type'])

    # Utils function to extract coordinates (lon/lat) from the osmElement
    @staticmethod
    def getGeographicCoordinates(osmElement: dict) -> tuple:
        # Check for direct longitude/latitude coordinate properties
        if (('lon' in osmElement) and ('lat' in osmElement)):
            # Extract the longitude/latitude directly from the element properies
            return (osmElement['lon'], osmElement['lat'])
        
        # Check for indirect bounds to calc the coordinates
        if ('bounds' in osmElement):
            # Extract the bounds property from the element
            buildingBounds = osmElement['bounds']

            # Calculate the avg longitude and latitude by their min/max values
            buildingLon = round((buildingBounds['minlon'] + buildingBounds['maxlon']) / 2, 7)
            buildingLat = round((buildingBounds['minlat'] + buildingBounds['maxlat']) / 2, 7)

            # Set the calculated values as the coordinates
            return (buildingLon, buildingLat)
        
        # Check for converted element with geometry properties
        if ('geometry' in osmElement):
            # Extract the geometry coordinates property from the element
            buildingCoordinates = osmElement['geometry']['coordinates']

            # Set the coordinates from the converted geometry coordinates
            return (buildingCoordinates[0], buildingCoordinates[1])
        
        # No coordinate based properties found, raise a value error with a dedicated message
        raise ValueError('Coordinate parameters (lat/lon, bounds, geometry) are missing.')
    
    # Utils function to get the base area of the osmElement
    @staticmethod
    def getBaseArea(osmElement: dict) -> float:
        # Node with no boundary
        if osmElement['type'] == 'node':
            # Calculate the area and return it
            return Element.__getNodeBaseArea(osmElement)
        # Way with polygon bounds
        if osmElement['type'] == 'way':
            # Calculate the area and return it
            return Element.__getWayBaseArea(osmElement)
        # Relation with multiple ways
        if osmElement['type'] == 'relation':
            # Calculate the area and return it
            return Element.__getRelationBaseArea(osmElement)

    # Utils function to check for a given tag in the osmElement
    @staticmethod
    def hasTag(osmElement: dict, tagKey: str) -> bool:
        # Check if the object has a tags key and check there for key
        return (('tags' in osmElement) and (tagKey in osmElement['tags']))

    # Utils function to check if the given osmElement is a boundary
    @staticmethod
    def isBoundary(osmElement: dict) -> bool:
        # Check if the osmElement is a Relation
        if Element.getType(osmElement) != ElementType.RELATION:
            # No Boundary relation
            return False
        
        # Check if the osmElement has a type tag
        if not Element.hasTag(osmElement, 'type'):
            # No Boundary type tag
            return False
        
        # Check if the osmElement tag type is a boundary
        return osmElement['tags']['type'] == 'boundary'
    
    # Function to filter boundary elements for a list of osmElements
    @staticmethod
    def filterBoundaryElements(osmElements: [dict]) -> [dict]:
        # Use the built in filter and Element isDistrict function
        return list(filter(Element.isBoundary, osmElements))
    
    # Function to filter district elements for a list of osmElements
    @staticmethod
    def filterBuildingElements(osmElements: [dict]) -> [dict]:
        # Use the built in filter and Element isDistrict function
        return list(filter(lambda x: not Element.isBoundary(x), osmElements))


    #################################################################
    #################### Private Static Functions ###################
    #################################################################

    # Utils function to get the base area of the osmNodeElement
    @staticmethod   
    def __getNodeBaseArea(node: dict) -> float:
        # TODO: Take relation, find closest ways/relation, take area of them and do median of all in 200 meter radius, if there are non return error
        return 0

    # Utils function to get the base area of the osmWayElement
    @staticmethod
    def __getWayBaseArea(way: dict) -> float:
        # Check for geometry attribute
        if 'geometry' not in way:
            # Return 0 m2
            return 0
        
        # Empty arry for coordinates
        coordinates = []
            
        # Loop through the coordinates
        for coord in way['geometry']:
            # Add the converted coordinate type as a new point
            coordinates.append((coord['lat'], coord['lon']))

        # Use the coordinates to calculate the area
        return Element.__calcAreaByGeodesic(coordinates)

    # Utils function to get the base area of the osmRelationElement
    @staticmethod
    def __getRelationBaseArea(relation: dict) -> float:
        # Parameter for the sum of the member areas
        memberAreaSum = 0

        # Check for relevant parameters in the relation
        if (('members' not in relation) and ('tags' not in relation)):
            # Return the current sum
            return memberAreaSum

        # Check tags type of relation for polygon
        if relation['tags']['type'] != 'multipolygon':
            # Return the current sum
            return memberAreaSum

        # Loop through the members of the relation
        for members in relation['members']:
            # Add the getBaseArea for the member
            memberAreaSum += Element.getBaseArea(members)

        # Return the member area sum
        return memberAreaSum
    
    # Utils function to calculate a geodesic area by coordinates
    @staticmethod
    def __calcAreaByGeodesic(coordinates: [tuple] = []) -> float:
        # Create the PolygonArea with the Geodesic.WGS84
        polyArea = PolygonArea(Geodesic.WGS84, False)

        # Loop through the list of coordinates
        for coordinate in coordinates:
            # Add the coordinate to the Polygon
            polyArea.AddPoint(coordinate[0], coordinate[1])

        # Return absolute area of polygon in m2 as float
        return round(float(abs(polyArea.Compute(False, True)[2])), 2)