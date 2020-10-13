import cProfile

from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_factory import WaypointFactory, WaypointAlgorithmEnum

prob_map_img = "img/probability_imgs/prob_map_6_multimodal_tiny.png"
prob_map = ProbabilityMap.fromPNG(prob_map_img)

cProfile.run('WaypointFactory(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER, prob_map, threaded = False, animate=False).generate()')