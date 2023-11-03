from typing import Callable

class Event():
    # Constructor the Event with a given parameters
    def __init__(self, eventTime: int, eventFunction: Callable, eventParameters: []):
        # Save the eventTime for later sorting
        self.eventTime = eventTime
        
        # Save the eventFunction for later execution
        self.eventFunction = eventFunction

        # Save the eventParameters for the eventFunction execution
        self.eventParameters = eventParameters
    
    def getTime(self) -> int:
        # Resolve and return the timestamp
        return self.eventTime
    
    def getFunction(self) -> Callable:
        # Resolve and return the function
        return self.eventFunction
    
    def getParameters(self) -> []:
        # Resolve and return the parameters
        return self.eventParameters

    def executeFunction(self):
        # Execute the event function with the paramaters
        return self.eventFunction(*self.eventParameters)