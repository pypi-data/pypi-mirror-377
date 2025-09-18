# pynusinov
<!--Basic information-->
pynusinov is a Python3 implementation of models of the ultraviolet radiation spectra from the Sun described by A.A. Nusinov. 
The EUV model describes variations in the 5–105 nm spectral region, which are responsible for the ionization of the main components of the earth’s atmosphere.
The FUV model describes the flux changes in the 115–242 nm region, which determines heating of the upper atmosphere and the dissociation of molecular oxygen.
The input parameter for both models is the intensity of the photon flux in the Lyman-alpha line, which has been measured for decades. 
Using this parameter allows you to calculate solar radiation fluxes for any period of time.

If you use pynusinov or Nusinov's EUV/FUV models directly or indirectly, please, cite in your research the following paper:

1. Nusinov, A.A., Kazachevskaya, T.V., Katyushina, V.V. - Solar Extreme and Far Ultraviolet Radiation Modeling for Aeronomic
Calculations. Remote Sens. 2021, 13, 1454. https://doi.org/10.3390/rs13081454

## User's guide

<!--Users guide-->

### Installation

The following command is used to install the package:

```
python -m pip install pynusinov
```

pynusinov is the name of the package.

The package contains two classes: Euvt2021 and Fuvt2021.

### Fuvt2021

Implementation of the Nusinov model for calculating the spectrum of far ultraviolet radiation from the Sun (FUV)
in the wavelength range 115-242 nm. The model is based on the idea of a linear dependence of radiation fluxes in
1 nm wide intervals on the intensity in the Lyman-alpha hydrogen line (l = 121.6 nm).

Input parameters:
- flow in the Lyman-alpha line N<sub>La</sub> in lac unit (1 lac = 1 * 10<sup>15</sup> m<sup>-2</sup> s<sup>-1</sup>). 
You can set one or more N<sub>La</sub> values. Use a list to pass multiple values.

Output parameters:
- xarray dataset.

```
<xarray.Dataset> Size: 4kB
Dimensions:           (band_center: 127, lac: 1, band_number: 127)
Coordinates:
  * lac               (lac) float64 8B <Input Lyman alpha values>
  * band_center       (band_center) float64 1kB 115.5 116.5 ... 240.5 241.5
  * band_number       (band_number) int32 508B 0 1 2 3 4 ... 122 123 124 125 126
Data variables:
    fuv_flux_spectra  (band_center, lac) float64 1kB <Output spectrum>
    lband             (band_number) int32 508B 115 116 117 118 ... 239 240 241
    uband             (band_number) int32 508B 116 117 118 119 ... 240 241 242
```

### Fuvt2021 usage example

- import the pynusinov package;
- create an instance of the Fuvt2021 class;
- perform calculations with the created instance.

This class contains two methods for calculating the spectrum:
- get_spectral_bands() for calculating the spectrum in a wavelength interval;
- get_spectra() a method for unifying the use of a class with the Euvt2021 class.

1. get_spectral_bands()
```
# importing a package with the alias p
import pynusinov as p
# creating an instance of the Fuvt2021 class
ex = p.Fuvt2021()
# calculate the spectra values at N_La = 3.31 lac unit using get_spectral_bands()
spectra = ex.get_spectral_bands(3.31)
# output the resulting FUV-spectra
print(spectra['fuv_flux_spectra'])


<xarray.DataArray 'fuv_flux_spectra' (band_center: 127, lac: 1)> Size: 1kB
array([[1.0226240e+13],
       [1.3365010e+13],
...
       [4.5222314e+16],
       [5.3300029e+16]])
Coordinates:
  * lac          (lac) float64 8B 3.31
  * band_center  (band_center) float64 1kB 115.5 116.5 117.5 ... 240.5 241.5
```

If you need to calculate the spectrum for several N<sub>La</sub> values, pass them using a list:

```
# calculate the spectrum values at N_La_1 = 3.31 lac unit and N_La_2 = 7.12 lac unit using get_spectral_bands()
spectra = ex.get_spectral_bands([3.31, 7.12])
# output the resulting FUV-spectrum
print(spectra['fuv_flux_spectra'])


<xarray.DataArray 'fuv_flux_spectra' (band_center: 127, lac: 2)> Size: 2kB
array([[1.0226240e+13, 1.7099480e+13],
       [1.3365010e+13, 1.7826520e+13],
...
       [4.5222314e+16, 4.7239328e+16],
       [5.3300029e+16, 5.5418008e+16]])
Coordinates:
  * lac          (lac) float64 16B 3.31 7.12
  * band_center  (band_center) float64 1kB 115.5 116.5 117.5 ... 240.5 241.5
```

2. get_spectra()

This method is used to unify the use of the pynusinov package classes. get_spectra() internally calls the 
get_spectral_bands() method with the parameters passed to get_spectra().


### Euvt2021

Implementation of the Nusinov model for calculating the spectra of the extreme ultraviolet radiation of the Sun (EUV)
in the wavelength range of 10-105 nm. This model calculates the ultraviolet spectra for an individual wavelength or 
a wavelength interval. The model is based on the idea of a linear dependence of radiation fluxes in intervals
of unequal width on the intensity in the HeI helium line (l = 58.4 nm). 

Input parameters:
- flow in the Lyman-alpha line N<sub>La</sub> in lac unit (1 lac = 1 * 10<sup>15</sup> m<sup>-2</sup> s<sup>-1</sup>). 
You can set one or more N<sub>La</sub> values. Use a list to pass multiple values.

Output parameters:
- xarray dataset.

For calculations of the model by interval wavelength and by wavelength interval xarray is different:

```
# wavelength interval
<xarray.Dataset> Size: 728B
Dimensions:           (band_center: 20, lac: 1, band_number: 20)
Coordinates:
  * lac               (lac) float64 8B <Input Lyman alpha values>
  * band_center       (band_center) float64 160B 7.5 12.5 17.5 ... 97.5 102.5
  * band_number       (band_number) int32 80B 0 1 2 3 4 5 ... 14 15 16 17 18 19
Data variables:
    euv_flux_spectra  (band_center, lac) float64 160B <Output spectrum>
    lband             (band_number) int64 160B 5 10 15 20 25 ... 80 85 90 95 100
    uband             (band_number) int64 160B 10 15 20 25 30 ... 90 95 100 105


# wavelength line
<xarray.Dataset> Size: 456B
Dimensions:           (line_wavelength: 16, lac: 1, line_number: 16)
Coordinates:
  * lac               (lac) float64 8B <Input Lyman alpha values>
  * line_wavelength   (line_wavelength) float64 128B 25.6 28.4 ... 102.6 103.2
  * line_number       (line_number) int32 64B 0 1 2 3 4 5 ... 10 11 12 13 14 15
Data variables:
    euv_flux_spectra  (line_wavelength, lac) float64 <Output spectrum>
    wavelength        (line_number) float64 128B 25.6 28.4 30.4 ... 102.6 103.2
```

### Euvt2021 usage example

This class contains two methods for calculating the spectrum:
- get_spectral_bands() for calculating the spectrum in a wavelength interval;
- get_spectral_lines() for calculating the spectrum for an individual wavelength.

The steps of work are similar to the steps described for the Fuvt2021 class. 

Below is an example of working with the Euvt2021 class:

1. get_spectral_bands()
```
# importing a package with the alias p
import pynusinov as p
# creating an instance of the Euvt2021 class
ex = p.Euvt2021()
# calculate the spectrum values at N_La = 3.31 lac unit using get_spectral_bands()
spectrum = ex.get_spectral_bands(3.31)
# output the resulting EUV-spectra
print(spectrum['euv_flux_spectra'])


<xarray.DataArray 'euv_flux_spectra' (band_center: 20, lac: 1)> Size: 160B
array([[2.52122700e+12],
       [2.59186240e+12],
...
       [5.73289352e+13],
       [9.57620734e+13]])
Coordinates:
  * lac          (lac) float64 8B 3.31
  * band_center  (band_center) float64 160B 7.5 12.5 17.5 ... 92.5 97.5 102.5
```

If you need to calculate the spectrum for several N<sub>La</sub> values, pass them using a list:

```
# calculate the spectrum values at N_La_1 = 3.31 lac unit and N_La_2 = 7.12 lac unit using get_spectral_bands()
spectra = ex.get_spectral_bands([3.31, 7.12])
# output the resulting EUV-spectrum
print(spectra['euv_flux_spectra'])


<xarray.DataArray 'euv_flux_spectra' (band_center: 20, lac: 2)> Size: 320B
array([[2.52122700e+12, 3.44494080e+13],
       [2.59186240e+12, 2.14175296e+13],
...
       [5.73289352e+13, 1.07909581e+14],
       [9.57620734e+13, 2.62794074e+14]])
Coordinates:
  * lac          (lac) float64 16B 3.31 7.12
  * band_center  (band_center) float64 160B 7.5 12.5 17.5 ... 92.5 97.5 102.5
```

2. get_spectral_lines()
```
# importing a package with the alias p
import pynusinov as p
# creating an instance of the Euvt2021 class
ex = p.Euvt2021()
# calculate the spectrum values at N_La = 3.31 lac unit using get_spectral_lines()
spectra = ex.get_spectral_lines(3.31)
# output the resulting EUV-spectra
print(spectra['euv_flux_spectra'])


<xarray.DataArray 'euv_flux_spectra' (line_wavelength: 16, lac: 1)> Size: 128B
array([[ 1.07475700e+13],
       [-3.48013400e+11],
...
       [ 3.01426805e+13],
       [ 5.22986620e+12]])
Coordinates:
  * lac              (lac) float64 8B 3.31
  * line_wavelength  (line_wavelength) float64 128B 25.6 28.4 ... 102.6 103.2
```

If you need to calculate the spectrum for several N<sub>La</sub> values, pass them using a list:

```
# calculate the spectrum values at N_La_1 = 3.31 lac unit and N_La_2 = 7.12 lac unit using get_spectral_lines()
spectra = ex.get_spectral_lines([3.31, 7.12])
# output the resulting EUV-spectrum
print(spectra['euv_flux_spectra'])


<xarray.DataArray 'euv_flux_spectra' (line_wavelength: 16, lac: 2)> Size: 256B
array([[ 1.07475700e+13,  6.92348800e+13],
       [-3.48013400e+11,  1.29777664e+13],
...
       [ 3.01426805e+13,  9.21014720e+13],
       [ 5.22986620e+12,  1.51018048e+13]])
Coordinates:
  * lac              (lac) float64 16B 3.31 7.12
  * line_wavelength  (line_wavelength) float64 128B 25.6 28.4 ... 102.6 103.2
```

3. get_spectra()

This method combines the get_spectral_bands() and get_spectral_lines() methods. The method returns a tuple (bands, lines), 
the first element is the flux in intervals, the second is the flux in individual lines. 
