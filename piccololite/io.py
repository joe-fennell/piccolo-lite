"""Piccolo file (.pico) input/output
"""
import json
import numpy as np
import pandas
import os
import xarray


def read_piccolo_file(piccolo_data, assign_coords=False):
    """Read in a piccolo data file.

    Args:
        piccolo_data: Can be 1. a valid filepath 2. json-like string
            containing piccolo data
        assign_coords: a list of coords to assign to new dimensions
    """
    try:
        # assume a filepath first
        _data = _read_from_json_file(piccolo_data)

    except FileNotFoundError as f:
        try:
            # try and read string directly
            _data = _parse_from_string(piccolo_data)
        except:
            raise f

    spectra = []
    for i, ds in enumerate(_data['Spectra']):
        _pixel = _make_spectrum(ds)
        # assign wavelength coordinate
        _pixel = _pixel.assign_coords({'wavelength': ('pixel',
                                                      _get_wavelengths(_pixel))
                                       })
        if assign_coords:
            _pixel = _assign_coords(_pixel, assign_coords)

        spectra.append(_pixel.swap_dims({'pixel': 'wavelength'}))

    # sort into 1 dataset per instrument
    out = {}
    for s in spectra:
        name = s.attrs['name']
        if name in out:
            out[name].append(s)
        else:
            out[name] = [s]

    return out

def read_piccolo_sequence(files, *args, **kwargs):
    """Read a directory of .pico files or an explicit list.

    Args and Kwargs can be supplied to read_piccolo_file

    Args:
        files: Can be a list or path to a directory of .pico files
    """
    if type(files) == str:
        root = files
        # assume a directory
        flist = os.listdir(root)
        files = [os.path.join(root, x) for x in flist if x.endswith('.pico')]

    out = {}
    for path in files:
        fname = os.path.basename(path)
        out[fname] = read_piccolo_file(path, *args, **kwargs)

    return out


# Private funcs
def _assign_coords(dataArray, coords = ['Dark', 'name', 'Direction']):
    for c in coords:
        try:
            dataArray = dataArray.expand_dims({c.lower(): [dataArray.attrs[c]]})
        except KeyError:
            pass
    return dataArray


def _read_from_json_file(fpath):
    # read only open
    with open(fpath, 'r') as f:
        return _parse_from_string(f.read())


def _parse_from_string(data_string):
    return json.loads(data_string)


def _make_spectrum(reading):
    # do baseline parsing to xarray
    pix = np.array(reading['Pixels'], dtype='uint32')
    return xarray.DataArray(
        pix,
        coords = [('pixel', np.arange(len(pix)))],
        attrs = reading['Metadata'])


def _get_wavelengths(dataArray):
    coefs = np.array(dataArray.attrs['WavelengthCalibrationCoefficients'])
    # poly1d requires coefs in reverse power order
    wpoly = np.poly1d(coefs[::-1])
    return wpoly(dataArray.pixel)
