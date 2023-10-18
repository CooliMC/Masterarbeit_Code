from typing import Callable

class Event():
    # Constructor the Event with a given parameters
    def __init__(self, eventFunction: Callable, eventParameters: []):
        # Save the eventFunction for later execution
        self.eventFunction = eventFunction

        # Save the eventParameters for the eventFunction execution
        self.eventParameters = eventParameters

    def executeFunction(self):
        # Execute the event function with the paramaters
        self.eventFunction(*self.eventParameters)