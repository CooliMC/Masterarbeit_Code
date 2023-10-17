from model.Building import Building
from model.District import District
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, districtList: [District]):
        # Save the districtList for later use
        self.districtList = districtList

        # Create empty event lists for the simulation
        self.bookedEventList = []
        self.conditionalEventList = []

        # Save the current time for the simulation
        self.currentTime = 0

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

        

        



    