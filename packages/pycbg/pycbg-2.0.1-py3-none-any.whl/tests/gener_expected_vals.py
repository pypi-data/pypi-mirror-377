"""This script can be used to generate expected results in various cases, in order to serve as reference for unit tests. Before integrating the results of this script in the test scripts, the former should be carefully reviewed so no error slips into the testing. 
"""

import os, shutil, pathlib, json
import itertools as it
from pycbg import preprocessing as ppc

import numpy as np

# This class is used to make possible writing a np.ndarray into a JSON file 
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    
def dump_json(parameters_sets_keys, expected_vals, filename="expected_vals.json"):
    """Dump the expected values obtained with several parameters_sets into a JSON file, for easy import.

    Args:
        parameters_sets_keys (list of strings): String identifying each parameters set, it will be used as keys for the dictionary written to the JSON file.
        expected_vals (list of dict): Expected values obtained with the corresponding parameters set in the parameters_sets_keys list.
        filename (str, optional): Name of the JSON file to be created. Defaults to "expected_vals.json".
    """
    main_dic = {psk: ev for psk, ev in zip(parameters_sets_keys, expected_vals)}
    with open(filename, 'w') as fil: json.dump(main_dic, fil, sort_keys=False, indent=4, cls=NumpyEncoder)

# Create results directory if non existant
    ## Get tests directory's path
if not "__file__" in globals().keys(): raise RuntimeError("`__file__` variable not found, there must be a bug in the tests/gener_expected_vals.py script")
tests_dir = str(pathlib.Path(__file__).resolve()).rsplit("/", 1)[0]

    ## Check and create expected results directory
res_dir = tests_dir + "/expected_results/"
os.makedirs(res_dir, exist_ok=True)


####################################################################################################
####### MESH ############## MESH ############## MESH ############## MESH ############## MESH #######
####################################################################################################

default_mesh_params = {"dimensions": None, "ncells": None, "origin": (0.,0.,0.), "directory": "", "check_duplicates": True, "cell_type": "ED3H8", "round_decimal": None, "no_output": True, "save_shapefn": [], "shapefn_resolution": 25, "save_shapefn_grad": False}
mesh_dir = tests_dir + "/test_mesh"

def gener_mesh_expected(mesh_params):
    """Returns expected mesh file values for a given set of mesh parameters. Should be used only with a working version of PyCBG.

    Args:
        mesh_params (dict): Parameters of the mesh from which to extract the data

    Raises:
        FileNotFoundError: if the mesh file creation failed
        
    Returns:
        dict: dictionary containing expected values ("nnodes", "ncells", "npos", "cells")
    """
    if mesh_params["directory"] == "":
        init_dir, sim_dir = os.getcwd(), mesh_dir
        os.makedirs(sim_dir, exist_ok=True)
        os.chdir(sim_dir)
        mesh_file = sim_dir + "/mesh.txt"
    else: 
        sim_dir = mesh_params["directory"]
        mesh_file = sim_dir + "/mesh.txt"
        
    mesh = ppc.Mesh(**mesh_params)
    
    if not os.path.isfile(mesh_file): raise FileNotFoundError(f"{mesh_file} doesn't exist, it couldn't be loaded")
    with open(mesh_file, 'r') as fil: lines = fil.readlines()
    
    # Extract data
            ## Number of nodes and cells
    nnodes, ncells = [int(i) for i in lines[0][:-1].split("\t")]
        ## Nodes positions
    nodes = np.array([[float(i) for i in line[:-2].split(" ")] for line in lines[1:nnodes+1]])
        ## Cells, as list of node IDs
    cells = np.array([[int(i) for i in line[:-1].split(" ")] for line in lines[nnodes+1:]])
    
    if mesh_params["directory"] == "": os.chdir(init_dir)
    shutil.rmtree(sim_dir)
    
    return {"nnodes": nnodes, "ncells": ncells, "npos": nodes, "cells": cells}


mesh_param_sets, mesh_keys = [], []

# Parameters sets for the default parameters tests
mesh_param_sets.append({**default_mesh_params, "dimensions": [1]*2, "ncells": [1]*2, "cell_type": "ED2Q4"}) # 2D
mesh_param_sets.append({**default_mesh_params, "dimensions": [1]*3, "ncells": [1]*3}) # 3D
mesh_keys += ["default_2d", "default_3d"]

# Parameters set for the specified directory test
mesh_param_sets.append({**default_mesh_params, "dimensions": [1]*3, "ncells": [1]*3, "directory": mesh_dir})
mesh_keys.append("specified_dir")

# Parameters sets for the shifted origin tests
o_shifts = [[1, 1, 1], [-1, -1, -1], [1000, 0, 0], [0, 1e-10, 0], [0, 0, 1/2]]
for o_shift in o_shifts:
    mesh_param_sets.append({**default_mesh_params, "dimensions": [1]*3, "ncells": [1]*3, "directory": mesh_dir, "origin": o_shift})
    mesh_keys.append("origin_shift_{:g}_{:g}_{:g}".format(*o_shift))

# Parameters sets for larger tests
    ## 2D various cases
dim_vals_2d = [[1e-7]*2, [1/6]*2, [10000, 1e8]]
ncells_vals_2d = [[2]*2, [10, 3], [4, 3], [1, 5]]
for dim, ncells in it.product(dim_vals_2d, ncells_vals_2d):
    mesh_param_sets.append({**default_mesh_params, "dimensions": dim, "ncells": ncells, "cell_type": "ED2Q4"})
    mesh_keys.append("large_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells))

    ## 3D various cases
dim_vals_3d = [[1e-7]*3, [1/3]*3, [10000, 1e8, .5]]
ncells_vals_3d = [[2]*3, [10, 3, 1], [4, 3, 2]]
for dim, ncells in it.product(dim_vals_3d, ncells_vals_3d):
    mesh_param_sets.append({**default_mesh_params, "dimensions": dim, "ncells": ncells})
    mesh_keys.append("large_{:g}_{:g}_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells))

# Write the JSON file
expected_mesh_vals = [gener_mesh_expected(ps) for ps in mesh_param_sets]
dump_json(mesh_keys, expected_mesh_vals, res_dir+"mesh.json")


####################################################################################################
####### PARTICLES ############## PARTICLES ############## PARTICLES ############## PARTICLES #######
####################################################################################################

default_part_params = {"mesh": None, "npart_perdim_percell": 1, "positions": None, "directory": "", "check_duplicates": True, "automatic_generation": "pycbg"}
part_dir = tests_dir + "/test_particles"

def gener_part_expected(part_params):
    """Returns expected particles file values for a given set of particles parameters. Should be used only with a working version of PyCBG.

    Args:
        part_params (dict): Parameters of the particles from which to extract the data

    Raises:
        FileNotFoundError: if the particles file creation failed
        
    Returns:
        dict: dictionary containing expected values ("nparts", "ppos")
    """
    if part_params["directory"] == "":
        init_dir, sim_dir = os.getcwd(), mesh_dir
        os.makedirs(sim_dir, exist_ok=True)
        os.chdir(sim_dir)
        part_file = sim_dir + "/particles.txt"
    else: 
        sim_dir = part_params["directory"]
        part_file = sim_dir + "/particles.txt"
        
    particles = ppc.Particles(**part_params)
    particles.write_file()
    
    if not os.path.isfile(part_file): raise FileNotFoundError(f"{part_file} doesn't exist, it couldn't be loaded")
    with open(part_file, 'r') as fil: lines = fil.readlines()
    
    # Extract data
        ## Number of particles
    nparts = int(lines[0][:-1])
        ## Particles positions
    ppos = np.array([[float(i) for i in line[:-1].split("\t")] for line in lines[1:]])
    
    if part_params["directory"] == "": os.chdir(init_dir)
    shutil.rmtree(sim_dir)
    
    return {"nparts": nparts, "ppos": ppos}


part_param_sets, part_keys = [], []

# Parameters sets for the default parameters tests
nppd_s = list(range(1, 8)) # numbers of particles per cell per dimensions to be tested
    ## 2D cases
mesh_2d = ppc.Mesh([1]*2, [1]*2, cell_type="ED2Q4", directory=part_dir)
for nppd in nppd_s:
    part_param_sets.append({**default_part_params, "mesh": mesh_2d, "npart_perdim_percell": nppd, "directory": part_dir})
    part_keys.append(f"2D_{nppd}")

    ## 3D cases
mesh_3d = ppc.Mesh([1]*3, [1]*3, directory=part_dir)
for nppd in nppd_s:
    part_param_sets.append({**default_part_params, "mesh": mesh_3d, "npart_perdim_percell": nppd, "directory": part_dir})
    part_keys.append(f"3D_{nppd}")

# Parameters sets for larger tests
    ## 2D cases
larger_mesh_2d = ppc.Mesh([2]*2, [5]*2, cell_type="ED2Q4", directory=part_dir)
for nppd in nppd_s:
    part_param_sets.append({**default_part_params, "mesh": larger_mesh_2d, "npart_perdim_percell": nppd, "directory": part_dir})
    part_keys.append(f"2D_{nppd}_large")
    
    ## 3D cases
larger_mesh_3d = ppc.Mesh([2]*3, [5]*3, directory=part_dir)
for nppd in nppd_s:
    part_param_sets.append({**default_part_params, "mesh": larger_mesh_3d, "npart_perdim_percell": nppd, "directory": part_dir})
    part_keys.append(f"3D_{nppd}_large")

# Write the JSON file
expected_part_vals = [gener_part_expected(ps) for ps in part_param_sets]
dump_json(part_keys, expected_part_vals, res_dir+"particles.json")


############################################################################################################
####### ENTITY SETS ############## ENTITY SETS ############## ENTITY SETS ############## ENTITY SETS #######
############################################################################################################

default_es_params = {"mesh": None, "particles": None, "directory": ""}
es_dir = tests_dir + "/test_entity_sets"

def gener_es_expected(es_params, nodes_fcts=[], particles_fcts=[]):
    """Returns expected entity sets file values for a given set of entity sets parameters. Should be used only with a working version of PyCBG.

    Args:
        es_params (dict): Parameters of the entity sets from which to extract the data
        nodes_fcts (list, optional): List of functions that will define the nodes sets. Defaults to [].
        particles_fcts (list, optional): List of functions that will define the particles sets. Defaults to [].

    Raises:
        FileNotFoundError: if the entity sets file creation failed

    Returns:
        dict: dictionary containing expected values ("particle_sets", "node_sets")
    """
    if es_params["directory"] == "":
        init_dir, sim_dir = os.getcwd(), mesh_dir
        os.makedirs(sim_dir, exist_ok=True)
        os.chdir(sim_dir)
        es_file = sim_dir + "/entity_sets.json"
    else: 
        sim_dir = es_params["directory"]
        es_file = sim_dir + "/entity_sets.json"
        
    es = ppc.EntitySets(**es_params)
    for nf in nodes_fcts: es.create_set(nf, typ="node")
    for pf in particles_fcts: es.create_set(pf, typ="particle")
    es.write_file()
    
    if not os.path.isfile(es_file): raise FileNotFoundError(f"{es_file} doesn't exist, it couldn't be loaded")
    with open(es_file, 'r') as fil: es_dict = json.load(fil)
    
    if es_params["directory"] == "": os.chdir(init_dir)
    shutil.rmtree(sim_dir)
    
    return es_dict


es_param_sets, es_keys = [], []
node_functions, particles_functions = [], []

# Parameters sets for various entity sets tests
    ## 2D case
particles_2d = ppc.Particles(larger_mesh_2d, 1)
lmaxs_2d = np.array(larger_mesh_2d.dimensions)
es_param_sets.append({"mesh": larger_mesh_2d, "particles": particles_2d, "directory": es_dir})
node_functions.append([lambda x,y: x==0, lambda x,y: y==0, lambda x,y: x==lmaxs_2d[0], lambda x,y: y==lmaxs_2d[1]])
particles_functions.append([lambda x,y: x<lmaxs_2d[0]/2, lambda x,y: y<lmaxs_2d[1]/2, lambda x,y: x>lmaxs_2d[0]/2, lambda x,y: y>lmaxs_2d[1]/2])
es_keys.append("2D")

    ## 3D case
particles_3d = ppc.Particles(larger_mesh_3d, 1)
lmaxs_3d = np.array(larger_mesh_3d.dimensions)
es_param_sets.append({"mesh": larger_mesh_3d, "particles": particles_3d, "directory": es_dir})
node_functions.append([lambda x,y,z: x==0, lambda x,y,z: y==0, lambda x,y,z: z==0, 
                       lambda x,y,z: x==lmaxs_3d[0], lambda x,y,z: y==lmaxs_3d[1], lambda x,y,z: z==lmaxs_3d[2]])
particles_functions.append([lambda x,y,z: x<lmaxs_3d[0]/2, lambda x,y,z: y<lmaxs_3d[1]/2, lambda x,y,z: z<lmaxs_3d[2]/2, 
                            lambda x,y,z: x>lmaxs_3d[0]/2, lambda x,y,z: y>lmaxs_3d[1]/2, lambda x,y,z: z>lmaxs_3d[2]/2])
es_keys.append("3D")

# Write the JSON file
expected_es_vals = [gener_es_expected(ps, nfs, pfs) for ps, nfs, pfs in zip(es_param_sets, node_functions, particles_functions)]
dump_json(es_keys, expected_es_vals, res_dir+"entity_sets.json")


####################################################################################################
####### SIMULATION ############# SIMULATION ############# SIMULATION ############# SIMULATION ######
####################################################################################################

sim_dir = tests_dir + "/test_sim"

def turn_path_rel(path_dict, base_dir):
    if not isinstance(path_dict, dict): 
        if isinstance(path_dict, str) and base_dir in path_dict: # This field is a path
            path_dict = base_dir + path_dict.split(base_dir, 1)[1]
        return path_dict
    return {key: turn_path_rel(val, base_dir) for key, val in path_dict.items()}

def gener_sim_expected(mesh_params, part_params, sim_params, analysis_params, nodes_functions, part_functions, vel_conditions, materials_pes, gravity):
    """Returns expected input file values for a given set of simulation (mesh, particles, ...) parameters. Should be used only with a working version of PyCBG.

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

    Raises:
        FileNotFoundError: if the input file creation failed

    Returns:
        dict: dictionary containing expected input file values (imported JSON file)
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
    
    input_file = sim.directory + sim.input_filename
    
    if not os.path.isfile(input_file): raise FileNotFoundError(f"{input_file} doesn't exist, it couldn't be loaded")
    with open(input_file, 'r') as fil: input_dict = json.load(fil)
    
    shutil.rmtree(sim_dir)
    
    return turn_path_rel(input_dict, "pycbg/src/")


sim_param_sets, sim_keys = [], []

# Parameters sets for simple test on sim name
sim_param_sets.append({"mesh_params": {"dimensions": [10]*3, "ncells": [5]*3}, 
                      "part_params": {"npart_perdim_percell": 1}, 
                      "sim_params": {"title": "My_sim_name1_", "directory": sim_dir}, 
                      "analysis_params": {}, "nodes_functions": [], "part_functions": [], "vel_conditions": [],
                      "materials_pes": [], "gravity": [0,0,-10]})
sim_keys.append("sim_name")

# Test with various simulation sizes
nppc_vals = list(range(1, 4))

    ## 2D case
dim_vals_2d = [[1e-3]*2, [1/7]*2, [5692.6, 5.8e8]]
ncells_vals_2d = [[2]*2, [7, 2], [5, 3], [1, 5]]
mesh_part_comb_2d = list(it.product(dim_vals_2d, ncells_vals_2d, nppc_vals))
for dim, ncells, nppc in mesh_part_comb_2d:
    sim_param_sets.append({"mesh_params": {"dimensions": dim, "ncells": ncells, "cell_type": "ED2Q4"},
                           "part_params": {"npart_perdim_percell": nppc},
                           "sim_params": {"title": "My_sim_name1_", "directory": sim_dir},
                           "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                           "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10]})
    sim_keys.append("2D_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells))
    
    ## 3D case
dim_vals_3d = [[1e-7]*3, [1/3]*3, [10000, 1e8, .5]]
ncells_vals_3d = [[2]*3, [10, 3, 1], [4, 3, 2]]
mesh_part_comb_3d = list(it.product(dim_vals_3d, ncells_vals_3d, nppc_vals))
for dim, ncells, nppc in mesh_part_comb_3d:
    sim_param_sets.append({"mesh_params": {"dimensions": dim, "ncells": ncells},
                           "part_params": {"npart_perdim_percell": nppc},
                           "sim_params": {"title": "My_sim_name1_", "directory": sim_dir},
                           "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                           "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10]})
    sim_keys.append("3D_{:g}_{:g}_{:g}_{:g}_{:g}_{:g}".format(*dim, *ncells))

# Test with various configurations
mat_strs = ["LinearElastic", "MohrCoulomb", "Newtonian", "NorSand"]
damping_vals = [.01, .2, .7]
dts = [1e-6, 1e-5, 1e-4]
vu_vals = ["flip", "flip0.9", "pic", "apic"]
various_comb = list(it.product(mat_strs, damping_vals, dts, vu_vals))

    ## 2D case
for mat_str, damp, dt, vu in various_comb:
    sim_param_sets.append({"mesh_params": {"dimensions": [10]*2, "ncells": [5]*2, "cell_type": "ED2Q4"},
                           "part_params": {"npart_perdim_percell": nppc},
                           "sim_params": {"title": "My_sim_name1_", "directory": sim_dir},
                           "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                           "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10]})
    sim_keys.append("2D_{:}_{:g}_{:g}_{:}".format(mat_str, damp, dt, vu))
    
    ## 3D case
dim_vals_3d = [[1e-7]*3, [1/3]*3, [10000, 1e8, .5]]
ncells_vals_3d = [[2]*3, [10, 3, 1], [4, 3, 2]]
mesh_part_comb_3d = list(it.product(dim_vals_3d, ncells_vals_3d, nppc_vals))
for mat_str, damp, dt, vu in various_comb:
    sim_param_sets.append({"mesh_params": {"dimensions": [10]*3, "ncells": [5]*3},
                           "part_params": {"npart_perdim_percell": nppc},
                           "sim_params": {"title": "My_sim_name1_", "directory": sim_dir},
                           "analysis_params": {}, "nodes_functions": [], "part_functions": [],
                           "vel_conditions": [], "materials_pes": [], "gravity": [0,0,-10]})
    sim_keys.append("3D_{:}_{:g}_{:g}_{:}".format(mat_str, damp, dt, vu))

# Write the JSON file
expected_sim_vals = [gener_sim_expected(**sim_params) for sim_params in sim_param_sets]
dump_json(sim_keys, expected_sim_vals, f"{res_dir}simulation.json")