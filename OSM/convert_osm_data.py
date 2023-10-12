import json

from model.District import District
from simulation.Simulation import Simulation

def readJsonFile(path: str = ''):
    # Open the JSON-File in Read-Only Mode
    with open(path, 'r') as json_file:
        # Load the json and return the data
        return json.load(json_file)

def main():
    # Load the json property data from the assets
    propertyData = readJsonFile('./assets/DataBS310.json')
    
    # Create a district with building from the data
    district = District(propertyData['elements'])

    print(district)
    print(district.getBuildingList()[151])

    print(district.mapResidentialsToBuildings()[:10])

    # Create the Simulation with the district
    simulation = Simulation(district)

    return 0


# Execute the main() function
main()