from pdb import set_trace
from matplotlib import pyplot as plt
import numpy as np

from gfatpy.atmo.atmo import standard_atmosphere, generate_meteo_profiles 

def test_standard_atmosphere():    
    heights = np.arange(2666) * 7.5
    pressure, temperature, density = standard_atmosphere(heights)    
    assert pressure.shape == (2666,)
    assert temperature.shape == (2666,)
    assert density.shape == (2666,)

#TODO: test generate_meteo_profile
