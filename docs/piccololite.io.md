<!-- markdownlint-disable -->

# <kbd>module</kbd> `piccololite.io`
Piccolo file (.pico) input/output 


---

## <kbd>function</kbd> `read_piccolo_file`

```python
read_piccolo_file(piccolo_data, assign_coords=False)
```

Read in a piccolo data file. 



**Args:**
 
 - <b>`piccolo_data`</b>:  Can be 1. a valid filepath 2. json-like string  containing piccolo data 
 - <b>`assign_coords`</b>:  a list of coords to assign to new dimensions 


---

## <kbd>function</kbd> `read_piccolo_sequence`

```python
read_piccolo_sequence(files, *args, **kwargs)
```

Read a directory of .pico files or an explicit list. 

Args and Kwargs can be supplied to read_piccolo_file 



**Args:**
 
 - <b>`files`</b>:  Can be a list or path to a directory of .pico files 


---

## <kbd>function</kbd> `sequence_to_datasets`

```python
sequence_to_datasets(piccolo_sequence, clean_metadata=True)
```

Converts a Piccolo sequence dictionary to xarray Datasets. 

Each dataset represents a single instrument. 



**Args:**
 
 - <b>`piccolo_sequence`</b>:  nested dictionary of piccolo spectra. 
 - <b>`clean_metadata`</b> (bool):  if True, attempts to clean metadata  so that the dataset is safe for writing to netcdf 



**Returns:**
 dictionary of xarray Datasets keyed by instrument serial 


---

## <kbd>function</kbd> `sequence_to_netcdf`

```python
sequence_to_netcdf(piccolo_sequence, fname)
```

Converts a Piccolo sequence dictionary to NetCDF files. 

Each file represents a single instrument. 



**Args:**
 
 - <b>`piccolo_sequence`</b>:  nested dictionary of piccolo spectra.  Must be in the form [filename][instrument][downwelling]  or a dictionary of xarray Datasets 
 - <b>`fname`</b> (str):  destination filename 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
