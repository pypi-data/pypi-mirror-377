import numpy as np
import xarray as xr
import pynusinov._misc as _m


class Euvt2021:
    '''
    EUVT model class.
    '''

    def __init__(self):
        self._bands_dataset, self._lines_dataset = _m.get_nusinov_euvt_coeffs()
        self._bands_coeffs = np.vstack((np.array(self._bands_dataset['B0'], dtype=np.float64),
                                        np.array(self._bands_dataset['B1'], dtype=np.float64))).transpose()
        self._lines_coeffs = np.vstack((np.array(self._lines_dataset['B0'], dtype=np.float64),
                                        np.array(self._lines_dataset['B1'], dtype=np.float64))).transpose()

    def _get_nlam(self, lac):
        '''
        A method for preparing data. It creates a two-dimensional array, the first column of which is filled with ones,
        the second with the values of the fluxes in the Lyman-alpha line.
        :param lac: single value or list of flux values in lac unit (1 lac = 1 * 10^15 m^-2 * s^-1).
        :return: numpy-array for model calculation.
        '''

        try:
            if isinstance(lac, float) or isinstance(lac, int):
                return np.array([lac, lac ** 2], dtype=np.float64).reshape(1, 2)
            return np.vstack([np.array([x, x ** 2]) for x in lac], dtype=np.float64)
        except TypeError:
            raise TypeError('Only int, float or array-like object types are allowed.')

    def get_spectral_lines(self, lac):
        '''
        Model calculation method. Returns the values of radiation fluxes in all lines
        of the spectrum of the interval 10-105 nm.
        :param lac: single value or list of flux values in lac unit (1 lac = 1 * 10^15 m^-2 * s^-1).
        :return: xarray Dataset [euv_flux_spectra, wavelength].
        '''

        nlam = self._get_nlam(lac)
        res = np.dot(self._lines_coeffs, nlam.T) * 1.e15
        return xr.Dataset(data_vars={'euv_flux_spectra': (('line_wavelength', 'lac'), res),
                                     'wavelength': ('line_number', self._lines_dataset['lambda'].values)},
                          coords={'lac': nlam[:, 0],
                                  'line_wavelength': self._lines_dataset['lambda'].values,
                                  'line_number': np.arange(16)})

    def get_spectral_bands(self, lac):
        '''
        Model calculation method. Returns the xarray dataset values of radiation fluxes in all intervals
        of the spectrum of the interval 10-105 nm.
        :param lac: single value or list of flux value in lac unit (1 lac = 1 * 10^15 m^-2 * s^-1)s.
        :return: xarray Dataset [euv_flux_spectra, lband, uband].
        '''

        nlam = self._get_nlam(lac)
        res = np.dot(self._bands_coeffs, nlam.T) * 1.e15
        return xr.Dataset(data_vars={'euv_flux_spectra': (('band_center', 'lac'), res),
                                     'lband': ('band_number', self._bands_dataset['lband'].values),
                                     'uband': ('band_number', self._bands_dataset['uband'].values)},
                          coords={'lac': nlam[:, 0],
                                  'band_center': self._bands_dataset['center'].values,
                                  'band_number': np.arange(20)})

    def get_spectra(self, lac):
        '''
        Model calculation method. Combines the get_spectral_bands() and  get_spectra_lines() methods.
        :param lac: single value or list of flux values in lac unit (1 lac = 1 * 10^15 m^-2 * s^-1).
        :return: xarray Dataset [euv_flux_spectra, lband, uband], xarray Dataset [euv_flux_spectra, wavelength]
        '''

        return self.get_spectral_bands(lac), self.get_spectral_lines(lac)
