
# OSL_CGCD

Program for the deconvolution of OSL curves using the CGCD method.

## Author
**EDWIN JOEL PILCO QUISPE**  
Email: edwinpilco10@gmail.com

## Description
This package allows you to analyze and deconvolute OSL (Optically Stimulated Luminescence) curves using the CGCD method. It includes tools to process Excel files, fit curves, and save results.

## Installation
You can install the package from PyPI:

```bash
python -m pip install OSL_CGCD
```

Or install it locally from the generated `.whl` file:

```bash
cd dist
python -m pip install osl_cgcd-0.1.1-py3-none-any.whl
```

## Basic Usage
Create a script and use the included module:

```python
from OSL_CGCD import modulo
# Example: run analysis functions
```

## Package Structure

- `modulo.py`: Deconvolution of OSL curves from Excel files. Allows you to select the file to process and saves results in the `deconvolution_results` folder. Combines results from several columns into a single continuous file for further analysis.

## Example Execution
1. Run `modulo.py` to process your Excel file:
	```bash
	python src/OSL_CGCD/modulo.py
	```

## Publishing to PyPI
To publish a new version:
1. Update the version in `setup.py`.
2. Build the package:
	```bash
	python -m build
	```
3. Upload the package:
	```bash
	python -m twine upload dist/*
	```

## Requirements
- Python >= 3.6
- Recommended packages: numpy, scipy, matplotlib, pandas, prettytable

## License
This project is free to use for academic and personal purposes.
