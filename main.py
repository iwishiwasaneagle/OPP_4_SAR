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

prob_map.lq_shape = (10,10)

img = prob_map.toIMG(prob_map.lq_prob_map)
plt.figure()
plt.imshow(img) 
plt.xlim(0,10)
plt.ylim(0,10)
plt.show()


#waypoints = WaypointFactory(WaypointAlgorithmEnum.LHC_GW_CONV_E, prob_map, Waypoint(0,0),threaded=True,animate=False).generate()
#waypoints = Waypoints([Waypoint(5,0), Waypoint(10, 0), Waypoint(10, 10),Waypoint(0, 10)])
#waypoints = WaypointFactory(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER, prob_map, threaded = False, animate=False).generate()


import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as sco

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints
wps = 8
lower_1,lower_2 = 0,0
upper_1,upper_2 = max(prob_map.shape),max(prob_map.shape)

b = 25 # sweep width

def cost_func(x:np.array) -> float:
    x = np.reshape(x,(len(x)//2,2))
    
    x_old = x[0]    
    cost = 0
    for x_cur in x[1:]:
        
        cost += line_probability_cost(x_old, x_cur, prob_map)

        dist = np.linalg.norm(x_old-x_cur)
        cost +=  dist

        x_old = x_cur
            
    return cost

def line_probability_cost(x1,x2, prob_map) -> float: 
    y = lambda i:  i*((x2[1]-x1[1])/(x2[0]-x1[0])) - x1[0] + x1[1]
    
    x_test = np.arange(x1[0],x2[0])
    y_test = y(x_test)
    
    x_test = set(np.round(x_test,0))
    y_test = set(np.round(y_test,0))
    
    cost = 0
    for i,j in zip(x_test,y_test):
        cost -= prob_map[i,j]
    
    return cost

if __name__ == "__main__":
    r = 0.9*max(upper_1,upper_2)/2
    x0 = [(r+r*np.cos(theta), r+r*np.sin(theta)) for theta in np.arange(0,2*np.pi,2*np.pi/wps)]
    x0.append(x0[0])
    x0_store = np.array(x0)
    x0 = np.reshape(x0,np.shape(x0)[0]*np.shape(x0)[1])

    print("Started optimisation")

    res = sco.minimize(cost_func,x0,method='Nelder-Mead',options={'maxiter':10000000})
    print("Finished optimisation")
    print(res)
    min_x = np.reshape(res.x,(len(res.x)//2,2))

    waypoints = []
    for wp in min_x:
        waypoints.append(Waypoint(wp[0],wp[1]))

    waypoints = Waypoints(waypoints)


    sim = sim.simulation(waypoints, animate=False)
    vehicle = sim.run()

    plt.figure()
    img = prob_map.toIMG()
    plt.imshow(img)
    plt.plot(x0_store[:,0], x0_store[:,1],'g')
    plt.plot(vehicle.data['pos']['x'], vehicle.data['pos']['y'], '-r')
    plt.xlim(0,img.size[0])
    plt.ylim(0,img.size[1])
    plt.show()