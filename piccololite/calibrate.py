"""Routines for Piccolo calibration
"""
from .correct import RadiometricCorrection
from .io import read_piccolo_sequence, aggregate_sequence
import logging
import xarray

def generate_calibration(piccolo_sequence, reference, direction=None):
    """Calculate the calibration coefficients for the Piccolo.

    As different calibration sources are used for Upwelling and Downwelling,
    this process must be repeated for the different directions.

    Note that if defining the  reference object, the wavelength dimension must
    be named 'wavelength' and should be in nanometres. The metadata should
    contain ['WavelengthUnit', 'RadiometricUnit', 'CalibrationSourceReference',
    'CalibrationDirection']

    Args:
        piccolo_sequence : a standard piccolo sequence, or filepath to
            standard format directory
        reference : filepath to a calibration reference file in NetCDF format
        direction (optional) : Upwelling or Downwelling but can be inferred
            from reference NetCDF
    """

    # Read reference files if a string
    if type(reference) is str:
        reference = xarray.load_dataarray(reference)

    # guess direction if not provided
    if not direction:
        if reference.attrs['SourceType'] == 'absolute radiance':
            direction = 'Upwelling'
        elif reference.attrs['SourceType'] == 'absolute irradiance':
            direction = 'Downwelling'
        else:
            raise ValueError('{} not a recognised SourceType'.format(
                reference.attrs['SourceType']))

    # Read piccolo_sequence
    if type(piccolo_sequence) is not dict:
        piccolo_sequence = read_piccolo_sequence(piccolo_sequence)

    # apply non linearity, integration time correction etc.
    # and calculate mean
    correction = RadiometricCorrection()
    mean_seq = aggregate_sequence(correction.transform(piccolo_sequence),
                                  'mean')
    out = {}
    for instr, v in mean_seq.items():
        _measured = v[direction].fillna(1e-4)
        # _coefs = (reference / _measured.interp_like(reference)).interp_like(_measured)
        _coefs = (reference.interp_like(_measured) / _measured).interp_like(_measured)

        # Add metadata
        _coefs.attrs = _measured.attrs

        for k in ['WavelengthUnit', 'RadiometricUnit',
                  'CalibrationSourceReference']:
            try:
                _coefs.attrs[k] = reference.attrs[k]
            except KeyError:
                logging.warning('{} metadata missing from cal'.format(k))

        _coefs.attrs['CalibrationDirection'] = direction
        _coefs.attrs['Type'] = 'calibration'
        out[instr] = _coefs

    return out
