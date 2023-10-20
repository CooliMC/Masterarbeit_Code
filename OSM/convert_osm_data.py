import json

from model.District import District
from simulation.Simulation import Simulation
from simulation.Event import Event

def readJsonFile(path: str = ''):
    # Open the JSON-File in Read-Only Mode
    with open(path, 'r') as json_file:
        # Load the json and return the data
        return json.load(json_file)
    
def writeJsonFile(path: str = '', content: str = ''):
    # Open the JSON-File in Read-Only Mode
    with open(path, 'w') as json_file:
        # Write the json string to the file
        json_file.write(content)

def main():
    # Load the json property data from the assets
    propertyData = readJsonFile('./assets/DataBS310.json')
    
    # Create a district with building from the data
    district = District(propertyData['elements'])

    print(district)
    print(district.getBuildingList()[151])
    print(district.mapResidentialsToBuildings()[:10])

    print(f'Distance between {district.getBuildingList()[151]} and {district.getBuildingList()[201]} is {district.getBuildingList()[151].getDistanceTo(district.getBuildingList()[201])}')
    print(f'Distance between {district.getBuildingList()[151]} and {district.getBuildingList()[201]} is {district.getBuildingList()[151].getDistanceTo(district.getBuildingList()[201].getCoordinates())}')
    print(f'Distance between {district.getBuildingList()[151]} and {district.getBuildingList()[201]} is {district.getBuildingList()[151].getDistanceTo((52.2618746, 10.5035718))}')

    # Create the Simulation with the district
    simulation = Simulation([district])

    ev = Event(lambda *x: print(f'{x[0]} + {x[1]} = {x[2]}'), [1, 4, 5])
    ev.executeFunction()

    print(f'Station Cluster: {simulation.calculateChargingStationCoordinates(10, True)}')

    for x in simulation.calculateChargingStationCoordinates(10):
        print('{ "type": "Feature", "properties": { "@id": "ChargingStation" }, "geometry": { "type": "Point", "coordinates": [' + f'{x[1]}, {x[0]}' + '] } },')

    return 0


# Execute the main() function
main()