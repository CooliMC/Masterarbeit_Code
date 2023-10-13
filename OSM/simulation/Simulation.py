from model.Building import Building
from model.District import District
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, districtList: [District]):
        # Save the districtList for later use
        self.districtList = districtList

    