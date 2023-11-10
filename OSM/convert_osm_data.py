import json
import random

from model.District import District
from model.Building import Building

from simulation.Simulation import Simulation
from simulation.Drone import Drone
from simulation.Order import Order

from solver.Solver import Solver

from geojson import FeatureCollection, Feature, Point, LineString

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
    propertyDataBS111 = readJsonFile('./assets/DataBS111.json')
    propertyDataBS112 = readJsonFile('./assets/DataBS112.json')
    propertyDataBS120 = readJsonFile('./assets/DataBS120.json')
    propertyDataBS130 = readJsonFile('./assets/DataBS130.json')
    propertyDataBS211 = readJsonFile('./assets/DataBS211.json')
    propertyDataBS212 = readJsonFile('./assets/DataBS212.json')
    propertyDataBS221 = readJsonFile('./assets/DataBS221.json')
    propertyDataBS222 = readJsonFile('./assets/DataBS222.json')
    propertyDataBS310 = readJsonFile('./assets/DataBS310.json')
    propertyDataBS321 = readJsonFile('./assets/DataBS321.json')
    propertyDataBS322 = readJsonFile('./assets/DataBS322.json')
    propertyDataBS330 = readJsonFile('./assets/DataBS330.json')
    
    # Create a list of district with building from the data
    districtList = [
        District(propertyDataBS111['elements']),
        District(propertyDataBS112['elements']),
        District(propertyDataBS120['elements']),
        District(propertyDataBS130['elements']),
        District(propertyDataBS211['elements']),
        District(propertyDataBS212['elements']),
        District(propertyDataBS221['elements']),
        District(propertyDataBS222['elements']),
        District(propertyDataBS310['elements']),
        District(propertyDataBS321['elements']),
        District(propertyDataBS322['elements']),
        District(propertyDataBS330['elements'])
    ]

    depot = Building.CreateFromAttributes(
        1, 'node', (52.2607922, 10.5045533)
    )

    # Create a fleet of drones for the simulation
    droneList = [
        Drone(500, 200, 1000),
        Drone(500, 200, 1000),
        Drone(500, 200, 1000),
        Drone(500, 200, 1000),
        Drone(500, 200, 1000),
    ]

    # Create the Simulation with the district
    simulation = Simulation(districtList, droneList, depot, 15)
    
    # Create random orders for buildings in the district
    orderList = list(map(lambda x: Order(x), simulation.pickRandomBuildings(350)))

    solver = Solver(droneList, depot, simulation.getChargingStationList(), orderList)

    t = solver.generateInitialSolution()

    # Solution output
    print(f'InitialSolution ResponseCode={t}')
    print(f'InitialSolution:')
    for drone, orders in solver.solutionMatrix.items():
        print(f'-> Drone (milageAvailable={drone.getRemainingFlightDistance()})')
        for order in orders:
            print(f'---> Order (destination={order[0].getDestination()}, currentMilage={order[1]})')
    

    # GeoJSON Visualisation
    depotFeature = Feature(geometry=Point(depot.getCoordinates()[::-1]), properties={ 
        'description': 'Depot', 
        'marker-color': '#D914B8', 
        'marker-size': 'large', 
        'marker-symbol': 'warehouse' 
    })

    chargingStationFeatureList = list(map(lambda x: Feature(geometry=Point(x.getCoordinates()[::-1]), properties={ 
        'description': 'Charging Station',
        'marker-color': '#217016',
        'marker-size': 'large', 
        'marker-symbol': 'fuel'
    }), simulation.getChargingStationList()))

    orderFeatureList = list(map(lambda x: Feature(geometry=Point(x.getDestination().getCoordinates()[::-1]), properties={ 
        'description': ''.join((x.getDestination().getSourceElement()['tags']['addr:street'] + ' ' + x.getDestination().getSourceElement()['tags'].get('addr:housenumber', 'N/A')).splitlines()),
        'marker-color': 'FAFAFA',
        'marker-size': 'small', 
        'marker-symbol': 'building'
    }), orderList))

    colorList = [ 'red', 'green', 'blue', 'orange', 'black' ]
    droneFlightFeatureList = []

    for drone, orders in solver.solutionMatrix.items():
        droneFlightFeatureList.append(Feature(geometry=LineString(list(map(lambda x: x[0].getDestination().getCoordinates()[::-1], orders))), properties={ 'stroke': colorList[droneList.index(drone)], 'stroke-width': '3', 'stroke-opacity': 1 }))

    featureCollection = FeatureCollection([depotFeature] + chargingStationFeatureList + orderFeatureList + droneFlightFeatureList)

    print(featureCollection)


    return 0


# Execute the main() function
main()