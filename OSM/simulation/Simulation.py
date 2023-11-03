from sklearn.cluster import KMeans

from model.Building import Building
from model.District import District

from .Event import Event
from .Drone import Drone
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, districtList: [District], droneList: [Drone], depot: 'Building | (float, float)', chargingStations: 'int | [(float, float)]', initialEvents: Event = [], initialTime: int = 0):
        # Save the districtList for later use
        self.districtList = districtList

        # Save the droneList for later use
        self.droneList = droneList

        # Check if the depot is no building:
        if not isinstance(depot, Building):
            # Create the depot as a building from the given coordinates
            depot = Building.CreateFromAttributes(1, 'node', depot)

        # Save the depot for later use
        self.depot = depot

        # Check if the chargingStations is a valid int
        if isinstance(chargingStations, int):
            # Calculate the list of charging station coordinates and take the parameter as the count
            chargingStations = self.calculateChargingStationCoordinates(chargingStations, True)

        # Save the chargingStationList for later use
        self.chargingStationList = chargingStations

        # Create empty event lists for the simulation
        self.eventList = initialEvents

        # Save the current time for the simulation
        self.currentTime = initialTime

    def getEventList(self, sorted: bool = True) -> [Event]:
        # Check and sort the list if necesarry
        if (sorted == True): self.sortEventList()
    
        # Return the eventList
        return self.eventList

    def getCurrentTime(self) -> int:
        # Return the currentTime
        return self.currentTime
    
    def sortEventList(self) -> None:
        # Sort the event list by the timestamp of each event
        self.eventList.sort(key=lambda x: x.getTime(), reverse=False)

    def jumpToNextEvent(self) -> bool:
        # Resolve the sorted event list
        sortedEventList = self.getEventList(True)

        # Check if there is a nextEvent in the list
        if not sortedEventList: return False

        # Remove and get the next event from the sorted list
        nextEvent = sortedEventList.pop(0)

        # Update the current time to the event time
        self.currentTime = nextEvent.getTime()

        # Execute the event function
        nextEvent.executeFunction()

        # Successfully executed next event
        return True

    def calculateChargingStationCoordinates(self, stationCount: int, takeNearestNeighbor: bool = False) -> [(float, float)]:
        # Use the integrated python loops to get the flatMapped distric building coordinates
        buildingCoordinateList = [building.getCoordinates() for district 
            in self.districtList for building in district.getBuildingList()]

        # Create kMeans model with some adjusted parameters
        kmeans = KMeans(init="k-means++", n_clusters=stationCount,
            n_init=10, max_iter=500, random_state=None)

        # Fit the building coordinate list into the model
        kmeans.fit(buildingCoordinateList)

        # Convert the list of cluster centers to charging station location coordinates for further compution
        chargingStationLocationList = list(map(lambda x: (round(x[0], 7), round(x[1], 7)), kmeans.cluster_centers_))

        # Check if the positions need to be mapped on the nearest neighbor
        if not takeNearestNeighbor: return chargingStationLocationList

        # List of nearest neighbors
        nearestNeighborList = []

        # Loop over the station per index
        for stationIndex in range(stationCount):
            # Create a simple Building for the station to measure distances by using the center charging station location
            tempStationObject = Building.CreateFromAttributes(1, 'node', chargingStationLocationList[stationIndex])

            # Loop over the list of labels per index, filter all index entries that are in the current cluster and resolve the corresponding data
            mappedClusterDataList = [ buildingCoordinateList[idx] for idx, clu_num in enumerate(kmeans.labels_.tolist()) if clu_num == stationIndex ]

            # Use the min function on the clusterDataList to finde the geographically clostest building for each charging station
            nearestNeighborList.append(min(mappedClusterDataList, key=lambda x: tempStationObject.getDistanceTo(x)))

        # Return the list of closest neighbors
        return nearestNeighborList

        

    
    
