from .base_wp_generator import BaseWPGenerator

class ConstantSpeed(BaseWPGenerator):
    pass

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as sco

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints

prob_map_img = "img/probability_imgs/prob_map_2.png"
prob_map = ProbabilityMap.fromPNG(prob_map_img)

wps = 4
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
            cost += prob_map[i,j]
            
        x_old = x_cur
            
    return cost

x0 = (np.random.random(wps*2)*max(upper_1,upper_2))
print(x0)

min_x = sco.minimize(cost_func,x0)

waypoints = Waypoints()
for i in range(0,wps*2,2):
    waypoints.add(Waypoint(min_x.x[i],min_x.x[i+1]))
    

print(waypoints)