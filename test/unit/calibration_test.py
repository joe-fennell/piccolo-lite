from piccololite import generate_calibration

import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))

def test_calibrate_simple():
    dpath = os.path.join(HERE, 'data')
    refpath = os.path.join(dpath, 'F1380_irradiance.nc')
    c = generate_calibration(dpath, refpath)
    assert len(c) == 2
