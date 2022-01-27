from piccololite import read_piccolo_file, read_piccolo_sequence
import os

HERE = os.path.dirname(os.path.abspath(__file__))

def test_file_read():
    file1 = 'b000000_s000005_light.pico'
    ds = read_piccolo_file(os.path.join(HERE, 'data', file1))
    # Manually checked raw pixel values for b000000_s000005_light.pico
    assert ds['S_QEP00984'][0][0] == 1644
    assert ds['S_QEP00984'][0][-1] == 200000
    assert ds['S_FLMS01691'][0][0] == 7
    assert ds['S_FLMS01691'][0][-1] == 752

    # Manually checked array lengths
    assert len(ds['S_FLMS01691'][0]) == 2048
    assert len(ds['S_QEP00984'][0]) == 1044

    # Manual check metadata
    assert "SaturationLevel" in ds['S_FLMS01691'][1].attrs
    assert "SaturationLevel" in ds['S_QEP00984'][1].attrs

    # Open another and test lengths are correct

    file2 = 'b000000_s000000_dark.pico'
    ds2 = read_piccolo_file(os.path.join(HERE, 'data', file2))

    # Manually checked array lengths
    assert len(ds2['S_FLMS01691'][0]) == 2048
    assert len(ds2['S_QEP00984'][0]) == 1044


def test_dir_read():
    _ds = read_piccolo_sequence(os.path.join(HERE, 'data'))
    ds = _ds['b000000_s000005_light.pico']

    # Manually checked raw pixel values for b000000_s000005_light.pico
    assert ds['S_QEP00984'][0][0] == 1644
    assert ds['S_QEP00984'][0][-1] == 200000
    assert ds['S_FLMS01691'][0][0] == 7
    assert ds['S_FLMS01691'][0][-1] == 752

    # Manual check metadata
    assert "SaturationLevel" in ds['S_FLMS01691'][1].attrs
    assert "SaturationLevel" in ds['S_QEP00984'][1].attrs

def test_dir_read_single():
    _ds = read_piccolo_sequence([os.path.join(HERE, 'data',
                                             'b000000_s000005_light.pico')])
    ds = _ds['b000000_s000005_light.pico']

    # Manually checked raw pixel values for b000000_s000005_light.pico
    assert ds['S_QEP00984'][0][0] == 1644
    assert ds['S_QEP00984'][0][-1] == 200000
    assert ds['S_FLMS01691'][0][0] == 7
    assert ds['S_FLMS01691'][0][-1] == 752

    # Manual check metadata
    assert "SaturationLevel" in ds['S_FLMS01691'][1].attrs
    assert "SaturationLevel" in ds['S_QEP00984'][1].attrs
