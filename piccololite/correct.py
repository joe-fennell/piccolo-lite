"""Radiometric Correction
"""
import datetime
import os
import pandas
import xarray
import numpy as np
import logging

from ._version import __version__
# logging.basicConfig(level=logging.DEBUG)

class RadiometricCorrection:
    """Class for performing calibration transformation of Piccolo data.

    The order of operations is (1) Dark Signal estimation (2) Non Linearity
    Correction (3) Dark Signal subtraction (4) integration time normalisation
    (5) application of Gain (from calibration files).

    ### 1. Dark Signal Estimation

    As it has been observed that the QE Pro used in our lab group does not have
    adequate optical dark pixels, the dark signal is estimated from the
    reference file rather than from the optical dark pixels. By default the
    first dark file will be used. Pixels that reach the SaturationLevel of the
    device are masked for this.

    ### 2. Non Linearity Correction

    Correct for non linearity across the dynamic range of the sensor
        corrected = dark + (raw - dark) / f(raw - dark)
    where f is a polynomial specified in the header

    ### 3. Dark Signal Subtraction

    Subtract off the dark signal (determined by a shutter closed measurement)
        subtracted = corrected - dark

    ### 4. Integration Normalisation

    Scale each measurement so that it is in unit DNs per second
        normalised = subtracted / integration_time

    ### 5. Bandwidth scaling

    Scale each measurement such that it in unit DNs per second per nm
        scaled = normalised / bandwidth

    ### 6. Gain adjustment (optional)

    Conversion of DN to calibrated units using a calibration file
        calibrated = scaled * gain

    """

    def __init__(self, calibration_file_paths=None, dark_reference=None,
                 correct_non_linearity=True, trim_optical_range=True,
                 correct_dark_signal=True, correct_integration_time=True,
                 correct_bandwidth=True, correct_gain=True):
        """
        Args:
            calibration_file_paths (list): a list of filepaths with the serial
                in the filename (i.e. FLMS01691_cals_.csv). Input files must
                have wvl, dnw and upw fields.
            dark_reference (str): If None, the average of all dark files in the
                sequence will be used (default). A filename can be supplied to
                specify a single file
            correct_non_linearity (bool): apply non linearity correction
            trim_optical_range (bool): trim wavelength range to optical region
            correct_dark_signal (bool): subtract off the dark signal
            correct_integration (bool): divide by integration time
            correct_gain (bool): apply gain multiplier (note this requires
                calibration_file_paths to be specified)
            correct_bandwidth (bool): divide by bandwidth

        Note: if cal_file_paths is not provided, no gain correction is made, so
        your data will be corrected DNs (rather than a radiometric unit)

        """
        self._cal_coefs = {}
        self.dark_reference = None
        self._dark_reference_file = dark_reference
        # flags defining which processing is applied
        self._do_non_linearity_correction = correct_non_linearity
        self._do_optical_range_trim = trim_optical_range
        self._do_correct_ds = correct_dark_signal
        self._do_correct_int_time = correct_integration_time
        self._do_correct_gain = correct_gain
        self._do_bandwidth_scaling = correct_bandwidth

        if calibration_file_paths is not None:
            for c in calibration_file_paths:
                serial = self._get_serial(c)
                self._cal_coefs[serial] = self._load_calibration(c)

        else:
            logging.warning('No calibration file provided. Final radiometric correction will not be made')
            self._do_correct_gain = False

    def transform(self, piccolo_sequence):
        """Apply calibration transform

        Args:
            piccolo_sequence: open data files
        """
        self.set_dark_reference(piccolo_sequence, self._dark_reference_file)

        out = {}
        # iterate filename
        for filename in piccolo_sequence.keys():
            _sub = {}
            for serial in piccolo_sequence[filename].keys():
                _sub2 = {}
                for _dir in piccolo_sequence[filename][serial].keys():
                    _sub2[_dir] = self._transform_single(
                        piccolo_sequence[filename][serial][_dir]
                    )
                _sub[serial] = _sub2
            out[filename] = _sub
        return out

    def get_calibration(self, spectrum):
        """Returns the calibration array

        Args:
            spectrum: DataArray with Direction and name parameters
        """
        serial = self._get_serial(spectrum.attrs['SerialNumber'])
        direction = spectrum.attrs['Direction']
        return self._cal_coefs[serial][direction]

    def get_dark_signal(self, spectrum):
        """Returns the dark signal

        Args:
            spectrum: DataArray with Direction and name parameters
        """
        if self.dark_reference:
            direction = spectrum.attrs['Direction']
            serial = spectrum.attrs['SerialNumber']
            # just take the mean across all regions
            return self.dark_reference[serial][direction]
        else:
            # fallback to instrument optical dark pixels
            return spectrum.attrs['DarkSignal']

    def set_dark_reference(self, piccolo_sequence, key=None):
        """Loads the dark reference from a piccolo_sequence.

        By default the first file is used, unless key specified.

        Args:
            piccolo_sequence: A piccolo sequence dictionary
            key (str): filename of .pico to use for dark signal
        """
        # find correct loaded pico file
        if not key:
            key = [x for x in piccolo_sequence.keys() if '_dark' in x]
            if len(key) < 1:
                raise ValueError('No dark signal file found')
            key = key[0]

        if key not in piccolo_sequence:
            raise ValueError('{} not in piccolo_sequence'.format(key))

        f = piccolo_sequence[key]
        out = {}
        for serial in f.keys():
            _sub = {}
            for _dir in f[serial].keys():
                arr = f[serial][_dir]
                sat_lvl = arr.attrs['SaturationLevel']
                direction = arr.attrs['Direction']
                # trim and mask out saturated
                x = self._trim_to_optical_range(arr).where(arr < sat_lvl)
                # # convert to dark signal rate
                # x = x / self._get_integration_time_s(x)
                _sub[direction] = float(x.mean())
            out[serial] = _sub
        self.dark_reference = out

    def _transform_single(self, da):
        # Get parameters
        dark_signal = self.get_dark_signal(da)
        # make an xarray copy
        x = da.copy()
        # non linearity correction
        if self._do_non_linearity_correction:
            x = self._correct_non_linearity(x, dark_signal)
            logging.debug('post linearity correct mean: {}'.format(
                x.mean().values))
        # Trim to internally specified optical range
        if self._do_optical_range_trim:
            x = self._trim_to_optical_range(x)
            logging.debug('post optic range trim mean: {}'.format(
                x.mean().values))
        # dark signal subtraction - note that this is reliant on dark signal
        # integration time being equal to measured signal integration time
        if self._do_correct_ds:
            x = x - dark_signal
            logging.debug('post DS subtraction mean: {}'.format(
                x.mean().values))
        # integration time normalisation
        if self._do_correct_int_time:
            x = x / self._get_integration_time_s(da)

        if self._do_bandwidth_scaling:
            x = x / self._get_band_width(x)

        if self._do_correct_gain:
            calibration = self.get_calibration(da)
            x = calibration.interp_like(x, method='linear') * x
            logging.debug('post gain mean: {}'.format(x.mean().values))
        # add metadata again
        x.attrs = da.attrs
        # add additional metadata
        try:
            x.attrs['CalibrationFilePath'] = calibration.attrs['SourceFilePath']
        except UnboundLocalError:
            x.attrs['CalibrationFilePath'] = 'None'
        x.attrs['DarkSignal'] = dark_signal
        x.attrs['RadiometricCorrectionCompleteUTC'] = \
            datetime.datetime.utcnow().isoformat()
        x.attrs['RadiometricCorrectionVersion'] = 'piccololite_v{}'.format(
            __version__)
        return x

    def _get_band_width(self, x):
        delta = x.wavelength.diff('wavelength') / 2
        delta = delta.pad(pad_width={'wavelength': 1}, mode='edge')
        return delta.values[:-1] + delta.values[1:]

    def _get_integration_time_s(self, dataArray):
        try:
            units = dataArray.attrs['IntegrationTimeUnits']
        except:
            raise RuntimeError('Datasets must specify IntegrationTimeUnits')

        try:
            int_time = dataArray.attrs['IntegrationTime']
        except:
            raise RuntimeError('Datasets must specify IntegrationTime')

        if units == 'milliseconds':
            return float(int_time) / 1000

        elif units == 'seconds':
            return float(int_time)

        else:
            raise RuntimeError('IntegrationTimeUnits ({}) not supported'.format(units))

    def _truncate(self, spectrum):
        _01 = spectrum.quantile(.01)
        _99 = spectrum.quantile(.99)
        s = spectrum.where(spectrum <= _99, _99)
        return s.where(spectrum >= _01, _01)

    def _get_serial(self, filepath):
        base = os.path.basename(filepath)
        return base.split('_')[0]

    def _load_calibration(self, fpath):
        raw = pandas.read_csv(fpath)
        def parse(col):
            ar = xarray.DataArray(raw[col],
                                  coords=[('wavelength',raw['wvl'])])
            ar.attrs['SourceFilePath'] = os.path.abspath(fpath)
            # truncate at .99 quantile
            return self._truncate(ar)
        return {'Downwelling': parse('dnw'),
                'Upwelling': parse('upw')}

    def _trim_to_optical_range(self, dataArray):
        _range = self._get_optical_pixel_range(dataArray)
        ds = dataArray.swap_dims({'wavelength':'pixel'})
        return ds.isel(pixel=slice(*_range)).swap_dims(
            {'pixel': 'wavelength'})

    def _get_optical_pixel_range(self, dataArray):
        # use tag if present in metadata
        if 'OpticalPixelRange' in dataArray.attrs:
            return list(dataArray.attrs['OpticalPixelRange'])
        # Fallback to full range
        return [0,len(dataArray)]

    def _correct_non_linearity(self, dataArray, dark):
        # Dark signal subtraction and non-linearity correction
        coefs = np.array(dataArray.attrs['NonlinearityCorrectionCoefficients'])
        # poly1d requires coefs in reverse power order
        cpoly = np.poly1d(coefs[::-1])
        corrected = dark + (dataArray - dark) / cpoly(dataArray - dark)
        corrected.attrs = dataArray.attrs
        return corrected
