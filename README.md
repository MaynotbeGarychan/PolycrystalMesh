# PolycrystalMesh
Tools to map grain structure from MTEX Toolbox to shell mesh, and then drag 2D shell to solid

### Author: 
Jiawei CHEN, Materials forming and processing lab, Institute of industrial science, the University of Tokyo

### Example
1. Retangle region

![Retangle region](https://github.com/MaynotbeGarychan/PolycrystalMesh/tree/dev/web/example_retangle_region.jpg)

### How to use?
1. Run the ./matlab_script/make_input.m with MTEX Toolbox to 
partition the grain and making some input information for the next step.
2. Make a keyword file for a shell mesh.
3. Run the ./Script.py to partition the shell mesh and drag it into
solid mesh.

### Supported format
1. LS-Dyna keyword file

(It's welcomed to provide other format of io for this project.)

### Citation
If you use this code, please cite this paper