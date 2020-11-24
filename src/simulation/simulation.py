from math import cos, sin
from src.waypoint_generation.waypoint_settings import SarGenOutput, WaypointAlgSettings
from src.enums.waypoint_algorithm_enum import WaypointAlgorithmEnum
from loguru import logger
import numpy as np
from src.simulation.vehicle import Vehicle, VehicleSimData
from src.simulation.trajectory import Trajectory, Trajectories
from src.simulation.parameters import *
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.data_models.positional.pose import Pose
from typing import List, Tuple

class SimRunnerOutput:
    def __init__(self) -> None:
        self.data = []

    def add_simulation_data(self, sim_output: VehicleSimData, alg:WaypointAlgorithmEnum):
        assert(isinstance(sim_output,VehicleSimData))
        assert(isinstance(alg,WaypointAlgorithmEnum))
        self.data.append((alg,sim_output))    

class Simulation:
    def __init__(self, waypoints: Waypoints,searched_object_locations: Waypoints, animate:bool=False):

        self.waypoints=waypoints

        self.trajectories=Trajectories()
        self.animate = animate

        self.wp_settings = WaypointAlgSettings.Global()

        self.search_radius = self.wp_settings.search_radius
        self.searched_object_locations = searched_object_locations.toNumpyArray()
        self.num_objs = len(self.searched_object_locations)
   
        logger.info(f"Running simulation with {len(waypoints)} waypoints and {len(searched_object_locations)} searched objects with search radius = {self.search_radius}")

    def run(self) -> VehicleSimData:
        for i,wp in enumerate(self.waypoints):
            try:
                trajectory = Trajectory(wp, self.waypoints[i+1], 1)
                self.trajectories.add(trajectory)
            except IndexError:
                break

        vehicle = Vehicle(pos=Pose.fromWP(self.waypoints[0]), animate=self.animate)

        t = 0
        for trajectory in self.trajectories:
            t_local = 0
            while t_local <= trajectory.T:
                # Search for object
                if self.searched_object_locations is not None:

                    # create distance vectors
                    v = np.array([vehicle.pos.x-self.searched_object_locations[:,0],vehicle.pos.y-self.searched_object_locations[:,1]])
                    # if distance is < search radius -> object found
                    dist = np.linalg.norm(v,axis=0)
                    if any(dist<self.search_radius):
                        inds = np.where(dist<self.search_radius)[0]
                        for ind in inds:
                            loc = self.searched_object_locations[ind]
                            vehicle.data.found.append((t,loc)) 
                        self.searched_object_locations = np.delete(self.searched_object_locations,inds,axis=0)

                        

                # Calc desired position, velocity and acceleration from generated polynomial trajectory
                des_pos = trajectory.position(t_local)
                des_vel = trajectory.velocity(t_local)
                des_acc = trajectory.acceleration(t_local)
                
                # Step the vehicle
                vehicle.step(des_pos, des_vel, des_acc)

                # Update time
                t_local += dt
                t += dt

        return vehicle.data
