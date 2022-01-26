"""Radiometric Correction
"""
from .io import read_piccolo_file
import os
import pandas

_OPTICAL_PIXEL_RANGES = {
    # https://www.flowinjection.com/images/Flame_Technical_Specifications.pdf
    # '_FLMS': [20, 2047]
}


_DARK_PIXEL_RANGES = {
    # https://www.flowinjection.com/images/Flame_Technical_Specifications.pdf
    # '_FLMS': [[2, 17]],
    # # https://old.spectrecology.com/wp-content/uploads/2015/12/QEPro-OEM-Data-Sheet.pdf
    # '_QEP': [[4, 10], [-10, -4]]
}

class RadiometricCorrection:
    """Class for performing calibration transformation of Piccolo data.

    The order of operations is (1) Dark Signal estimation (2) Non Linearity
    Correction (3) Dark Signal subtraction (4) integration time normalisation
    (5) application of Gain (from calibration files).

    (1) Dark Signal Estimation
    As it has been observed that the QE Pro used in our lab group does not have
    adequate optical dark pixels, the dark signal is estimated from the
    reference file rather than from the optical dark pixels. By default the
    first dark file will be used.

    (2) Non Linearity Correction
    This is a linear transformation:
        corrected = dark + (raw - dark) / f(raw - dark)
    where f is a polynomial specified in the header

    (3) Dark Signal Subtraction
    This is a linear transformation:
        subtracted = corrected - dark

    (4) Integration Normalisation
    This is a linear transformation:
        normalised = subtracted / integration_time

    (5) Gain adjustment
    Conversion of DN to calibrated units using a calibration file
        calibrated = normalised * gain

    """

    def __init__(self, cal_file_paths, dark_reference=None):
        """
        Args:
            cal_file_paths (list): a list of filepaths with the identifier
                in the filename (i.e. FLMS01691_cals_.csv). Input files must
                have wvl, dnw and upw fields.
            dark_reference (str): If None, the average of all dark files in the
                sequence will be used (default). A filename can be supplied to
                specify a single file
        """
        self._cal_coefs = {}
        self._dark_reference_file = dark_reference

        for c in cal_file_paths:
            serial = self._get_serial(c)
            self._cal_coefs[serial] = self._load_calibration(c)

    def transform(self, piccolo_sequence):
        """Apply calibration transform

        Args:
            piccolo_sequence: open data files
        """
        dark_signal =
        cal = self.get_calibration(spectrum).interp_like(spectrum,
                                                         method='linear')
        # dark_signal = self.get_dark_signal(spectrum)
        # unclear whether this needs conversion as in ms
        t_s = spectrum.attrs['IntegrationTime']

        return cal * ((spectrum - dark_signal) / t_s)

    def get_calibration(self, spectrum):
        """Returns the calibration array

        Args:
            spectrum: DataArray with Direction and name parameters
        """
        serial = self._get_serial(spectrum.attrs['name'])
        direction = spectrum.attrs['Direction']
        return self._cal_coefs[serial][direction]

    def get_dark_signal(self, spectrum):
        """Returns the dark signal

        Args:
            spectrum: DataArray with Direction and name parameters
        """
        if self.dark_reference:
            direction = spectrum.attrs['Direction']
            serial = spectrum.attrs['name']
            # just take the mean across all regions
            return float(self.dark_reference[serial][direction].mean())
        else:
            # fallback to instrument optical dark pixels
            return spectrum.attrs['DarkSignal']

    def _calculate_dark_reference(self, piccolo_sequence, key=None):
        # find all keys with dark tag
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
            arrs = f[serial]
            out[serial] = {x.attrs['Direction']: x for x in arrs}
        return out

    def _truncate(self, spectrum):
        _01 = spectrum.quantile(.01)
        _99 = spectrum.quantile(.99)
        s = spectrum.where(spectrum <= _99, _99)
        return s.where(spectrum >= _01, _01)

    def _get_serial(self, filepath):
        base = os.path.basename(filepath)
        return base.split('_')[1]

    def _load_calibration(self, fpath):
        raw = pandas.read_csv(fpath)
        def parse(col):
            ar = xarray.DataArray(raw[col],
                                  coords=[('wavelength',raw['wvl'])])
            # truncate at .99 quantile
            return self._truncate(ar)
        return {'Downwelling': parse('dnw'),
                'Upwelling': parse('upw')}

    def _get_optical_pixel_range(self, dataArray):
        # use tag if present in metadata
        if 'OpticalPixelRange' in dataArray.attrs:
            return list(dataArray.attrs['OpticalPixelRange'])
        # Fallback to datasheet specification
        for tag, pix_range in _OPTICAL_PIXEL_RANGES.items():
            if tag in dataArray.attrs['name']:
                return list(pix_range)
        raise ValueError('OpticalPixelRange not retrieved')

    def _trim_to_optical_range(self, dataArray):
        return dataArray.isel(pixel=slice(
            *dataArray.attrs['OpticalPixelRange']))

    def _correct_non_linearity(self, dataArray):
        # Dark signal subtraction and non-linearity correction
        try:
            coefs = np.array(dataArray.attrs['NonlinearityCorrectionCoefficients'])
        except KeyError:
            coefs = np.array(dataArray.attrs['NonlinearityCorrectionCoefficients'])
        # poly1d requires coefs in reverse power order
        cpoly = np.poly1d(coefs[::-1])
        dark = dataArray.attrs['DarkSignal']
        corrected = dark + (dataArray - dark) / cpoly(dataArray - dark)
        corrected.attrs = dataArray.attrs
        return corrected
