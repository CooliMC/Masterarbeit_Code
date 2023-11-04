import json
import random

from model.District import District
from model.Building import Building

from simulation.Simulation import Simulation
from simulation.Drone import Drone
from simulation.Order import Order

from solver.Solver import Solver

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
    propertyDataBS310 = readJsonFile('./assets/DataBS310.json')
    
    # Create a list of district with building from the data
    districtList = [
        District(propertyDataBS310['elements'])
    ]

    depot = Building.CreateFromAttributes(
        1, 'node', (52.2607922, 10.5045533)
    )

    # Create a fleet of drones for the simulation
    droneList = [
        Drone(500, 150, 1000),
        Drone(500, 150, 1000),
        Drone(500, 150, 1000),
        Drone(500, 150, 1000),
        Drone(500, 150, 1000),
    ]

    # Create the Simulation with the district
    simulation = Simulation(districtList, droneList, depot, 10)
    
    # Create 50 random orders for buildings in the district
    orderList = list(map(lambda x: Order(x), random.choices(districtList[0].getBuildingList(), k=500)))

    solver = Solver(droneList, depot, simulation.getChargingStationList(), orderList)

    t = solver.generateInitialSolution()

    print(f'InitialSolution ResponseCode={t}')
    print(f'InitialSolution:')
    for drone, orders  in solver.solutionMatrix.items():
        print(f'-> Drone (milageAvailable={drone.getRemainingFlightDistance()})')
        for order in orders:
            print(f'---> Order (destination={order[0].getDestination()}, currentMilage={order[1]})')
    

    return 0


# Execute the main() function
main()