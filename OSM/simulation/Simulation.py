from model.Building import Building
from model.District import District
 
class Simulation():
    # Constructor the simulation with a given district
    def __init__(self, district: District):
        # Save the district for later use
        self.district = district