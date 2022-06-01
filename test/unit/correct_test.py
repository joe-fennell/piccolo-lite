from piccololite import read_piccolo_sequence, RadiometricCorrection
import os

HERE = os.path.dirname(os.path.abspath(__file__))
cals = ['FLMS01691_CalCoeffs.csv', 'QEP00984_CalCoeffs.csv']
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

def test_transform_no_cal():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    r = RadiometricCorrection()
    x = r.transform(_ds)
    assert type(x) == dict

def test_transform_alternative_dark():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    r1 = RadiometricCorrection(cal_paths, 'b000000_s000009_dark.pico')
    r2 = RadiometricCorrection(cal_paths, 'b000000_s000000_dark.pico')
    x1 = r1.transform(_ds)
    x2 = r2.transform(_ds)
    # check dark references aren't identical
    assert r1.dark_reference != r2.dark_reference
    # assert both returns are valid
    assert type(x1) == dict
    assert type(x2) == dict
    # assert both returns aren't identical
    fn = 'b000000_s000000_light.pico'
    ser = 'QEP00984'
    dirs = 'Downwelling'
    assert (x1[fn][ser][dirs] != x2[fn][ser][dirs]).any()
