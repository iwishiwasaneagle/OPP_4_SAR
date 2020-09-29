import unittest
import numpy as np
import src.waypoint_generation as wpg 
import src.data_models.positional as pos
import src.data_models.probability_map as pm

class TestLHC_GW_CONV(unittest.TestCase):
    def test_conv_error_finding(self):
        prob_map = pm.ProbabilityMap(np.ones((15,15)))
        gen = wpg.LHC_GW_CONV(prob_map,pos.waypoint.Waypoint(0,0), animate=False)

        with self.assertRaises(TypeError):
            gen.convolute(pos.waypoint.Waypoint(0,0), prob_map, None)
        
        for i in wpg.ConvolutionType:
            raised = False
            try:
                gen.convolute(pos.waypoint.Waypoint(0,0), prob_map, i)
            except Exception as e:
                print(e)
                raised = True
            self.assertFalse(raised)

    def test_conv(self):
        prob_map = pm.ProbabilityMap(np.ones((50,50)))
        wp = pos.waypoint.Waypoint(25,25)
        gen = wpg.LHC_GW_CONV(prob_map,wp,animate=False)

        expected_sums = [48/float(49),24/float(25),8/float(9),120/float(121)]

        for i,expected_sum in zip(wpg.ConvolutionType,expected_sums):
            returned_sum = gen.convolute(wp, prob_map, i)
            self.assertAlmostEqual(expected_sum, returned_sum.value)


        

            