from sklearn.cluster import KMeans

from model.Building import Building
from model.District import District

from .Event import Event
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, districtList: [District], initialBookedEvents: Event = [], initialConditionalEvents: Event = []):
        # Save the districtList for later use
        self.districtList = districtList

        # Create empty event lists for the simulation
        self.bookedEventList = initialBookedEvents
        self.conditionalEventList = initialConditionalEvents

        # Save the current time for the simulation
        self.currentTime = 0

    def getBookedEventList(self, sorted: bool = True) -> [Event]:
        # Check if the list should be sorted by default
        if not sorted: return self.bookedEventList

        # Sort the booked event list by the timestamp and return the sorted list
        return self.bookedEventList.sort(key=lambda x: x['timestamp'], reverse=False)

    def getConditionalEventList(self) -> [Event]:
        # Resolve and return the condfitional event list
        return self.conditionalEventList
    
    def getCurrentTime(self) -> int:
        # Resolv and return the current time
        return self.currentTime

    def jumpToNextEvent(self):
        # Sort the bookedEventList by the timestamp to get the next event
        sortedBookedEvents = self.bookedEventList.sort(key=lambda x: x['timestamp'], reverse=False)

        # Set the currentTime to the timestamp of the next event
        self.currentTime = nextBookedEvent[0]['timestamp']

        # Loop over the list and execute all events with the current timestamp
        while (self.currentTime == sortedBookedEvents[0]['timestamp']):
            # Resolve the next event from the sorted booked events list
            nextBookedEvent = sortedBookedEvents.pop(0)

            # Execute the event function with the given event parameters
            nextBookedEvent['function'](*nextBookedEvent['parameters'])

        # Loop over the conditional event list to execute all events
        while (True):
            # Flag for event execution
            executedEvent = False

            # Loop over the configtional event list
            for conditionalEvent in self.conditionalEventList:
                # Check if the condition of the event is met
                if conditionalEvent['condition']():
                    # Remove the event from the list
                    self.conditionalEventList.remove(conditionalEvent)

                    # Execute the event function with the given event parameter
                    conditionalEvent['function'](*conditionalEvent['parameters'])

                    # Mark the executed event parameter
                    executedEvent = True

            # Check if at least one event was executed
            if not executedEvent: break

    def calculateChargingStationLocations(self, stationCount: int) -> [(float, float)]:
        # Use the integrated python loops to get the flatMapped distric building coordinates
        buildingCoordinateList = [building.getCoordinates() for district 
            in self.districtList for building in district.getBuildingList()]

        # Create kMeans model with some adjusted parameters
        kmeans = KMeans(init="k-means++", n_clusters=stationCount,
            n_init=10, max_iter=500, random_state=None)

        # Fit the building coordinate list into the model
        kmeans.fit(buildingCoordinateList)

        # Return the converted list of cluster centers as charging station locations coordinates
        return list(map(lambda x: (round(x[0], 7), round(x[1], 7)), kmeans.cluster_centers_))

        



    