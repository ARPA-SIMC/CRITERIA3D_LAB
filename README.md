# CRITERIA3D Lab
Python version of CRITERIA-3D agro-hydrological model, it allows to configure 1D, 2D and simple 3D hydrological experiments.
  
- Numerical solution for three-dimensional water flow in the soil, with management of different soil horizons.  
- Soil water retention curves: Campbell, modified Van Genucthen.  
- Sink/source: evapotranspiration, precipitation, drip irrigation.  
- Boundary conditions: surface runoff, free drainage, prescribed total potential (watertable), no flux.
- The crop coefficient varies based on monthly leaf area index (LAI).
- Other crop parameters: maximum crop coefficient (Kcmax), readily available water fraction (fRAW), shape factors of the root system.
- Input: hourly data of air temperature, precipitation, solar radiation, air humidity, wind speed, drip irrigation.
- Output (water content / water potential) at specific points in the domain.
- The software can save states and assimilate observed water potential values.  


![](https://github.com/ARPA-SIMC/CRITERIA3D_LAB/blob/main/doc/criteria3d.png)

## Requirements
- Cython
- VPython
- numpy  
- scipy  
- pandas

## How to compile solverC.pyx
It requires the Cython library and a C compiler, on Windows you can use the MinGW or Visual Studio compilers.
>cd src  
>python cythonSetup.py build_ext --inplace
 
If the Cython library is missing, you can run the code by setting this variable in the **commonConst.py** module:
> CYTHON = False


## Authors
- Fausto Tomei    <ftomei@arpae.it>
- Joseph Giovanelli <josephgiovanelli@gmail.com>
- Marco Bittelli  <marco.bittelli@unibo.it>

## References
Bittelli, M., Campbell, G. S., & Tomei, F. (2015). Soil physics with Python: transport in the soil-plant-atmosphere system. OUP Oxford.
