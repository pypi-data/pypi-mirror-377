[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5179973.svg)](https://doi.org/10.5281/zenodo.5179973)

PyCBG is a Python tool that should be helpful in running [CB-Geo MPM](https://forge.inrae.fr/mpm-at-recover/cbgeo) (in our forked version, and possibly also for what concerns its [initial version](https://github.com/cb-geo/mpm)) simulations, either for generating expected input files at the preprocessing stage, or for postprocessing results.

Install PyCBG
=============

`pycbg` can be installed using `pip` (the latter being itself installed on Debian-based systems with `sudo apt install python3-pip`) with different manners depending on the desired version.

## Release version from PyPI

The last release of PyCBG on [PyPI](https://pypi.org/) can be simply installed using:

```console
$ python3 -m pip install pycbg
```

Installation automatically includes the following dependencies: 
 - `numpy`
 - `gmsh`
 - `pandas`
 - `matplotlib`
 - `versioneer`
 - `pyreadline`
 - `sphinx` (at least version `3.3.1`)
 - `sphinx_rtd_theme`

## Developer version

If you want to install a specific version of PyCBG (e.g., the most recent one), you can download the sources for that specific version before running the installation.

**Downloading PyCBG**

If you have SSH access to the [INRAE GitLab instance](https://forge.inrae.fr), you can download the sources in a read-write access with `git`:
```console
$ git clone git@forge.inrae.fr:mpm-at-recover/pycbg.git
```

Without SSH access, you can download it from command line with
```console
$ git clone https://forge.inrae.fr/mpm-at-recover/pycbg.git
```
or manually from [the corresponding repository](https://forge.inrae.fr/mpm-at-recover/pycbg).

**Installing PyCBG**

From the root of the `pycbg` directory (the one you just downloaded), type the following command: 

```console
$ python3 -m pip install -e .
```

> **Note:**
>
> The `-e` option (edit mode) is necessary in order to access all features of PyCBG, e.g. the documentation build using `pycbg -d`. Basically, `pip` will create a `pycbg.egg-link` file in the installation directory (something like `~/.local/lib/python3.10/site-packages`) which refers to the actual path of PyCBG sources on your computer. As a consequence, any modification to the source file is effective immediately, without re-installing PyCBG. 

**Testing PyCBG**

PyCBG includes a testing module based on the built-in [Python module `unittest`](https://docs.python.org/3/library/unittest.html) and can be run using the following command:
```console
$ cd pycbg_package
$ python3 -m unittest -v src.tests.test_preprocessing
```
> **Notes:**
> - the optional `-v` flag increases the verbosity.
> - alternatively, tests can be run from the command line (see paragraph below).

These tests will fail if, with respect to a reference version of PyCBG:
 - the type of a preprocessing class' attribute has changed
 - the content of any input file (among `mesh.txt`, `particles.txt`, `entity_sets.json`, and `input_file.json`) isn't the one expected
 - an error occurred during the execution of the testing scripts

They will not fail if, with respect to a reference version of PyCBG:
 - all class attributes haven't changed for any of the parameter sets tested
 - the content of all input files is the exactly the same as the one expected
 - the `input_file.json` file has new parameters, in which case a warning will be displayed


Command line usage
==================

While PyCBG is essentially a Python module, installation also provides a new Python executable `pycbg` (`pip` should automatically install it inside a directory in your `$PATH`) with all PyCBG features being already imported. The executable may serve to create a PyCBG interactive session, build the documentation or get PyCBG's version.

## Complete description
```console
$ pycbg -h
usage: pycbg [-h] [-v] [-V] [-p] [-i] [-n] [-d [BUILD_DIR]] [-t] [PYCBG_SCRIPT]

Manage CB-Geo MPM simulations using PyCBG Python module

positional arguments:
  PYCBG_SCRIPT          pycbg script to be run. By default, the following import lines are added at the top
                        of the file: `from pycbg.preprocessing import *`, `from pycbg.postprocessing import
                        *` and `from pycbg.MPMxDEM import *`. To deactivate this behaviour, use the -n (or
                        --no-import) option

options:
  -h, --help            show this help message and exit
  -v, --version         print pycbg version
  -V, --all-version     print all pycbg version information, including the ones of its dependencies
  -p, --pip-show        alias for `pip show pycbg`
  -i, --interactive     run in an interactive IPython session. Using both the -i and -n options simply
                        creates a IPython interactive session
  -n, --no-import       deactivates automatic import of pycbg
  -d [BUILD_DIR], --build-doc [BUILD_DIR]
                        build pycbg's documentation in BUILD_DIR, its path being relative to the current
                        working directory. If BUILD_DIR isn't specified, it will be set to
                        `${PWD}/pycbg_doc`. If BUILD_DIR is `..`, it is set to `../pycbg_doc`. If -d and
                        PYCBG_SCRIPT are specified, the documentation is build before running the script
  -t, --tests           run unit tests for the current installation of PyCBG. If specified along with other
                        options, tests will be performed first
```

## Usage
One can easily run a PyCBG script:
```console
$ pycbg my_script.py
```

Or experiment with PyCBG's functions and classes:
```console
$ pycbg -i
Python 3.9.7 (default, Sep  3 2021, 12:45:31) 
Type 'copyright', 'credits' or 'license' for more information
IPython 8.0.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: mesh = Mesh(...)
```

## Get version
To get the installed version of PyCBG, simply run:
```console
$ pycbg -v
v1.0.2+107.g3997bd9
```

This PEP440-compliant version string has the following format: `TAG[+DIST.gHASH[.dirty]]`, where:
 - `TAG` is the most recent Git tag (in the above, `v1.0.2`),
 - `DIST` is the number of commits since that last tag, only present if commits were made after the last tag (in the above, `107`),
 - `HASH` is the short Git commit SHA1, only present if commits were made after the last tag (in the above, `3997bd9`),
 - `.dirty` is the suffix appended to the string in the case of uncommitted local changes in any of the Git-controlled files. 

> **More information:**
> 
> PyCBG version management is handled with the [`python-versioneer` project](https://github.com/python-versioneer/python-versioneer/tree/master).
> See [this detailed description](https://github.com/python-versioneer/python-versioneer/blob/master/details.md#how-do-i-select-a-version-style) of various version formatting styles, or [these comments](https://forge.inrae.fr/mpm-at-recover/pycbg/-/blob/91fa38e9f3d27fe5df3702585daa13cf391806a1/versioneer.py#L136-152) in PyCBG project files.



Documentation
=============

## On GitLab Pages

The documentation for the `main` branch is available at [https://mpm-at-recover.pages-forge.inrae.fr/pycbg/](https://mpm-at-recover.pages-forge.inrae.fr/pycbg/). It is updated each time the CI pipeline job `pages` (stage `post-install`) runs successfully on this branch.

## On ReadTheDocs

The latest build of the documentation at [ReadTheDocs](https://readthedocs.org/) is available online [here](https://pycbg.readthedocs.io/en/latest/). If nothing appears under `Classes overview` left of your screen, please reload the page (this is probably a small bug on ReadTheDocs).

## Local build using the command line

The documentation can also be built locally using `sphinx`:
```
pycbg -d
```

This will create a folder in the current working directory named `pycbg_doc` containing the built documentation.
It can then be accesed by opening `pycbg_doc/_build/html/index.html` in your browser.

The `pycbg_doc` folder name can be modified if necessary when executing the bash script:
```
pycbg -d my_folder_name
```

> **Note:** 
> 
> In the background `pycbg -d` is equivalent to executing the source file `build_doc.sh`

Citation
========

In case PyCBG is useful to your research, please consider to include the following reference in your publications:

Duverger Sacha & Duriez Jérôme (2021) PyCBG, a python module for generating CB-Geo MPM input files (1.1.4). Zenodo. https://doi.org/10.5281/zenodo.5179973

