Welcome to pycbg's documentation!
=================================

This module helps configuring MPM simulations for `CB-Geo MPM <https://github.com/cb-geo/mpm>`_: a simple Python script can generate the input files required by CB-Geo MPM (see :ref:`Preprocessing`). The results of the simulation can also be imported in Python using pycbg (see :ref:`Postprocessing`). This documentation should be used alongside `CB-Geo MPM's documentation <https://mpm.cb-geo.com/#/>`_.

In case PyCBG is useful to your research, please consider to include the following reference in your publications:

Duverger Sacha & Duriez Jérôme (2021) PyCBG, a python module for generating CB-Geo MPM input files (1.1.4). Zenodo. https://doi.org/10.5281/zenodo.5179973


.. Preprocessing:

----

Preprocessing
=============

Preprocessing a MPM simulation for CB-Geo consists in creating several input files:

 - a mesh file, where the positions of all nodes and their interconnections are described. Pycbg saves it under the name `mesh.msh`. Can be created using the :py:class:`Mesh<pycbg.preprocessing.Mesh>` class.
 - a particles file, where the initial positions of all material points are specified. Pycbg saves it under the name `particles.txt`. Can be created using the :py:class:`Particles<pycbg.preprocessing.Particles>` class.
 - an entity sets file (if entity sets are defined), where all entity sets are defined using entities' ids. An entity can be a node, a particle or a cell. Pycbg saves it under the name `entity_sets.txt`. Can be created using the :py:class:`EntitySets<pycbg.preprocessing.EntitySets>` class.

Instantiating the :py:class:`Simulation<pycbg.preprocessing.Simulation>` class involves creating :py:class:`Mesh<pycbg.preprocessing.Mesh>`, :py:class:`Particles<pycbg.preprocessing.Particles>`, :py:class:`Materials<pycbg.preprocessing.Materials>` and :py:class:`EntitySets<pycbg.preprocessing.EntitySets>` objects and should be enough to prepare a simulation.

Classes overview
----------------

.. currentmodule:: pycbg.preprocessing

.. autosummary::
   :nosignatures:
   :recursive:
   :template: custom-class-template.rst
   :toctree: stubs

   Mesh
   Particles
   EntitySets
   Materials
   Simulation
   setup_batch

----

Postprocessing
==============

While CB-Geo MPM outputs results in a number of files being often generated at each save iteration, the :py:class:`ResultsReader<pycbg.postprocessing.ResultsReader>` is provided for a seamless processing of those data.

.. currentmodule:: pycbg.postprocessing

.. autosummary::
   :nosignatures:
   :recursive:
   :template: custom-class-template.rst
   :toctree: stubs

   ResultsReader
   load_batch_results
   
----

MPMxDEM
==============

This submodule can be use to setup everything necessary for the MPMxDEM coupling's RVE script.

.. currentmodule:: pycbg.MPMxDEM

.. autosummary::
   :nosignatures:
   :recursive:
   :template: custom-class-template.rst
   :toctree: stubs

   setup_yade
   DefineCallable
   
----

Basic utility
==============

Warnings, exceptions and some utility functions are available directly with the `pycbg` namespace.

.. currentmodule:: pycbg

.. autosummary::
   :nosignatures:
   :recursive:
   :template: custom-class-template-2.rst
   :toctree: stubs

   NewFeatureWarning
   VersionWarning
   VersionError
   Version
   printAllVersions
   pycbg.versions
   
----

Version
=======

This documentation was built from version |version|_, its source code is available at:

|gitlab_link|

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
