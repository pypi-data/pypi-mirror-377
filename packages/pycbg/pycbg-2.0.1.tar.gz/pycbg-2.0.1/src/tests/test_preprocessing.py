import unittest, warnings
import os, shutil, pathlib, json, sys
import itertools as it

if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the src/tests/test_preprocessing.py script")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pycbg import preprocessing as ppc

import numpy as np

def load_json(filename):
    with open(filename, 'r') as fil: data_dict = json.load(fil)
    for key, val in data_dict.items():
        if isinstance(val, list): data_dict[key] = np.array(val)
    return data_dict

class TestMesh(unittest.TestCase):
    def load_mesh_file(self, mesh_file):
        """Loads mesh file into a dictionary containing relevant values
        """
        # Load mesh file
        if not os.path.isfile(mesh_file): raise FileNotFoundError(f"{mesh_file} doesn't exist, it couldn't be loaded")
        with open(mesh_file, 'r') as fil: lines = fil.readlines()
        
        # Extract data
            ## Number of nodes and cells
        nnodes, ncells = [int(i) for i in lines[0][:-1].split("\t")]
            ## Nodes positions
        nodes = np.array([[float(i) for i in line[:-2].split(" ")] for line in lines[1:nnodes+1]])
            ## Cells, as list of node IDs
        cells = np.array([[int(i) for i in line[:-1].split(" ")] for line in lines[nnodes+1:]])
        
        return {"nnodes": nnodes, "ncells": ncells, "nodes": nodes, "cells": cells}
    
    def check_mesh_file(self, mesh_params, nnodes, ncells, npos, cells, rm_dir=True):
        """Compare the values written to the mesh file with the one ~predicted when calling this function 
        """
        # Create the mesh
        mesh = ppc.Mesh(**mesh_params)
        
        # Check the attributes of the mesh
        self.check_mesh_attributes(mesh)
        
        # Check if the mesh file was created
        self.assertTrue(os.path.isfile(self.sim_dir + "/mesh.txt"), "Mesh file creation failed")
        
        # Check data inside the mesh file
        mesh_data = self.load_mesh_file(self.sim_dir + "/mesh.txt")
            ## Number of nodes and cells
        self.assertEqual(mesh_data["nnodes"], nnodes, "Number of nodes in mesh file wrong ({:d}, expected {:d})".format(mesh_data["nnodes"], nnodes))
        self.assertEqual(mesh_data["ncells"], ncells, "Number of cells in mesh file wrong ({:d}, expected {:d})".format(mesh_data["ncells"], ncells))
        
            ## Nodes positions
        nodes_equal = (mesh_data["nodes"]==npos).all()
        self.assertTrue(nodes_equal, "Nodes positions in mesh file wrong")
        
            ## Cells
        cells_equal = (mesh_data["cells"]==cells).all()
        self.assertTrue(cells_equal, "Cells (list of nodes IDs) in mesh file wrong")
        
        # Optionally, remove the simulation directory
        if rm_dir: shutil.rmtree(self.sim_dir)
        
    def check_mesh_attributes(self, mesh):
        """Checks that the attributes of the mesh have the right type, and valid value for some 

        Args:
            mesh (pycbg.preprocessing.Mesh): Mesh object whose attributes will be checked
        """
        # Nodes and cells
        self.assertIsInstance(mesh.nodes, np.ndarray, f"`node` attribute is of type {type(mesh.nodes)} while it should be of type {np.ndarray}")
        self.assertIsInstance(mesh.cells, np.ndarray, f"`cells` attribute is of type {type(mesh.cells)} while it should be of type {np.ndarray}")
        
        # Cell type
        self.assertIsInstance(mesh.cell_type, str, f"`cell_type` attribute is of type {type(mesh.cells)} while it should be of type {str}")
        cell_types_str = ", ".join([f"'{ct}'" for ct in self.cell_types])
        self.assertIn(mesh.cell_type, self.cell_types, f"`cell_type` is equal to '{mesh.cell_type}' while it should be among [{cell_types_str}]")
        
        # Dimensions
        self.assertIsInstance(mesh.n_dims, int, f"`n_dims` attribute is of type {type(mesh.n_dims)} while it should be of type {int}")
        self.assertIn(mesh.n_dims, [2, 3], f"`n_dims` is equal to '{mesh.n_dims}' while it should be among [2, 3]")
        self.assertIsInstance(mesh.dimensions, tuple, f"`dimensions` attribute is of type {type(mesh.dimensions)} while it should be of type {tuple}")
        for i_l, l in enumerate(mesh.dimensions): 
            self.assertIsInstance(l, float, f"`dimensions[{i_l}]` is of type {type(l)} while it should be of type {float}")
        self.assertIsInstance(mesh.l0, float, f"`l0` is of type {type(mesh.l0)} while it should be of type {float}")
        self.assertIsInstance(mesh.l1, float, f"`l1` is of type {type(mesh.l1)} while it should be of type {float}")
        if mesh.n_dims==3: self.assertIsInstance(mesh.l2, float, f"`l2` is of type {type(mesh.l2)} while it should be of type {float}")
        
        # Number of cells
        self.assertIsInstance(mesh.ncells, tuple, f"`ncells` is of type {type(mesh.ncells)} while it should be of type {tuple}")
        for i_nc, nc in enumerate(mesh.ncells): self.assertIsInstance(nc, int, f"`ncells[{i_nc}]` is of type {type(nc)} while it should be of type {int}")
        self.assertIsInstance(mesh.nc0, int, f"`nc0` is of type {type(mesh.nc0)} while it should be of type {int}")
        self.assertIsInstance(mesh.nc1, int, f"`nc1` is of type {type(mesh.nc1)} while it should be of type {int}")
        if mesh.n_dims==3: self.assertIsInstance(mesh.nc2, int, f"`nc2` is of type {type(mesh.nc2)} while it should be of type {int}")
        
        # Origin
        self.assertIsInstance(mesh.origin, tuple, f"`origin` is of type {type(mesh.origin)} while it should be of type {tuple}")
        for i_o, o in enumerate(mesh.origin): self.assertIsInstance(o, float, f"`origin[{i_o}]` is of type {type(o)} while it should be of type {int}")
        
        # Shape functions parameters
        if isinstance(mesh.save_shapefn, str):
            self.assertEqual(mesh.save_shapefn.lower(), "all", f"`save_shapefn` attribute is equal to {mesh.save_shapefn} while it should be either 'all' (case insensitive) or a list of ints")
        else:
            self.assertIsInstance(mesh.save_shapefn, list, f"`save_shapefn` attribute is of type {type(mesh.save_shapefn)} while it should be of type {list}")
            for i_nid, nid in enumerate(mesh.save_shapefn): 
                self.assertIsInstance(nid, int, f"`save_shapefn[{i_nid}]` is of type {type(nid)} while it should be of type {int}")
        self.assertIsInstance(mesh.shapefn_resolution, int, f"`shapefn_resolution` attribute is of type {type(mesh.shapefn_resolution)} while it should be of type {int}")
        self.assertIsInstance(mesh.save_shapefn_grad, bool, f"`save_shapefn_grad` attribute is of type {type(mesh.save_shapefn_grad)} while it should be of type {bool}")
        
        
        # Simulation parameters
        self.assertIsInstance(mesh.directory, str, f"`directory` attribute is of type {type(mesh.directory)} while it should be of type {str}")
        self.assertIsInstance(mesh.check_duplicates, bool, f"`check_duplicates` attribute is of type {type(mesh.check_duplicates)} while it should be of type {bool}")
        if mesh.round_decimal is not None:
            self.assertIsInstance(mesh.round_decimal, int, f"`round_decimal` attribute is of type {type(mesh.round_decimal)} while it should be of type {int}")
        self.assertIsInstance(mesh.params, dict, f"`params` attribute is of type {type(mesh.params)} while it should be of type {dict}")
    
    def setUp(self):
        # Put the simulation in the "tests" directory
            ## The following error should only be raised if there is a big mistake in this script
        if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the src/tests/test_preprocessing.py script")

            ## Extract the directory path from this script path and create the path of the simulation directory 
        self.test_dir = str(pathlib.Path(__file__).resolve()).rsplit("/", 1)[0]
        self.sim_dir = self.test_dir + "/test_mesh"
        
        # Define default values for mesh parameters, "dimensions" and "ncells" should always be overwritten
        self.default_params = {"dimensions": None, "ncells": None, "origin": (0.,0.,0.), "directory": "", "check_duplicates": True, "cell_type": "ED3H8", "round_decimal": None, "no_output": True, "save_shapefn": [], "shapefn_resolution": 25, "save_shapefn_grad": False}
        
        # Define the possible values for cell types
        self.cell_types = ['ED3H8', 'ED3H20', 'ED3H64G', 'ED2Q4', 'ED2Q8', 'ED2Q9', 'ED2Q16G', 'ED3H8P2B', 'ED2Q4P2B', 'ED3H8P3B', 'ED2Q4P3B']
        
        # Define expected values 
        self.expected_vals = load_json(self.test_dir + "/expected_results/mesh.json")
        
        # Define origin shifts to be tested
        self.o_shifts = [[1, 1, 1], [-1, -1, -1], [1000, 0, 0], [0, 1e-10, 0], [0, 0, 1/2]]
        
        # Define combinations of `dimensions` and `ncells` for larger tests
            ## 2D cases
        dim_vals_2d = [[1e-7]*2, [1/6]*2, [10000, 1e8]]
        ncells_vals_2d = [[2]*2, [10, 3], [4, 3], [1, 5]]
        self.comb_larger_2d = list(it.product(dim_vals_2d, ncells_vals_2d))
        
            ## 3D cases
        dim_vals_3d = [[1e-7]*3, [1/3]*3, [10000, 1e8, .5]]
        ncells_vals_3d = [[2]*3, [10, 3, 1], [4, 3, 2]]
        self.comb_larger_3d = list(it.product(dim_vals_3d, ncells_vals_3d))
    
    def test_specified_directory(self):
        """Check if the Mesh's `directory` feature works
        """
        mesh_params = {"dimensions": [1]*3, "ncells": [1]*3, "directory": self.sim_dir}
        with self.subTest(mesh_params=mesh_params):
            self.check_mesh_file(mesh_params, **self.expected_vals["default_3d"])
        
    def test_default_mesh(self):
        """Check that the mesh default parameters work with a mesh containing a unique unitary cell
        """
        # Define expected values for each number of dimensions
        dim_values = {2: self.expected_vals["default_2d"],
                      3: self.expected_vals["default_3d"]}
        
        # Test for each number of dimensions
        for key, expected_vals in dim_values.items():
            dim_str = f"{key}D case" # this string will serve as identifier if a test failure occurs
            with self.subTest(dim_str=dim_str):
                mesh_params = {"dimensions": [1]*key, "ncells": [1]*key, "cell_type": "ED3H8" if key==3 else "ED2Q4", "directory": self.sim_dir}
                self.check_mesh_file(mesh_params, rm_dir=False, **expected_vals)
        
    def test_origin_shift(self):
        """Check if the `origin` feature works
        """
        for o_shift in self.o_shifts:
            shift_str = "Origin shift [{:g}, {:g}, {:g}]".format(*o_shift) # this string will serve as identifier if a test failure occurs
            with self.subTest(shift_str=shift_str):
                # Construct the key to access expected results
                expected_vals_key = "origin_shift_{:g}_{:g}_{:g}".format(*o_shift)

                # Perform the check
                mesh_params = {"dimensions": [1]*3, "ncells": [1]*3, "directory": self.sim_dir, "origin": o_shift}
                self.check_mesh_file(mesh_params, rm_dir=False, **self.expected_vals[expected_vals_key])
                
    def test_larger_mesh(self):
        """Check if the Mesh class works with various (larger) meshes
        """
        # 2D cases
        for dim, ncells in self.comb_larger_2d:
            mesh_str = "dim: {:g}, {:g}; ncells: {:g}, {:g}".format(*dim, *ncells) # this string will serve as identifier if a test failure occurs
            with self.subTest(mesh_str=mesh_str):
                # Construct the key to access expected results
                expected_vals_key = "large_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells)
                
                # Perform the check
                mesh_params = {"dimensions": dim, "ncells": ncells, "directory": self.sim_dir, "cell_type": "ED2Q4"}
                self.check_mesh_file(mesh_params, rm_dir=False, **self.expected_vals[expected_vals_key])
        
        # 3D cases
        for dim, ncells in self.comb_larger_3d:
            mesh_str = "dim: {:g}, {:g}, {:g}; ncells: {:g}, {:g}, {:g}".format(*dim, *ncells) # this string will serve as identifier if a test failure occurs
            with self.subTest(mesh_str=mesh_str):
                # Construct the key to access expected results
                expected_vals_key = "large_{:g}_{:g}_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells)
                
                # Perform the check
                mesh_params = {"dimensions": dim, "ncells": ncells, "directory": self.sim_dir}
                self.check_mesh_file(mesh_params, rm_dir=False, **self.expected_vals[expected_vals_key])
    
    def tearDown(self):
        if os.path.isdir(self.sim_dir): shutil.rmtree(self.sim_dir)


class TestParticles(unittest.TestCase):
    def load_particles_file(self, particles_file):
        """Loads particles file into a dictionary containing relevant values
        """
        # Load particles file
        if not os.path.isfile(particles_file): raise FileNotFoundError(f"{particles_file} doesn't exist, it couldn't be loaded")
        with open(particles_file, 'r') as fil: lines = fil.readlines()
        
        # Extract data
            ## Number of particles
        nparts = int(lines[0][:-1])
            ## Particles positions
        particles = np.array([[float(i) for i in line[:-1].split("\t")] for line in lines[1:]])
        
        return {"nparts": nparts, "particles": particles}
    
    def check_particles_file(self, part_params, nparts, ppos, rm_dir=True):
        """Compare the values written to the particles file with the one ~predicted when calling this function 
        """
        # Create the particles
        particles = ppc.Particles(**part_params)
        particles.write_file()
        
        # Check the attributes of the particles
        self.check_particles_attributes(particles)
        
        # Check if the particles file was created
        self.assertTrue(os.path.isfile(self.sim_dir + "/particles.txt"), "Particles file creation failed")
        
        # Check data inside the particles file
        particles_data = self.load_particles_file(self.sim_dir + "/particles.txt")
            ## Number of particles
        self.assertEqual(particles_data["nparts"], nparts, "Number of particles in particles file wrong ({:d}, expected {:d})".format(particles_data["nparts"], nparts))
        
            ## Particles positions
        parts_equal = (particles_data["particles"]==ppos).all()
        self.assertTrue(parts_equal, "Particles positions in particles file wrong")
        
        # Optionally, remove the simulation directory 
        if rm_dir: shutil.rmtree(self.sim_dir)
        
    def check_particles_attributes(self, particles):
        """Checks that the attributes of the particles object have the right type, and valid value for some 

        Args:
            particles (pycbg.preprocessing.Particles): Particles object whose attributes will be checked
        """
        # Positions
        self.assertIsInstance(particles.positions, np.ndarray, f"`positions` attribute is of type {type(particles.positions)} while it should be of type {np.ndarray}")
        self.assertIsInstance(particles.npart_perdim_percell, int, f"`positions` attribute is of type {type(particles.npart_perdim_percell)} while it should be of type {int}")
        
        # Automatic generation parameter
        self.assertIsInstance(particles.automatic_generation, str, f"`automatic_generation` attribute is of type {type(particles.automatic_generation)} while it should be of type {str}")
        self.assertIn(particles.automatic_generation, self.auto_gener, f"`automatic_generation` is equal to {particles.automatic_generation} while it should be among {self.auto_gener}")
        
        # Mesh
        self.assertIsInstance(particles.mesh, ppc.Mesh, f"`mesh` attribute is of type {type(particles.mesh)} while it should be of type {ppc.Mesh}")
        
        # Simulation parameters
        self.assertIsInstance(particles.directory, str, f"`directory` attribute is of type {type(particles.directory)} while it should be of type {str}")
        self.assertIsInstance(particles.check_duplicates, bool, f"`check_duplicates` attribute is of type {type(particles.check_duplicates)} while it should be of type {bool}")
        self.assertIsInstance(particles.params, dict, f"`params` attribute is of type {type(particles.params)} while it should be of type {dict}")
    
    def setUp(self):
        # Put the simulation in the "tests" directory
            ## The following error should only be raised if there is a big mistake in this script
        if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the src/tests/test_preprocessing.py script")

            ## Extract the directory path from this script path and create the path of the simulation directory 
        self.test_dir = str(pathlib.Path(__file__).resolve()).rsplit("/", 1)[0]
        self.sim_dir = self.test_dir + "/test_particles"
        
        # Create Mesh objects
            ## 2D mesh
        self.mesh_2d = ppc.Mesh([1]*2, [1]*2, cell_type="ED2Q4", directory=self.sim_dir)
        self.larger_mesh_2d = ppc.Mesh([2]*2, [5]*2, cell_type="ED2Q4", directory=self.sim_dir)
        
            ## 3D mesh
        self.mesh_3d = ppc.Mesh([1]*3, [1]*3, directory=self.sim_dir)
        self.larger_mesh_3d = ppc.Mesh([2]*3, [5]*3, directory=self.sim_dir)
        
        # Define default values for particles parameters, "mesh" should always be overwritten
        self.default_params = {"mesh": None, "npart_perdim_percell": 1, "positions": None, "directory": "", "check_duplicates": True, "automatic_generation": "pycbg"}
        
        # Define the possible values for automatic generation parameter
        self.auto_gener = ['pycbg', 'cbgeo']
        
        # Define expected values 
        self.expected_vals = load_json(self.test_dir + "/expected_results/particles.json")
        
    def test_default_particles(self):
        """Check that the default particles parameters work in simple configurations
        """
        # Define expected values for each number of dimensions
        dim_values = {ndim: {nppd: self.expected_vals[f"{ndim}D_{nppd}"] for nppd in range(1, 8)} 
                            for ndim in [2, 3]}
        
        # Test for each number of dimensions
        for ndim, expected_vals_dict in dim_values.items():
            dim_str = f"{ndim}D case" # this string will serve as identifier if a test failure occurs
            for nppd, expected_vals in expected_vals_dict.items():
                nppd_str = f"{nppd} particles per cells per dimension"
                with self.subTest(dim_str=dim_str, nppd_str=nppd_str):
                    particles_params = {"mesh": self.mesh_2d if ndim==2 else self.mesh_3d, "npart_perdim_percell": nppd, "directory": self.sim_dir}
                    self.check_particles_file(particles_params, rm_dir=True, **expected_vals)
        
    def test_larger_nparticles(self):
        """Check that the particles file contains the right data for larger meshes
        """
        
        # Define expected values for each number of dimensions
        dim_values = {ndim: {nppd: self.expected_vals[f"{ndim}D_{nppd}_large"] for nppd in range(1, 5)} 
                            for ndim in [2, 3]}
        
        # Test for each number of dimensions
        for ndim, expected_vals_dict in dim_values.items():
            dim_str = f"{ndim}D case" # this string will serve as identifier if a test failure occurs
            for nppd, expected_vals in expected_vals_dict.items():
                nppd_str = f"{nppd} particles per cells per dimension"
                with self.subTest(dim_str=dim_str, nppd_str=nppd_str):
                    particles_params = {"mesh": self.larger_mesh_2d if ndim==2 else self.larger_mesh_3d, "npart_perdim_percell": nppd, "directory": self.sim_dir}
                    self.check_particles_file(particles_params, rm_dir=True, **expected_vals)
    
    def tearDown(self):
        if os.path.isdir(self.sim_dir): shutil.rmtree(self.sim_dir)

class TestEntitySets(unittest.TestCase):
    def load_es_file(self, entity_sets_file):
        """Loads entity sets file into a dictionary containing relevant values
        """
        # Load entity sets file into a dictionary
        if not os.path.isfile(entity_sets_file): raise FileNotFoundError(f"{entity_sets_file} doesn't exist, it couldn't be loaded")
        with open(entity_sets_file, 'r') as fil: return json.load(fil)
            
    def check_es_file(self, es_params, nodes_fcts, particles_fcts, node_sets, particle_sets, rm_dir=True):
        """Compare the values written to the entity sets file with the one ~predicted when calling this function 
        """
        # Create the entity sets
        es = ppc.EntitySets(**es_params)
        for nf in nodes_fcts: es.create_set(nf, typ="node")
        for pf in particles_fcts: es.create_set(pf, typ="particle")
        es.write_file()
        
        # Check the attributes of the entity sets
        self.check_es_attributes(es)
        
        # Check if the entity sets file was created
        self.assertTrue(os.path.isfile(self.sim_dir + "/entity_sets.json"), "Entity sets file creation failed")
        
        # Check data inside the entity sets file
        es_data = self.load_es_file(self.sim_dir + "/entity_sets.json")
            ## Nodes sets
        self.assertListEqual(es_data["particle_sets"], particle_sets, "Particles sets in entity sets file wrong")
        
            ## Particles sets
        self.assertListEqual(es_data["node_sets"], node_sets, "Nodes sets in entity sets file wrong")
        
        # Optionally, remove the simulation directory 
        if rm_dir: shutil.rmtree(self.sim_dir)
        
    def check_es_attributes(self, es):
        """Checks that the attributes of the entity sets object have the right type, and valid value for some 

        Args:
            es (pycbg.preprocessing.EntitySets): EntitySets object whose attributes will be checked
        """
        # Mesh
        self.assertIsInstance(es.mesh, ppc.Mesh, f"`mesh` attribute is of type {type(es.mesh)} while it should be of type {ppc.Mesh}")
        
        # Particles
        self.assertIsInstance(es.particles, ppc.Particles, f"`particles` attribute is of type {type(es.particles)} while it should be of type {ppc.Particles}")
        
        # Entity sets attributes
            ## Nodes sets
        self.assertIsInstance(es.nsets, list, f"`nsets` attribute is of type {type(es.nsets)} while it should be of type {list}")
        for i_nid, nid in enumerate(es.nsets): 
            self.assertIsInstance(nid, list, f"`nsets[{i_nid}]` attribute is of type {type(nid)} while it should be of type {list}")
            for i_n, n in enumerate(nid):
                self.assertIsInstance(n, int, f"`nsets[{i_nid}][{i_n}]` attribute is of type {type(n)} while it should be of type {int}")
                
            ## Particles sets
        self.assertIsInstance(es.psets, list, f"`psets` attribute is of type {type(es.psets)} while it should be of type {list}")
        for i_nid, nid in enumerate(es.psets): 
            self.assertIsInstance(nid, list, f"`psets[{i_nid}]` attribute is of type {type(nid)} while it should be of type {list}")
            for i_n, n in enumerate(nid):
                self.assertIsInstance(n, int, f"`psets[{i_nid}][{i_n}]` attribute is of type {type(n)} while it should be of type {int}")
        
        # Simulation parameters
        self.assertIsInstance(es.directory, str, f"`directory` attribute is of type {type(es.directory)} while it should be of type {str}")
        self.assertIsInstance(es.params, dict, f"`params` attribute is of type {type(es.params)} while it should be of type {dict}")
    
    def setUp(self):
        # Put the simulation in the "tests" directory
            ## The following error should only be raised if there is a big mistake in this script
        if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the src/tests/test_preprocessing.py script")

            ## Extract the directory path from this script path and create the path of the simulation directory 
        self.test_dir = str(pathlib.Path(__file__).resolve()).rsplit("/", 1)[0]
        self.sim_dir = self.test_dir + "/test_entity_sets"
        
        # Create Mesh and Particles objects
            ## 2D mesh
        self.mesh_2d = ppc.Mesh([2]*2, [5]*2, cell_type="ED2Q4", directory=self.sim_dir)
        self.particles_2d = ppc.Particles(self.mesh_2d, 1, directory=self.sim_dir)
        
            ## 3D mesh
        self.mesh_3d = ppc.Mesh([2]*3, [5]*3, directory=self.sim_dir)
        self.particles_3d = ppc.Particles(self.mesh_3d, 1, directory=self.sim_dir)
        
        # Define entity sets functions
            ## 2D case
        lmaxs_2d = np.array(self.mesh_2d.dimensions)
        self.nodes_fcts_2d = [lambda x,y: x==0, lambda x,y: y==0, lambda x,y: x==lmaxs_2d[0], lambda x,y: y==lmaxs_2d[1]]
        self.particles_fcts_2d = [lambda x,y: x<lmaxs_2d[0]/2, lambda x,y: y<lmaxs_2d[1]/2, lambda x,y: x>lmaxs_2d[0]/2, lambda x,y: y>lmaxs_2d[1]/2]
        
            ## 3D case
        lmaxs_3d = np.array(self.mesh_3d.dimensions)
        self.nodes_fcts_3d = [lambda x,y,z: x==0, lambda x,y,z: y==0, lambda x,y,z: z==0, 
                              lambda x,y,z: x==lmaxs_3d[0], lambda x,y,z: y==lmaxs_3d[1], lambda x,y,z: z==lmaxs_3d[2]]
        self.particles_fcts_3d = [lambda x,y,z: x<lmaxs_3d[0]/2, lambda x,y,z: y<lmaxs_3d[1]/2, lambda x,y,z: z<lmaxs_3d[2]/2, 
                                  lambda x,y,z: x>lmaxs_3d[0]/2, lambda x,y,z: y>lmaxs_3d[1]/2, lambda x,y,z: z>lmaxs_3d[2]/2]
        
        # Define expected values
        self.expected_vals = load_json(self.test_dir + "/expected_results/entity_sets.json")
    
    def test_entity_sets(self):
        """Check that the EntitySets class works
        """
        # Define expected values for each number of dimensions
        dim_values = {ndim: self.expected_vals[f"{ndim}D"] for ndim in [2, 3]}
        
        # Test for each number of dimensions
        for ndim, expected_vals in dim_values.items():
            dim_str = f"{ndim}D" # this string will serve as identifier if a test failure occurs
            if ndim==3: 
                mesh, particles = self.mesh_3d, self.particles_3d
                nodes_fcts, particles_fcts = self.nodes_fcts_3d, self.particles_fcts_3d
            else: 
                mesh, particles = self.mesh_2d, self.particles_2d
                nodes_fcts, particles_fcts = self.nodes_fcts_2d, self.particles_fcts_2d
                
            with self.subTest(dim_str=dim_str):
                es_params = {"mesh": mesh, "particles": particles, "directory": self.sim_dir}
                self.check_es_file(es_params, nodes_fcts, particles_fcts, rm_dir=True, **expected_vals)
    
    def tearDown(self):
        if os.path.isdir(self.sim_dir): shutil.rmtree(self.sim_dir)

class TestMaterials(unittest.TestCase):
    def test_materials_attributes(self):
        """Checks that the attributes of the materials object have the right type, and valid value for some 
        """
        
        # Create materials object
        materials = ppc.Materials()
        
        # Materials list
        self.assertIsInstance(materials.materials, list, f"`materials` attribute is of type {type(materials.materials)} while it should be of type {list}")
        for i_mat, mat in enumerate(materials.materials):
            self.assertIsInstance(mat, dict, f"`materials[{i_mat}]` attribute is of type {type(mat)} while it should be of type {dict}")
        
            ## Particles sets
        self.assertIsInstance(materials.pset_ids, list, f"`psets` attribute is of type {type(materials.pset_ids)} while it should be of type {list}")
        for i_set, set in enumerate(materials.pset_ids):
            if not (isinstance(set, int) or isinstance(set, list)): self.fail(f"`pset_ids` attribute is of type {type(materials.pset_ids)} while it should be of type {int} or {list}")
            elif isinstance(set, list):
                for i_pid, pid in enumerate(set):
                    self.assertIsInstance(set, int, f"`pset_ids[{i_set}][{i_pid}]` attribute is of type {type(pid)} while it should be of type {int}")
        
        # Number of dimensions
        self.assertIsInstance(materials.n_dims, int, f"`n_dims` attribute is of type {type(materials.n_dims)} while it should be of type {int}")
        self.assertIn(materials.n_dims, [2, 3], f"`n_dims` attribute is equal to {materials.n_dims} while it should be among [2, 3]")
        

class TestSimulation(unittest.TestCase):
    def load_input_file(self, input_file):
        """Loads input file into a dictionary containing relevant values
        """
        # Load entity sets file into a dictionary
        if not os.path.isfile(input_file): raise FileNotFoundError(f"{input_file} doesn't exist, it couldn't be loaded")
        with open(input_file, 'r') as fil: return json.load(fil)
    
    def check_sim_files(self, mesh_params, part_params, sim_params, analysis_params, nodes_functions, part_functions, vel_conditions, materials_pes, gravity, input_dict, rm_dir=True, copy_script=False):
        """Check that all files have been created, and check the content of the main input file.

        Args:
            mesh_params (dict): Parameters for the mesh
            part_params (dict): Parameters for the particles
            sim_params (dict): Parameters for the simulation
            analysis_params (dict): Analysis parameters
            nodes_functions (list of functions): List of functions defining nodes sets
            part_functions (list of functions): List of functions defining particles sets
            vel_conditions (list of triplets (int, float, int)): List of triplets corresponding to velocity conditions, each contains (node_set_id, imposed_value, axis)
            materials_pes (list of triplets (int, str, dict)): List of triplets corresponding to materials each contains (particles_set_id, material_str_identifier, material_params)
            gravity (list of floats): Gravity to use for during the simulation
            input_dict (dict): Reference input file values to check for errors
            rm_dir (bool, optional): Remove the simulation directory once testing is done. Defaults to True.
        """
        # Create the Simulation object, its mesh, and its particles
        sim = ppc.Simulation(**sim_params)
        sim.create_mesh(**mesh_params)
        sim.create_particles(**part_params)
        
        # Create the entity sets
        sim.init_entity_sets()
            ## Nodes sets
        nodes_sets = [sim.entity_sets.create_set(fct, typ="node") for fct in nodes_functions]
            ## Particles sets
        particles_sets = [sim.entity_sets.create_set(fct, typ="particle") for fct in part_functions]
        
        # Add nodal velocity conditions
        for nes, val, dir in vel_conditions: sim.add_velocity_condition(dir, val, nes)
        
        # Create the materials
        for pes, mat_str, mat_params in materials_pes:
            create_mat = getattr(sim.materials, f"create_{mat_str}")
            create_mat(pset_id=pes, **mat_params)
            
        # Add gravity
        sim.set_gravity(gravity)
        
        # Set the analysis parameters
        sim.set_analysis_parameters(**analysis_params)
        
        # Write input file (and entity sets file, and pickle simulation object)
        sim.write_input_file()
        
        # Check the attributes of the Simulation object
        self.check_sim_attributes(sim)
        
        # Check that all files were created
        self.check_sim_files_exist(sim)
        
        # Check the content of the input file
        sim_data = self.load_input_file(f"{self.sim_dir}/{sim.input_filename}")
        self.check_input_file(sim_data, input_dict)
                
        # Optionally, remove the simulation directory 
        if rm_dir: shutil.rmtree(self.sim_dir)
    
    def check_sim_files_exist(self, sim):
        """Check if the simulation files were indeed created

        Args:
            sim (pycbg.preprocessing.Simulation): Simulation object to be checked
        """
        # Mesh file
        self.assertTrue(os.path.isfile(self.sim_dir + "/mesh.txt"), "Mesh file missing")
        
        # Particles file
        self.assertTrue(os.path.isfile(self.sim_dir + "/particles.txt"), "Particles file missing")
        
        # Entity sets file
        self.assertTrue(os.path.isfile(self.sim_dir + "/entity_sets.json"), "Entity sets file missing")
        
        # Input file
        self.assertTrue(os.path.isfile(self.sim_dir + f"/{sim.input_filename}"), "Input file missing")
        
        # Simulation pickle file
        self.assertTrue(os.path.isfile(self.sim_dir + f"/{sim.title}.Simulation"), "Pickled simulation file missing")
    
    def check_input_file(self, sim_data, input_dict): 
        """Checks if the input file is correct. If sim_data is not exactly input_dict, subsets of sim_data are checked, in the case of new parameters.

        Args:
            sim_data (_type_): _description_
            input_dict (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Convert both nested dictionaries of list and dict mixture into nested dictionary of only dict
        sim_data, input_dict = self.convert2dict(sim_data), self.convert2dict(input_dict)
        
        # Make sure paths are relative to PyCBG's root directory
        sim_data = self.turn_path_rel(sim_data, "pycbg/src/")
        input_dict = self.turn_path_rel(input_dict, "pycbg/src/")
        
        if sim_data==input_dict: return # tested passed
        
        # Extract from sim_data the subset containing only the keys present in input_dict (recursively)
        subset_data = self.subset_nested_dict(sim_data, input_dict)
        
        # Check if the reference dict is a subset of the tested dict (should occur when new parameters are added) 
        if subset_data==input_dict: 
            self.warn_new_params = True
            self.new_params = self.diff_keys(sim_data, subset_data)
            return # tested passed
        
        # Fail the test and display the difference between the expected and actual dictionaries    
        self.assertDictEqual(sim_data, input_dict, "Input file content is not what was expected") 
            
    def convert2dict(self, nested_list_dict):
        """Converts a dictionary nested with a mixture of lists and dictionaries (very much like CB-Geo MPM's input file) into a purely nested dictionary.

        Args:
            nested_list_dict (dict nested with dicts and/or lists): Bastardly nested dictionary to convert

        Returns:
            nested dict: Converted nested dictionary
        """
        if isinstance(nested_list_dict, list): 
            return self.convert2dict({i: val for i, val in enumerate(nested_list_dict)})
        elif isinstance(nested_list_dict, dict):
            return {key: self.convert2dict(val) for key, val in nested_list_dict.items()}
        else: return nested_list_dict
        
    def subset_nested_dict(self, nested_dict, nested_dict_ref):
        """Extract from nested_dict the subset that contains only the field from nested_dict_ref. Useful to detect if there are new parameters in the input file.

        Args:
            nested_dict (nested dict): Nested dictionary containing the input file data, may contain more parameters than the reference input file 
            nested_dict_ref (nested dict): Nested dictionary containing the reference input file data.

        Returns:
            nested dict: Subset of nested_dict containing only the keys present in nested_dict_ref
        """
        if not isinstance(nested_dict, dict): return nested_dict
        subdict = {}
        for key, val in nested_dict.items():
            # if not key in nested_dict_ref: continue
            if isinstance(val, dict):
                subdict[key] = {key2: self.subset_nested_dict(val2, nested_dict_ref[key][key2]) for key2, val2 in val.items() if key2 in nested_dict_ref[key]}
            else: 
                if key in nested_dict_ref: subdict[key] = val
        return subdict
    
    def diff_keys(self, dnew, dold):
        """Return a list of all the keys in dnew that are not in dold (recursively)

        Args:
            dnew (nested dict): Dictionary containing new keys
            dold (nested dict): Dictionary which is only a subset of dnew

        Returns:
            list: list containing all keys that dnew has and dold doesn't have. Note that keys from different nesting level are all in the same level in the returned list.
        """
        if not isinstance(dnew, dict): return []
        new_keys = list(set(dnew)^set(dold))
        for key in dnew:
            if key not in dold: continue
            new_keys += self.diff_keys(dnew[key], dold[key])
        return new_keys
    
    def turn_path_rel(self, path_dict, base_dir):
        if not isinstance(path_dict, dict): 
            if isinstance(path_dict, str) and base_dir in path_dict: # This field is a path
                path_dict = base_dir + path_dict.split(base_dir, 1)[1]
            return path_dict
        return {key: self.turn_path_rel(val, base_dir) for key, val in path_dict.items()}
        
    def check_sim_attributes(self, sim):
        """Checks that the attributes of the mesh have the right type, and valid value for some 

        Args:
            mesh (pycbg.preprocessing.Mesh): Mesh object whose attributes will be checked
        """
        # Mesh
        self.assertIsInstance(sim.mesh, ppc.Mesh, f"`mesh` attribute is of type {type(sim.mesh)} while it should be of type {ppc.Mesh}")
        
        # Particles
        self.assertIsInstance(sim.particles, ppc.Particles, f"`particles` attribute is of type {type(sim.particles)} while it should be of type {ppc.Particles}")
        
        # Entity sets
        self.assertIsInstance(sim.entity_sets, ppc.EntitySets, f"`entity_sets` attribute is of type {type(sim.entity_sets)} while it should be of type {ppc.EntitySets}")
        
        # Materials
        self.assertIsInstance(sim.materials, ppc.Materials, f"`materials` attribute is of type {type(sim.materials)} while it should be of type {ppc.Materials}")
        
        # Initial stresses
        if sim.init_stresses is not None:
            self.assertIsInstance(sim.init_stresses, np.ndarray, f"`init_stresses` attribute is of type {type(sim.init_stresses)} while it should be of type {np.ndarray}")

        # Initial velocity
        if sim.init_velocities is not None:
            self.assertIsInstance(sim.init_velocities, np.ndarray, f"`init_velocities` attribute is of type {type(sim.init_velocities)} while it should be of type {np.ndarray}")
        
        # Initial volume
        if sim.init_volumes is not None:
            self.assertIsInstance(sim.init_volumes, np.ndarray, f"`init_volumes` attribute is of type {type(sim.init_volumes)} while it should be of type {np.ndarray}")

        # Gravity
        self.assertIsInstance(sim.gravity, list, f"`gravity` attribute is of type {type(sim.gravity)} while it should be of type {np.ndarray}")
        for i_g, g in enumerate(sim.gravity):
            self.assertIsInstance(g, float, f"`gravity[{i_g}]` is of type {type(g)} while it should be of type {float}")
        
        # Analysis parameters
        self.assertIsInstance(sim.analysis_params, dict, f"`analysis_params` attribute is of type {type(sim.analysis_params)} while it should be of type {dict}")
        
        # Simulation parameters
        self.assertIsInstance(sim.custom_params, dict, f"`custom_params` attribute is of type {type(sim.custom_params)} while it should be of type {dict}")
        self.assertIsInstance(sim.directory, str, f"`directory` attribute is of type {type(sim.directory)} while it should be of type {str}")
        self.assertIsInstance(sim.title, str, f"`title` attribute is of type {type(sim.title)} while it should be of type {str}")
        self.assertIsInstance(sim.input_filename, str, f"`input_filename` attribute is of type {type(sim.input_filename)} while it should be of type {str}")
    
    
    def setUp(self):
        # Put the simulation in the "tests" directory
            ## The following error should only be raised if there is a big mistake in this script
        if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the src/tests/test_preprocessing.py script")

            ## Extract the directory path from this script path and create the path of the simulation directory 
        self.test_dir = str(pathlib.Path(__file__).resolve()).rsplit("/", 1)[0]
        self.sim_dir = self.test_dir + "/test_sim"
        
        # Define default values for simulation parameters
        self.default_params = {"title": 'Sim_title', "input_filename": 'input_file', "directory": ""}
        
        # Define expected values 
        self.expected_vals = load_json(self.test_dir + "/expected_results/simulation.json")
        
        # Define combinations of `dimensions`, `ncells`, `npart_perdim_percell` for tests with various sizes
        nppc_vals = list(range(1, 4))
        
            ## 2D cases
        dim_vals_2d = [[1e-3]*2, [1/7]*2, [5692.6, 5.8e8]]
        ncells_vals_2d = [[2]*2, [7, 2], [5, 3], [1, 5]]
        self.mesh_part_comb_2d = list(it.product(dim_vals_2d, ncells_vals_2d, nppc_vals))
        
            ## 3D cases
        dim_vals_3d = [[1e-7]*3, [1/3]*3, [10000, 1e8, .5]]
        ncells_vals_3d = [[2]*3, [10, 3, 1], [4, 3, 2]]
        self.mesh_part_comb_3d = list(it.product(dim_vals_3d, ncells_vals_3d, nppc_vals))
        
        # Define combinations of `material_type`, `damping`, `dt`, `velocity_update` for testing in various conditions
        mat_strs = ["LinearElastic", "MohrCoulomb", "Newtonian", "NorSand"]
        damping_vals = [.01, .2, .7]
        dts = [1e-6, 1e-5, 1e-4]
        vu_vals = ["flip", "flip0.9", "pic", "apic"]
        self.various_comb = list(it.product(mat_strs, damping_vals, dts, vu_vals))
        
        # Initialize the new_params variables
        self.warn_new_params = False
        self.new_params = []
        
    def test_sim_name(self):
        """Check if the simulation name feature works
        """
        sim_check_params = {"mesh_params": {"dimensions": [10]*3, "ncells": [5]*3},
                            "part_params": {"npart_perdim_percell": 1},
                            "sim_params": {"title": "My_sim_name1_", "directory": self.sim_dir, "copy_script": False},
                            "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                            "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10],
                            "input_dict": self.expected_vals["sim_name"]}
        with self.subTest(sim_check_params=sim_check_params): self.check_sim_files(**sim_check_params)
    
    def test_various_dims(self):
        """Check if the input file is correct for various simulation sizes
        """
        # 2D case
        for dim, ncells, nppc in self.mesh_part_comb_2d:
            expected_vals_key = "2D_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells)
            sim_check_params = {"mesh_params": {"dimensions": dim, "ncells": ncells, "cell_type": "ED2Q4"},
                                "part_params": {"npart_perdim_percell": nppc},
                                "sim_params": {"title": "My_sim_name1_", "directory": self.sim_dir, "copy_script": False},
                                "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                                "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10],
                                "input_dict": self.expected_vals[expected_vals_key]}
            with self.subTest(sim_check_params=sim_check_params): self.check_sim_files(**sim_check_params)
        # 3D case
        for dim, ncells, nppc in self.mesh_part_comb_3d:
            expected_vals_key = "3D_{:g}_{:g}_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells)
            sim_check_params = {"mesh_params": {"dimensions": dim, "ncells": ncells},
                                "part_params": {"npart_perdim_percell": nppc},
                                "sim_params": {"title": "My_sim_name1_", "directory": self.sim_dir, "copy_script": False},
                                "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                                "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10],
                                "input_dict": self.expected_vals[expected_vals_key]}
            with self.subTest(sim_check_params=sim_check_params): self.check_sim_files(**sim_check_params)
            
    def test_various_confs(self):
        """Check if the input file is correct for various configurations
        """
        # 2D case
        for mat_str, damp, dt, vu in self.various_comb:
            expected_vals_key = "2D_{:}_{:g}_{:g}_{:}".format(mat_str, damp, dt, vu)
            sim_check_params = {"mesh_params": {"dimensions": [10]*2, "ncells": [5]*2, "cell_type": "ED2Q4"},
                                "part_params": {"npart_perdim_percell": 1},
                                "sim_params": {"title": "My_sim_name1_", "directory": self.sim_dir, "copy_script": False},
                                "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                                "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10],
                                "input_dict": self.expected_vals[expected_vals_key]}
            with self.subTest(sim_check_params=sim_check_params): self.check_sim_files(**sim_check_params)
        # 3D case
        for mat_str, damp, dt, vu in self.various_comb:
            expected_vals_key = "3D_{:}_{:g}_{:g}_{:}".format(mat_str, damp, dt, vu)
            sim_check_params = {"mesh_params": {"dimensions": [10]*3, "ncells": [5]*3},
                                "part_params": {"npart_perdim_percell": 1},
                                "sim_params": {"title": "My_sim_name1_", "directory": self.sim_dir, "copy_script": False},
                                "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                                "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10],
                                "input_dict": self.expected_vals[expected_vals_key]}
            with self.subTest(sim_check_params=sim_check_params): self.check_sim_files(**sim_check_params)
    
    def tearDown(self):
        if self.warn_new_params: warnings.warn(f"The following new parameters are not yet included in the reference unit tests: {self.new_params}. Please consider updating `src/tests/test_preprocessing.py`", DeprecationWarning)
        if os.path.isdir(self.sim_dir): shutil.rmtree(self.sim_dir)