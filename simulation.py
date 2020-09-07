import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from models import Pose, Vehicle

def unit_vector(vector):
    return vector / np.linalg.norm(vector)
def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


### generate

waypoints = enumerate([Pose(0,0), Pose(5,0),Pose(10,10), Pose(5,5), Pose(0,5), Pose(0,0)])

### simulate

t_start = 0
t_end = 60
dt = 0.01

const_vel = 10 #m/s

t_store = []

vehicle = Vehicle()
vehicle.pos = Pose(-1,-1)

wp = next(waypoints)

for t in np.linspace(t_start,t_end,int((t_end-t_start)/0.01)):
    # store
    t_store.append(t)
    vehicle.store()

    # control
    if vehicle.pos == wp[1]:
        wp_old = wp
        try:
            wp = next(waypoints)
        except StopIteration as e:
            print(e)
            break

    theta = angle_between(wp[1].toTuple(), vehicle.pos.toTuple()) 

    vehicle.vel=Pose(const_vel*np.cos(theta),const_vel*np.sin(theta)) 

    # step
    vehicle.step(dt)

### analyse

fig0 = plt.figure()

plt.plot(t_store, [f.normalize() for f in vehicle.vel_store])
plt.show()

fig1 = plt.figure()
plt.plot([f.x for f in vehicle.pos_store], [f.y for f in vehicle.pos_store])
plt.show()

print("Done")


