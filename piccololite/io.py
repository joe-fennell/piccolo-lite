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
        fpath = os.path.abspath(piccolo_data)

    except (FileNotFoundError, TypeError, OSError) as f:
        fpath = 'NA'
        try:
            # try and read string directly
            _data = _parse_from_string(piccolo_data)
        except TypeError:
            if type(piccolo_data) == dict:
                _data = piccolo_data
            else:
                raise f

    spectra = []
    names = []
    for i, ds in enumerate(_data['Spectra']):
        _pixel = _make_spectrum(ds)
        _pixel.attrs['SourceFilePath'] = fpath
        # assign wavelength coordinate
        _pixel = _pixel.assign_coords({'wavelength': ('pixel',
                                                      _get_wavelengths(_pixel))
                                       })
        if assign_coords:
            _pixel = _assign_coords(_pixel, assign_coords)

        spectra.append(_pixel.swap_dims({'pixel': 'wavelength'}))
        names.append(_pixel.attrs['name'])

    # sort into 1 dataset per instrument
    out = {k:{'Downwelling':None, 'Upwelling':None} for k in np.unique(names)}

    for s in spectra:
        name = s.attrs['name']
        direction = s.attrs['Direction']
        out[name][direction] = s
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

def sequence_to_datasets(piccolo_sequence, clean_metadata=True):
    """Converts a Piccolo sequence dictionary to xarray Datasets.

    Each dataset represents a single instrument.

    Args:
        piccolo_sequence: nested dictionary of piccolo spectra.
        clean_metadata (bool): if True, attempts to clean metadata
            so that the dataset is safe for writing to netcdf

    Returns:
        dictionary of xarray Datasets keyed by instrument serial
    """
    serials = list(piccolo_sequence.values())[0].keys()
    out = {k:{} for k in serials}
    # iterate serial numbers
    for s in serials:
        for fname in piccolo_sequence.keys():
            for _dir in ['Upwelling', 'Downwelling']:
                new_key = '{}_{}_{}'.format(
                    fname.split('.pico')[0],
                    s, _dir)
                arr = piccolo_sequence[fname][s][_dir].copy()
                # attempt to clean metadata for NetCDF4 writing
                if clean_metadata:
                    arr.attrs = _clean_metadata(arr)
                out[s][new_key] = arr

    return {k: xarray.merge([v]) for k,v in out.items()}

def sequence_to_netcdf(piccolo_sequence, fname):
    """Converts a Piccolo sequence dictionary to NetCDF files.

    Each file represents a single instrument.

    Args:
        piccolo_sequence: nested dictionary of piccolo spectra.
            Must be in the form [filename][instrument][downwelling]
            or a dictionary of xarray Datasets
        fname (str): destination filename
    """

    def parse_fname(ser):
        if not fname.endswith('.nc'):
            return fname + '_{}.nc'.format(ser)
        else:
            return fname[:-3] + '_{}.nc'.format(ser)
    try:
        for serial, ds in piccolo_sequence.items():
            ds.to_netcdf(parse_fname(serial))
    except AttributeError:
        piccolo_sequence = sequence_to_datasets(piccolo_sequence, True)
        for serial, ds in piccolo_sequence.items():
            ds.to_netcdf(parse_fname(serial))

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
    pix = np.array(reading['Pixels'], dtype=float)
    da = xarray.DataArray(pix,
                          coords = [('pixel', np.arange(len(pix)))],
                          attrs = reading['Metadata'])
    return da


def _get_wavelengths(dataArray):
    coefs = np.array(dataArray.attrs['WavelengthCalibrationCoefficients'])
    # poly1d requires coefs in reverse power order
    wpoly = np.poly1d(coefs[::-1])
    return wpoly(dataArray.pixel)

def _clean_metadata(da):
    new_meta = {}
    mapping = {
        None: 'None',
        True: 'True',
        False: 'False'
    }
    for k, v in da.attrs.items():
        try:
            new_meta[k] = mapping[v]
        except (KeyError, TypeError):
            new_meta[k] = v
    return new_meta
