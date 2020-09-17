import simulation.simulation
from data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation

waypoints = Waypoints([Waypoint(5,0), Waypoint(10, 0), Waypoint(10, 10),Waypoint(0, 10)])

sim = simulation.simulation.simulation(waypoints)
vehicle = sim.run()

plt.figure(2)
plt.plot(vehicle.data['pos']['y'], vehicle.data['pos']['x'], '-r')
plt.show()