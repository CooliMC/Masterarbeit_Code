import json

from geographiclib.polygonarea import PolygonArea
from geographiclib.geodesic import Geodesic

from assets.osm.District import District

def calcAreaByGeodesic(coordinates: [tuple] = []):
	# Create the PolygonArea with the Geodesic.WGS84
    polyArea = PolygonArea(Geodesic.WGS84, False)

    # Loop through the list of coordinates
    for coordinate in coordinates:
        # Add the coordinate to the Polygon
        polyArea.AddPoint(coordinate[0], coordinate[1])

    # Return absolute area of polygon in m2 as float
    return float(abs(polyArea.Compute(False, True)[2]))

def readJsonFile(path: str = ''):
    # Open the JSON-File in Read-Only Mode
    with open(path, 'r') as json_file:
        # Load the json and return the data
        return json.load(json_file)

def calcOsmNodeArea(node: dict):
    # TODO: Take relation, find closest ways/relation, take area of them and do median of all in 200 meter radius, if there are non return error
    return 0

def calcOsmWayArea(way: dict):
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
    return calcAreaByGeodesic(coordinates)

def calcOsmRelationArea(relation: dict):
    # Parameter for the sum of the member areas
    memberAreaSum = 0

    # Check for relevant parameters in the relation
    if 'members' and 'tags' not in relation:
        # Return the current sum
        return memberAreaSum

    # Check tags type of relation for polygon
    if relation['tags']['type'] != 'multipolygon':
        # Return the current sum
        return memberAreaSum

    # Loop through the members of the relation
    for members in relation['members']:
        # Add the calcOsmBuildingArea for the member
        memberAreaSum += calcOsmBuildingArea(members)

    # Return the member area sum
    return memberAreaSum

def calcOsmBuildingArea(building: dict):
    # Node with no boundary
    if building['type'] == 'node':
        # Calculate the area and return it
        return calcOsmNodeArea(building)
    # Way with polygon bounds
    if building['type'] == 'way':
        # Calculate the area and return it
        return calcOsmWayArea(building)
    # Relation with multiple ways
    if building['type'] == 'relation':
        # Calculate the area and return it
        return calcOsmRelationArea(building)

def main():
    # Load the json property data from the assets
    propertyData = readJsonFile('./assets/DataBS310.json')
    
    test = District(propertyData['elements'])
    print(test.buildings)

    return 0


    # Loop through the list of building elements
    for building in propertyData['elements']:
        print(type(building))

        # Calculate the area and add it to the properties
        building['area'] = calcOsmBuildingArea(building)
        if building['area'] == 0: print(building)
    
    #print(propertyData['elements'])


# Execute the main() function
main()