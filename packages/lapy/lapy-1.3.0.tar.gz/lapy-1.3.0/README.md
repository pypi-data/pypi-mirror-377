[![PyPI version](https://badge.fury.io/py/lapy.svg)](https://pypi.org/project/lapy/)
# LaPy

LaPy is an open-source Python package for differential geometry on triangle
and tetrahedra meshes. It includes an FEM solver to estimate the Laplace,
Poisson or Heat equations. Further functionality includes the computations
of gradients, divergence, mean-curvature flow, conformal mappings, 
geodesics, ShapeDNA (Laplace spectra), and IO and plotting methods. 

LaPy is written purely in Python 3 without sacrificing speed as almost all
loops are vectorized, drawing upon efficient and sparse mesh data structures.

## Contents:

- **TriaMesh**: a class for triangle meshes offering various operations, such as
  fixing orientation, smoothing, curvature, boundary, quality, normals, and
  various efficient mesh datastructures (edges, adjacency matrices). IO from
  OFF, VTK and other formats.
- **TetMesh**: a class for tetrahedral meshes (orientation, boundary, IO ...)
- **Solver**: a class for linear FEM computation (Laplace stiffness and mass
  matrix, fast and sparse eigenvalue solver, anisotropic Laplace, Poisson)
- **io**: module for IO of vertex functions and eigenvector files
- **diffgeo**: module for gradients, divergence, mean curvature flow, etc.
- **heat**: module for heat kernel and diffusion
- **shapedna**: module for the ShapeDNA descriptor of surfaces and solids
- **plot**: module for interactive visualizations (wrapping plotly)

## Usage:

The LaPy package is a comprehensive collection of scripts, so we refer to the
'help' function and docstring of each module / function / class for usage info.
For example:

```
import lapy as lp
help(lp.TriaMesh)
help(lp.Solver)
```

In the `examples` subdirectory, we provide several Jupyter notebooks that
illustrate prototypical use cases of the toolbox.

## Installation:

Use the following code to install the latest release of LaPy into your local
Python package directory:

`python3 -m pip install lapy`

Use the following code to install the dev package in editable mode to a location of
your choice:

`python3 -m pip install --user --src /my/preferred/location --editable git+https://github.com/Deep-MI/Lapy.git#egg=lapy`

Several functions, e.g. the Solver, require a sparse matrix decomposition, for which either the LU decomposition (from scipy sparse, default) or the faster Cholesky decomposition (from scikit-sparse cholmod, recommended) can be used. If the parameter flag use_cholmod is True, the code will try to import cholmod from the scikit-sparse package. If this fails, an error will be thrown. If you would like to use cholmod, you need to install scikit-sparse separately, as pip currently cannot install it (conda can). scikit-sparse requires numpy and scipy to be installed separately beforehand.

## API Documentation

The API Documentation can be found at https://deep-mi.org/LaPy .

## References:

If you use this software for a publication please cite both these papers:

**[1]** Laplace-Beltrami spectra as 'Shape-DNA' of surfaces and solids. Reuter M, Wolter F-E, Peinecke N. Computer-Aided Design. 2006;38(4):342-366. http://dx.doi.org/10.1016/j.cad.2005.10.011

**[2]** BrainPrint: a discriminative characterization of brain morphology. Wachinger C, Golland P, Kremen W, Fischl B, Reuter M. Neuroimage. 2015;109:232-48. http://dx.doi.org/10.1016/j.neuroimage.2015.01.032 http://www.ncbi.nlm.nih.gov/pubmed/25613439

Shape-DNA [1] introduces the FEM methods and the Laplace spectra for shape analysis, while BrainPrint [2] focusses on medical applications.

For Geodesics please also cite:

[3] Crane K, Weischedel C, Wardetzky M. Geodesics in heat: A new approach to computing distance based on heat flow. ACM Transactions on Graphics. https://doi.org/10.1145/2516971.2516977

For non-singular mean curvature flow please cite:

[4] Kazhdan M, Solomon J, Ben-Chen M. 2012. Can Mean-Curvature Flow be Modified to be Non-singular? Comput. Graph. Forum 31, 5, 1745–1754.
https://doi.org/10.1111/j.1467-8659.2012.03179.x

For conformal mapping please cite:

[5] Choi PT, Lam KC, Lui LM. FLASH: Fast Landmark Aligned Spherical Harmonic Parameterization for Genus-0 Closed Brain Surfaces. SIAM Journal on Imaging Sciences, vol. 8, no. 1, pp. 67-94, 2015. https://doi.org/10.1137/130950008

We invite you to check out our lab webpage at https://deep-mi.org
