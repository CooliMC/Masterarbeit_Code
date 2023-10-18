import json

from model.District import District
from simulation.Simulation import Simulation

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

    # Create the Simulation with the district
    simulation = Simulation([district])

    print(f'Station Cluster: {simulation.calculateChargingStationLocations(10)}')

    for x in simulation.calculateChargingStationLocations(10):
        print('{ "type": "Feature", "properties": { "@id": "ChargingStation" }, "geometry": { "type": "Point", "coordinates": [' + f'{x[1]}, {x[0]}' + '] } },')

    return 0


# Execute the main() function
main()