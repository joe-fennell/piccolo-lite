from piccololite import read_piccolo_file, read_piccolo_sequence, \
sequence_to_datasets

import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))

def test_file_read():
    file1 = 'b000000_s000005_light.pico'
    ds = read_piccolo_file(os.path.join(HERE, 'data', file1))
    _check_b000000_s000005_light(ds)
    # Open another and test lengths are correct
    file2 = 'b000000_s000000_dark.pico'
    ds2 = read_piccolo_file(os.path.join(HERE, 'data', file2))
    _check_b000000_s000000_dark(ds2)


def test_dict_read():
    file1 = 'b000000_s000005_light.pico'
    with open(os.path.join(HERE, 'data', file1), 'r') as f:
        json_str = json.loads(f.read())
    ds = read_piccolo_file(json_str)
    _check_b000000_s000005_light(ds)


def test_json_str_read():
    file1 = 'b000000_s000005_light.pico'
    with open(os.path.join(HERE, 'data', file1), 'r') as f:
        json_str = f.read()
    ds = read_piccolo_file(json_str)
    _check_b000000_s000005_light(ds)


def test_dir_read():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    ds = _ds['b000000_s000005_light.pico']
    _check_b000000_s000005_light(ds)


def test_dir_read_single():
    _ds = read_piccolo_sequence([os.path.join(HERE, 'data',
                                             'b000000_s000005_light.pico')])
    ds = _ds['b000000_s000005_light.pico']
    _check_b000000_s000005_light(ds)


def test_sequence_to_datasets():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    _new = sequence_to_datasets(_ds)
    # 24 readings in each dataset
    assert len(_new['QEP00984']) == 26
    assert len(_new['FLMS01691']) == 26


# file specific checking parameters
def _check_b000000_s000005_light(ds):
    # Manually checked raw pixel values for b000000_s000005_light.pico
    assert ds['QEP00984']['Upwelling'][0] == 1644
    assert ds['QEP00984']['Upwelling'][-1] == 200000
    assert ds['FLMS01691']['Upwelling'][0] == 7
    assert ds['FLMS01691']['Upwelling'][-1] == 752

    # Manually checked array lengths
    assert len(ds['FLMS01691']['Upwelling']) == 2048
    assert len(ds['QEP00984']['Upwelling']) == 1044

    # Manual check metadata
    assert "SaturationLevel" in ds['FLMS01691']['Upwelling'].attrs
    assert "SaturationLevel" in ds['QEP00984']['Upwelling'].attrs

def _check_b000000_s000000_dark(ds):
    # Manually checked array lengths
    assert len(ds['FLMS01691']['Upwelling']) == 2048
    assert len(ds['QEP00984']['Upwelling']) == 1044
