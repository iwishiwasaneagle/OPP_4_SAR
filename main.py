import simulation.simulation
from data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation

waypoints = Waypoints(Waypoint(5,0,0), Waypoint(10, 0, 0), Waypoint(10, 10, 0),Waypoint(0, 10, 0))

sim = simulation.simulation.simulation(waypoints)
vehicle = sim.run()