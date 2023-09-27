# CRITERIA3D Lab
Python version of CRITERIA-3D agro-hydrological model
![](https://github.com/ARPA-SIMC/CRITERIA3D_LAB/blob/main/doc/criteria3d.png)

## Requirements
Cython
vpython
numpy
scipy
pandas
tkinter

## How to compile solverC.pyx
Requires Cython and a C compiler.
On Windows you can use the MinGW or Visual Studio compiler
cd src
python cythonSetup.py build_ext --inplace

## Authors
- Fausto Tomei    <ftomei@arpae.it>
- Marco Bittelli  <marco.bittelli@unibo.it>
- Joseph Giovanelli <josephgiovanelli@gmail.com>

## References
Bittelli, M., Campbell, G. S., & Tomei, F. (2015). Soil physics with Python: transport in the soil-plant-atmosphere system. OUP Oxford.
