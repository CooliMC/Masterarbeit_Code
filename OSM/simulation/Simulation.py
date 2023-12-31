from random import choices

from sklearn.cluster import KMeans

from model.Depot import Depot
from model.Building import Building
from model.District import District
from model.ChargingStation import ChargingStation

from .Event import Event
from .Drone import Drone
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, districtList: list[District], droneList: list[Drone], depot: Depot, chargingStations: int | list[ChargingStation], initialEvents: list[Event] = [], initialTime: int = 0):
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

    ################################################################################
    ############################### GETTER FUNCTIONS ###############################
    ################################################################################

    def getDistrictList(self) -> list[District]:
        # Return the districtList
        return self.districtList
    
    def getBuildingList(self) -> list[Building]:
        # Resolve the buildingList by flat mapping the district list with built-in functions
        return [building for district in self.getDistrictList() for building in district.getBuildingList()]

    def getBuildingPopulationList(self) -> list[tuple[Building, int]]:
        # Resolve the buildingPopulationList by flat mapping the district list with built-in functions
        return [buildingPopulation for district in self.getDistrictList() for buildingPopulation in district.mapResidentialsToBuildings()]

    def getDroneList(self) -> list[Drone]:
        # Return the droneList
        return self.droneList

    def getDepot(self) -> Depot:
        # Return the depot
        return self.depot

    def getChargingStationList(self) -> list[ChargingStation]:
        # Return the chargingStationList
        return self.chargingStationList

    def getEventList(self, sorted: bool = True) -> list[Event]:
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

    ################################################################################
    ############################# SIMULATION FUNCTIONS #############################
    ################################################################################

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

    ################################################################################
    ############################### HELPER FUNCTIONS ###############################
    ################################################################################

    def pickRandomBuildings(self, buildingCount: int, populationBased: bool = True) -> list [Building]:
        # Check if the selection criteria is not population based and just pick random buildings
        if not populationBased: return choices(self.getBuildingList(), k=buildingCount)

        # Use the built-in function to split the building population list into two
        buildingList, populationList = zip(*self.getBuildingPopulationList())

        # Use the extended built-in function to pick buildings on a inhabitant cound based probability
        return choices(buildingList, populationList, k=buildingCount)
        

    def calculateChargingStationCoordinates(self, stationCount: int, takeNearestNeighbor: bool = False) -> list[ChargingStation]:
        # Use the integrated python loops to get the flatMapped distric building coordinates
        buildingCoordinateList = [building.getCoordinates() for district 
            in self.districtList for building in district.getBuildingList()]

        # Create kMeans model with some adjusted parameters
        kmeans = KMeans(init="k-means++", n_clusters=stationCount,
            n_init=10, max_iter=500, random_state=1) #None) REMOVE THIS HERE REMOVE THIS HERE REMOVE THIS HERE REMOVE THIS HERE REMOVE THIS HERE REMOVE THIS HERE

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
            nearestStationNeighbor = min(mappedClusterDataList, key=lambda x: tempStationObject.getDistanceTo(x))

            # Create a charging station object with the station index and given coordinated as a simple node
            nearestNeighborList.append(ChargingStation.CreateFromAttributes(stationIndex + 1, 'node', nearestStationNeighbor))

        # Return the list of closest neighbors
        return nearestNeighborList

        

    
    
