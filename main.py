import src.simulation.simulation as sim
from src.data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from src.simulation.parameters import *


from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_factory import WaypointFactory, WaypointAlgorithmEnum

prob_map_img = "img/probability_imgs/prob_map_5_multimodal_small.png"
prob_map = ProbabilityMap.fromPNG(prob_map_img)


#waypoints = WaypointFactory(WaypointAlgorithmEnum.LHC_GW_CONV_E, prob_map, Waypoint(25,-1), threaded=True).generate()
#waypoints = Waypoints([Waypoint(5,0), Waypoint(10, 0), Waypoint(10, 10),Waypoint(0, 10)])
waypoints = WaypointFactory(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER, prob_map, threaded = False, animate=False).generate() 

sim = sim.simulation(waypoints, animate=False)
vehicle = sim.run()

plt.figure()
img = prob_map.toIMG()
plt.imshow(img)
plt.plot(vehicle.data['pos']['x'], vehicle.data['pos']['y'], '-r')
plt.xlim(0,img.size[0])
plt.ylim(0,img.size[1])
plt.show()