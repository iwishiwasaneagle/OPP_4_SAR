import src.simulation.simulation as sim
from src.data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from src.simulation.parameters import *


from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_factory import WaypointFactory, WaypointAlgorithmEnum

prob_map_img = "img/probability_imgs/prob_map_2.png"
#prob_map_img = "img/probability_imgs/prob_map_6_multimodal_tiny.png"
prob_map = ProbabilityMap.fromPNG(prob_map_img)


#waypoints = WaypointFactory(WaypointAlgorithmEnum.LHC_GW_CONV_E, prob_map, Waypoint(0,0),threaded=True,animate=False).generate()
#waypoints = Waypoints([Waypoint(5,0), Waypoint(10, 0), Waypoint(10, 10),Waypoint(0, 10)])
#waypoints = WaypointFactory(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER, prob_map, threaded = False, animate=False).generate()


import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as sco

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints
wps = 10
lower_1,lower_2 = 0,0
upper_1,upper_2 = 50,50

b = 25 # sweep width

def cost_func(x:np.array) -> float:
    x = np.reshape(x,(wps,2))
    
    x_old = x[0]    
    cost = 0
    for x_cur in x[1:]:
        
        y = lambda i:  i*((x_cur[1]-x_old[1])/(x_cur[0]-x_old[0])) - x_old[0] + x_old[1]
        
        x_test = np.arange(x_old[0],x_cur[0])
        y_test = y(x_test)
        
        x_test = set(np.round(x_test,0))
        y_test = set(np.round(y_test,0))
        
        for i,j in zip(x_test,y_test):
            cost -= prob_map[i,j]

        #cost +=  0.5*np.linalg.norm([x_old, x_cur])    
            
        x_old = x_cur
            
    return cost

x0 = [(25+25*np.cos(theta), 25+25*np.sin(theta)) for theta in np.arange(0,2*np.pi,2*np.pi/wps)]
x0 = np.reshape(x0,np.shape(x0)[0]*np.shape(x0)[1])

print("Started optimisation")
res = sco.minimize(cost_func,x0,options={'disp': True})
print("Finished optimisation")
print(res)
min_x = np.reshape(res.x,(wps,2))

waypoints = []
for wp in min_x:
    waypoints.append(Waypoint(wp[0],wp[1]))

waypoints = Waypoints(waypoints)


sim = sim.simulation(waypoints, animate=False)
vehicle = sim.run()

plt.figure()
img = prob_map.toIMG()
plt.imshow(img)
plt.plot(vehicle.data['pos']['x'], vehicle.data['pos']['y'], '-r')
plt.xlim(0,img.size[0])
plt.ylim(0,img.size[1])
plt.show()