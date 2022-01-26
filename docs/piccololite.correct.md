<!-- markdownlint-disable -->

# <kbd>module</kbd> `piccololite.correct`
Radiometric Correction 



---

## <kbd>class</kbd> `RadiometricCorrection`
Class for performing calibration transformation of Piccolo data. 

The order of operations is (1) Dark Signal estimation (2) Non Linearity Correction (3) Dark Signal subtraction (4) integration time normalisation (5) application of Gain (from calibration files). 

### 1. Dark Signal Estimation 

As it has been observed that the QE Pro used in our lab group does not have adequate optical dark pixels, the dark signal is estimated from the reference file rather than from the optical dark pixels. By default the first dark file will be used. 

### 2. Non Linearity Correction 

This is a linear transformation:  corrected = dark + (raw - dark) / f(raw - dark) where f is a polynomial specified in the header 

### 3. Dark Signal Subtraction 

This is a linear transformation:  subtracted = corrected - dark 

### 4. Integration Normalisation 

This is a linear transformation:  normalised = subtracted / integration_time 

### 5. Gain adjustment 

Conversion of DN to calibrated units using a calibration file  calibrated = normalised * gain 

### <kbd>method</kbd> `__init__`

```python
__init__(cal_file_paths, dark_reference=None)
```



**Args:**
 
 - <b>`cal_file_paths`</b> (list):  a list of filepaths with the identifier  in the filename (i.e. FLMS01691_cals_.csv). Input files must  have wvl, dnw and upw fields. 
 - <b>`dark_reference`</b> (str):  If None, the average of all dark files in the  sequence will be used (default). A filename can be supplied to  specify a single file 




---

### <kbd>method</kbd> `get_calibration`

```python
get_calibration(spectrum)
```

Returns the calibration array 



**Args:**
 
 - <b>`spectrum`</b>:  DataArray with Direction and name parameters 

---

### <kbd>method</kbd> `get_dark_signal`

```python
get_dark_signal(spectrum)
```

Returns the dark signal 



**Args:**
 
 - <b>`spectrum`</b>:  DataArray with Direction and name parameters 

---

### <kbd>method</kbd> `set_dark_reference`

```python
set_dark_reference(piccolo_sequence, key=None)
```

Loads the dark reference from a piccolo_sequence. 

By default the first file is used, unless key specified. 



**Args:**
 
 - <b>`piccolo_sequence`</b>:  A piccolo sequence dictionary 
 - <b>`key`</b> (str):  filename of .pico to use for dark signal 

---

### <kbd>method</kbd> `transform`

```python
transform(piccolo_sequence)
```

Apply calibration transform 



**Args:**
 
 - <b>`piccolo_sequence`</b>:  open data files 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
