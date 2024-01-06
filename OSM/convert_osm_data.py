import json
import time

from model.District import District
from model.Building import Building

from simulation.Simulation import Simulation
from simulation.Drone import Drone
from simulation.Order import Order

from solver.Solver import Solver
from solver.Solution import Solution

from geojson import FeatureCollection, Feature, Point, LineString

import plotly.express as px
import plotly.graph_objects as go


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
    #orderList = list(map(lambda x: Order(x), simulation.pickRandomBuildings(150))) # 350 is good medium
    orderList = list(map(lambda x: Order(x), simulation.getBuildingList()[0::299]))

    solver = Solver(droneList, depot, simulation.getChargingStationList(), orderList)

    print(f'---------------------------------------------------------------------------------------------------------------')

    start = time.time()
    initalSolution = solver.getInitialSolution()
    end = time.time()

    initalSolutionTourSum = sum(initalSolution.getDroneTourDistance(drone) for drone in initalSolution.getDroneList())
    initalSolutionTimeScore = initalSolution.getTimeScore()

    print(f'Calcualte the InitialSolution in {(end - start) * 1000} ms')
    print(f'Tour sum distance is {initalSolutionTourSum} m')
    print(f'Time score is {initalSolutionTimeScore} sec')

    print(f'---------------------------------------------------------------------------------------------------------------')

    start = time.time()
    localSearchSolution = solver.performLocalSearch(initalSolution)
    end = time.time()

    localSearchSolutionTourSum = sum(localSearchSolution.getDroneTourDistance(drone) for drone in localSearchSolution.getDroneList())
    localSearchSolutionTimeScore = localSearchSolution.getTimeScore()

    print(f'Calcualte the LocalSearch in {(end - start) * 1000} ms')
    print(f'Tour sum distance changed from {initalSolutionTourSum} m to {localSearchSolutionTourSum} m (Delta: {localSearchSolutionTourSum - initalSolutionTourSum} m)')
    print(f'Time score changed from {initalSolutionTimeScore} sec to {localSearchSolutionTimeScore} sec (Delta: {localSearchSolutionTimeScore - initalSolutionTimeScore} sec)')

    print(f'---------------------------------------------------------------------------------------------------------------')

    start = time.time()
    tabuSearchSolution = solver.performReactiveTabuSearch(localSearchSolution, 50, 5, 50000, 1.2, 2.0, 500, 250, 10)
    end = time.time()

    tabuSearchSolutionTourSum = sum(tabuSearchSolution.getDroneTourDistance(drone) for drone in tabuSearchSolution.getDroneList())
    tabuSearchSolutionTimeScore = tabuSearchSolution.getTimeScore()

    print(f'Calcualte the TabuSearchSolutions in {(end - start) * 1000} ms')
    print(f'Tour sum distance changed from {localSearchSolutionTourSum} m to {tabuSearchSolutionTourSum} m (Delta: {tabuSearchSolutionTourSum - localSearchSolutionTourSum} m)')
    print(f'Time score changed from {localSearchSolutionTimeScore} sec to {tabuSearchSolutionTimeScore} sec (Delta: {tabuSearchSolutionTimeScore - localSearchSolutionTimeScore} sec)')

    print(f'---------------------------------------------------------------------------------------------------------------')

    start = time.time()
    optimizedTabuSearchSolution = solver.performLocalSearch(tabuSearchSolution)
    end = time.time()

    optimizedTabuSearchSolutionTourSum = sum(optimizedTabuSearchSolution.getDroneTourDistance(drone) for drone in optimizedTabuSearchSolution.getDroneList())
    optimizedTabuSearchSolutionTimeScore = optimizedTabuSearchSolution.getTimeScore()

    print(f'Calcualte the OptimizedTabuSearchSolutions in {(end - start) * 1000} ms')
    print(f'Tour sum distance changed from {tabuSearchSolutionTourSum} m to {optimizedTabuSearchSolutionTourSum} m (Delta: {optimizedTabuSearchSolutionTourSum - tabuSearchSolutionTourSum} m)')
    print(f'Time score changed from {tabuSearchSolutionTimeScore} sec to {optimizedTabuSearchSolutionTimeScore} sec (Delta: {optimizedTabuSearchSolutionTimeScore - tabuSearchSolutionTimeScore} sec)')

    print(f'---------------------------------------------------------------------------------------------------------------')

    
    for drone, orders in optimizedTabuSearchSolution.getSolutionMatrix().items():
        print(f'-> Drone (milageAvailable={drone.getRemainingFlightDistance()}, tourDistance={optimizedTabuSearchSolution.getDroneTourDistance(drone)})')
        for order in orders:
            print(f'---> Order (destination={order.getDestination()})')

    print(f'---------------------------------------------------------------------------------------------------------------')

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
    
    # Print Initial Solution
    droneFlightFeatureList = []

    for drone, orders in initalSolution.getSolutionMatrix().items():
        droneFlightFeatureList.append(Feature(geometry=LineString(list(map(lambda x: x.getDestination().getCoordinates()[::-1], orders))), properties={ 'stroke': colorList[droneList.index(drone)], 'stroke-width': '3', 'stroke-opacity': 1 }))

    featureCollection = FeatureCollection([depotFeature] + chargingStationFeatureList + orderFeatureList + droneFlightFeatureList)

    print(featureCollection)

    print(f'---------------------------------------------------------------------------------------------------------------')

    # Print LocalSearch Solution
    droneFlightFeatureList = []

    for drone, orders in localSearchSolution.getSolutionMatrix().items():
        droneFlightFeatureList.append(Feature(geometry=LineString(list(map(lambda x: x.getDestination().getCoordinates()[::-1], orders))), properties={ 'stroke': colorList[droneList.index(drone)], 'stroke-width': '3', 'stroke-opacity': 1 }))

    featureCollection = FeatureCollection([depotFeature] + chargingStationFeatureList + orderFeatureList + droneFlightFeatureList)

    print(featureCollection)

    print(f'---------------------------------------------------------------------------------------------------------------')

    # Print TabuSearch Solution
    droneFlightFeatureList = []

    for drone, orders in tabuSearchSolution.getSolutionMatrix().items():
        droneFlightFeatureList.append(Feature(geometry=LineString(list(map(lambda x: x.getDestination().getCoordinates()[::-1], orders))), properties={ 'stroke': colorList[droneList.index(drone)], 'stroke-width': '3', 'stroke-opacity': 1 }))

    featureCollection = FeatureCollection([depotFeature] + chargingStationFeatureList + orderFeatureList + droneFlightFeatureList)

    print(featureCollection)

    print(f'---------------------------------------------------------------------------------------------------------------')

    # Print OptimizedTabuSearch Solution
    droneFlightFeatureList = []

    for drone, orders in optimizedTabuSearchSolution.getSolutionMatrix().items():
        droneFlightFeatureList.append(Feature(geometry=LineString(list(map(lambda x: x.getDestination().getCoordinates()[::-1], orders))), properties={ 'stroke': colorList[droneList.index(drone)], 'stroke-width': '3', 'stroke-opacity': 1 }))

    featureCollection = FeatureCollection([depotFeature] + chargingStationFeatureList + orderFeatureList + droneFlightFeatureList)

    print(featureCollection)

    print(f'---------------------------------------------------------------------------------------------------------------')

    return 0

    # Plot the feature collection on the map
    fig = go.Figure(
        go.Scattermapbox(),
        layout = {
            'mapbox': {
                'style': "stamen-terrain",
                'zoom': 10
            },
            'margin': {'l':0, 'r':0, 'b':0, 't':0},
            'mapbox_style': 'open-street-map',
        }
    )

    # Add the drone tours
    fig.update_mapboxes(layers=[
        {
            'source': feature,
            "sourcetype": "geojson",
            'type': "line", 
            'line': {
                'width': 3,
            },
            'below': "traces", 
            'color': feature.properties.get('stroke', 'royalblue'),
        } for feature in FeatureCollection(droneFlightFeatureList).features])
    
    # Add the depot marker
    fig.add_trace(
        go.Scattermapbox(
            mode='markers+text',
            lat=[depot.getCoordinates()[0]],
            lon=[depot.getCoordinates()[1]],
            marker={
                'symbol': 'circle',
                'size': 20,
                'color': 'purple',
                'allowoverlap': True
            },
            text = ["Depot"],
            textposition = "bottom right",
            showlegend=False
        )
    )

    # Add the charging station markers
    fig.add_trace(
        go.Scattermapbox(
            mode='markers+text',
            lat=[xy.getCoordinates()[0] for xy in relocateSol.getChargingStationList()],
            lon=[xy.getCoordinates()[1] for xy in relocateSol.getChargingStationList()],
            marker={
                'symbol': 'circle',
                'size': 15,
                'color': 'green',
                'allowoverlap': True
            },
            text = ["Charging Station" for xy in relocateSol.getChargingStationList()],
            textposition = "bottom right",
            showlegend=False
        )
    )

    # Add the order location markers
    fig.add_trace(
        go.Scattermapbox(
            mode='markers+text',
            lat=[xy.getDestination().getCoordinates()[0] for xy in relocateSol.getOrderList()],
            lon=[xy.getDestination().getCoordinates()[1] for xy in relocateSol.getOrderList()],
            marker={
                'symbol': 'circle',
                'size': 10,
                'color': 'yellow',
                'allowoverlap': True
            },
            text = ["Order" for xy in relocateSol.getOrderList()],
            textposition = "bottom right",
            showlegend=False
        )
    )

    

    #lats = [xy[1] for feature in featureCollection['features'] for xy in feature['geometry']['coordinates']]
    #lons = [xy[0] for feature in featureCollection['features'] for xy in feature['geometry']['coordinates']]

    center_lat = depot.getCoordinates()[0] #(min(lats) + max(lats)) / 2
    center_lon = depot.getCoordinates()[1] #(min(lons) + max(lons)) / 2
    
    fig.update_layout(
        mapbox = {
            'center': { 'lon':  center_lon, 'lat': center_lat}
        }
    )

    with open('./output/result.html', 'w') as f:
       f.write(fig.to_html())
       f.close()
    
    #image_io = fig.to_image(format="png", width=600, height=600)

    #Image(image_io)



    return 0


# Execute the main() function
main()