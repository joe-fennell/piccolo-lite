from piccololite import read_piccolo_sequence, RadiometricCorrection
import os

HERE = os.path.dirname(os.path.abspath(__file__))
cals = ['S_FLMS01691_CalCoeffs.csv', 'S_QEP00984_CalCoeffs.csv']
cal_paths = [os.path.join(HERE, 'data', x) for x in cals]

def test_instantiate():
    # test paths with known values
    r = RadiometricCorrection(cal_paths)
    r = RadiometricCorrection(cal_paths, '123')

def test_set_dark():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    r = RadiometricCorrection(cal_paths)
    r.set_dark_reference(_ds)
    assert type(r.dark_reference) == dict

def test_transform():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    r = RadiometricCorrection(cal_paths)
    x = r.transform(_ds)
    assert type(x) == dict
