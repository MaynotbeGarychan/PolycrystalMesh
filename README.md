# PolycrystalMesh
Tools to map grain structure from MTEX Toolbox to shell mesh, and then drag 2D shell to solid

## Example
1. Retangle region (./example/retangle_region)

![Retangle region](https://github.com/MaynotbeGarychan/PolycrystalMesh/blob/dev/web/example_retangle_region.jpg?raw=true)

2. More complex geometry is coming soon.

## Usage
1. Run the ./matlab_script/make_input.m with MTEX Toolbox to 
partition the grain and making some input information for the next step.
2. Make a keyword file for a shell mesh.

   (Note: Only 4-node Quad shell element is supported, this mesh should be renumbered using LSPP before mapping.)
3. Run the ./Script.py to partition the shell mesh and drag it into
solid mesh.

   
## Citation
Jiawei CHEN. (2023). PolycrystalMesh. GitHub. https://github.com/MaynotbeGarychan/PolycrystalMesh