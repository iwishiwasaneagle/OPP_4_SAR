import os
import diskcache as dc
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
import matplotlib.pyplot as plt
import tempfile
import time

class SimRunnerOutput:
    def __init__(self) -> None:
        self.data = []

    def add_simulation_data(self, sim_output: VehicleSimData, alg: WaypointAlgorithmEnum):
        assert(isinstance(sim_output, VehicleSimData))
        assert(isinstance(alg, WaypointAlgorithmEnum))
        self.data.append((alg, sim_output))


class Simulation:
    def __init__(self, waypoints: Waypoints, searched_object_locations: Waypoints, search_radius: float, mean_flight_speed: float, animate: bool = False,alg:WaypointAlgorithmEnum=WaypointAlgorithmEnum.UNKNOWN):

        self.waypoints = waypoints

        self.vehicle = Vehicle(pos=Pose.fromWP(self.waypoints[0]))
        self.trajectories = Trajectories()
        self.animate = animate
        self.alg = alg
        if self.animate:
            plt.ion()
            fig = plt.figure()
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])
            self._ax_pos = fig.add_subplot(211)
            self._ax_xy = fig.add_subplot(234)
            self._ax_dxy = fig.add_subplot(235)
            self._ax_ddxy = fig.add_subplot(236)


        self.wp_settings = WaypointAlgSettings.Global()

        self.search_radius = search_radius
        self.mean_flight_speed = mean_flight_speed
        self.searched_object_locations = searched_object_locations.toNumpyArray()
        self.num_objs = len(self.searched_object_locations)


        logger.info(
            f"{alg} - Running simulation with {len(waypoints)} waypoints and {len(searched_object_locations)} searched objects with search radius = {self.search_radius}",enqueue=True)

    def run(self) -> VehicleSimData:
        bounds = []
        bounds.append((self.waypoints[0],Pose.zero()))
        for wp_a, wp_b, wp_c in zip(self.waypoints[:-2],self.waypoints[1:-1],self.waypoints[2:]):
            a = np.array(wp_a)
            b = np.array(wp_b)
            c = np.array(wp_c)

            rAC = c-a
            rBA = a-b
            rBC = c-b
            rAC_unit = rAC/np.clip(np.linalg.norm(rAC),1e-6,np.inf) 
            theta = rBA.dot(rBC)/(np.linalg.norm(rBA)*np.linalg.norm(rBC))
            chi = np.power((1-theta)/2,3)
            vB = Pose(self.mean_flight_speed*rAC_unit*chi)
            bounds.append((wp_b,vB))
        bounds.append((self.waypoints[-1],Pose.zero()))

        for (wp1,v1),(wp2,v2) in zip(bounds[:-1],bounds[1:]):
                
            a = np.array(wp1)
            b = np.array(wp2)

            dist = np.linalg.norm(b-a)
            t = dist/self.mean_flight_speed

            trajectory = Trajectory(start_pos=wp1,
                                    dest_pos=wp2,
                                    T=t,
                                    start_vel=v1,
                                    dest_vel=v2,)
            self.trajectories.add(trajectory)

        t = 0
        max_x,max_y = np.max(self.searched_object_locations,axis=0)
        min_x,min_y = np.min(self.searched_object_locations,axis=0)
        x,y = np.meshgrid(np.arange(min_x,max_x+1),np.arange(min_y,max_y+1))
        x,y=x.flatten(),y.flatten()
        objs_possible_xy = np.vstack((x,y)).T

        np.random.seed(int(time.time()*len(self.alg)*len(self.waypoints)))
        cache_path = os.path.join(tempfile.gettempdir(),'opp4sar',str(np.random.rand())[2:])
        cache = dc.Cache(cache_path)
        logger.trace(f"{self.alg} - Cache path = {cache_path}",enqueue=True)
                
        for i,trajectory in enumerate(self.trajectories):
            t_local = 0

            logger.trace(
                f"{self.alg} - Trajectory {i}/{len(self.trajectories)} with T={trajectory.T:.2f}s", enqueue=True)
            while t_local <= trajectory.T:
                # Search for object
                if self.searched_object_locations is not None:

                    # create distance vectors
                    v = np.array([self.vehicle.pos.x-objs_possible_xy[:,0],
                                  self.vehicle.pos.y-objs_possible_xy[:, 1]])

                    # if distance is < search radius -> object found
                    dist = np.linalg.norm(v, axis=0)

                    if any(dist < self.search_radius):
                        inds = np.where(dist < self.search_radius)[0]
                        for ind in inds:
                            loc = objs_possible_xy[ind]
                            cache[f'{loc[0]},{loc[1]}'] = t                            
                        objs_possible_xy = np.delete(objs_possible_xy, inds, axis=0)

                # Calc desired position, velocity and acceleration from generated polynomial trajectory
                des_pos = trajectory.position(t_local)
                des_vel = trajectory.velocity(t_local)
                des_acc = trajectory.acceleration(t_local)

                # Step the vehicle
                self.vehicle.step(des_pos, des_vel, des_acc)

                # Update time
                t_local += dt
                t += dt

                if t_local==dt and self.animate:
                    self._plot()
                    
        for key in cache.iterkeys():
            t = cache[key]
            xy=tuple(np.array(key.split(',')).astype(float).astype(int))
            inds = np.where((self.searched_object_locations[:,0]==xy[0])&(self.searched_object_locations[:,1]==xy[1]))[0]
            for ind in inds:
                self.vehicle.data.found.append(
                    (t,self.searched_object_locations[ind])
                )

        logger.info(
            f"{self.alg} - Found {100*len(self.vehicle.data.found)/self.num_objs:.2f}% ({len(self.vehicle.data.found)}/{self.num_objs}) objects", enqueue=True)

        if self.animate:
            self._plot()
            plt.show(block=True)

        return self.vehicle.data
    
    def _plot(self) -> None:

        wps_x = self.waypoints.x
        wps_y = self.waypoints.y

        fig = self._ax_pos
        fig.cla()
        fig.set_aspect('equal',adjustable='datalim')
        fig.scatter(wps_x,wps_y,c='g',s=2)
        fig.add_artist(plt.Circle((self.vehicle.pos.x, self.vehicle.pos.y), size, color='r'))
        fig.plot(self.vehicle.data.pos.x, self.vehicle.data.pos.y, 'b:')      

        fig.quiver(self.vehicle.pos.x, self.vehicle.pos.y,np.clip(0.01,np.inf,self.vehicle.dpos.x), np.clip(0.001,np.inf,self.vehicle.dpos.y))
        
        fig.set_ylabel("y ($m$)")
        fig.set_xlabel("x ($m$)")
        fig.text(0.1,0.9,f"t=${self.vehicle.t:.2f}s$",ha='center', va='center', transform=fig.transAxes) 
        
        fig = self._ax_xy
        fig.cla()
        fig.set_ylabel("position ($m$)")
        fig.set_xlabel("$t$ ($s$)")
        x = np.array(self.vehicle.data.pos.x)
        y = np.array(self.vehicle.data.pos.y)
        fig.plot(self.vehicle.data.t,x,label=r'$\vec p_x$')
        fig.plot(self.vehicle.data.t,y,label=r'$\vec p_y$')
        fig.legend()
        
        fig = self._ax_dxy
        fig.cla()
        fig.set_ylabel("speed ($ms^{-1}$)")
        fig.set_xlabel("$t$ ($s$)")
        x = np.array(self.vehicle.data.dpos.x)
        y = np.array(self.vehicle.data.dpos.y)
        mag = np.linalg.norm([x,y],axis=0)
        fig.plot(self.vehicle.data.t,x,label=r'$\dot \vec p_x$')
        fig.plot(self.vehicle.data.t,y,label=r'$\dot \vec p_y$')
        fig.plot(self.vehicle.data.t,mag,label=r'$|\dot \vec p|$')
        fig.legend()

        fig = self._ax_ddxy
        fig.cla()
        fig.set_ylabel("acceleration ($m^2 s^{-1}$)")
        fig.set_xlabel("$t$ ($s$)")
        x = np.array(self.vehicle.data.ddpos.x)
        y = np.array(self.vehicle.data.ddpos.y)
        mag = np.linalg.norm([x,y],axis=0)
        fig.plot(self.vehicle.data.t,x,label=r'$\ddot \vec p_x$')
        fig.plot(self.vehicle.data.t,y,label=r'$\ddot \vec p_y$')
        fig.plot(self.vehicle.data.t,mag,label=r'$|\ddot \vec p|$')
        fig.legend()

        plt.pause(0.0001)
