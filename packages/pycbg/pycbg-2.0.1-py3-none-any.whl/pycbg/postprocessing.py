import os, pickle, warnings, re, glob, json
import numpy as np
import pandas as pd

import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from functools import partial

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from pycbg import NewFeatureWarning

class ResultsReader():
    """Load the result of a simulation. Can also load the :func:`~pycbg.preprocessing.Simulation` object used during preprocessing.

    Parameters
    ----------
    directory : str
        Directory in which the input file of the simulation was saved.
    load_step : int or str among {'first', 'last'}, optional
        Can be used to skip some `particles*.csv` files when loading data, in the case of heavy simulations. If set to an integer, 1 every `load_step` file will be loaded, starting from the first one. If set to a string, it should be either 'first' or 'last' to load only the first or last file respectively. By default all files are loaded (`load_step=1`).
    load_nodes_data : bool
        Whether to load nodes CSV files, if present. Default to `False`.
    fill_nan : int, optional
        number of `numpy.nan` to add at the end of the results, simulating additional CSV files that might be missing (useful for uncompleted batch simulations)

    Attributes
    ----------
    ppositions : list of numpy arrays
        Particles' positions for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``ppositions[i]`` is ``(npart,3)``.
    pvelocities : list of numpy arrays
        Particles' velocities for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pvelocities[i]`` is ``(npart,3)``.
    pstresses : list of numpy arrays
        Particles' stresses for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pstresses[i]`` is ``(npart,6)``. The columns respectively correspond to `xx`, `yy`, `zz`, `xy`, `yz` and `xz` components.
    pstrains : list of numpy arrays
        Particles' strains for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pstrains[i]`` is ``(npart,6)``. The columns respectively correspond to eps`xx`, eps`yy`, eps`zz`, gamma`xy`, gamma`yz` and gamma`xz` components, following the CB-Geo MPM convention to handle the engineering strain for out-of-diagonal terms.
    ppressures : list of numpy arrays
        Particles' pressures for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``ppressures[i]`` is ``(npart,)``.
    pmasses : list of numpy arrays
        Particles' masses for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pmasses[i]`` is ``(npart,)``.
    pvolumes : list of numpy arrays
        Particles' volumes for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pvolumes[i]`` is ``(npart,)``.
    pcell_ids: list of numpy arrays
        Ids of mesh cells hosting the particles for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pcell_ids[i]`` is ``(npart,)``.
    pmaterials : list of numpy arrays
        Particles' material's id for every saved steps. Noting npart the number of particles in the simulations at the ith step, the shape of ``pmaterials[i]`` is ``(npart,)``.
    Bs : list of numpy arrays if present
        If this simulation uses an affine augmented motion integration strategy, this attribute is set to a list of the values computed for the B matrix at each saved iteration. Each element is a numpy array of shape ``(npart, ndim, ndim)``.
    Ds : list of numpy arrays if present
        If this simulation uses an affine augmented motion integration strategy, this attribute is set to a list of the values computed for the D matrix at each saved iteration. Each element is a numpy array of shape ``(npart, ndim, ndim)``.
    Cs : list of numpy arrays if present
        If this simulation uses an affine augmented motion integration strategy, this attribute is set to a list of the values computed for the C matrix at each saved iteration (computed from B and D when loading the results). Each element is a numpy array of shape ``(npart, ndim, ndim)``.
    gVs : list of numpy arrays if present
        If this simulation uses a Taylor motion integration strategy, this attribute is set to a list of the values computed for the velocity gradient at each saved iteration. Each element is a numpy array of shape ``(npart, ndim, ndim)``, with ``ndim`` the number of dimensions.
    raw_data : list of pandas dataframes
        All data saved in the particles CSV files. The data is stored for each time step as a dataframe.
    npositions : numpy array
        Nodes' positions, constant during the whole simulation. Noting nnodes the number of nodes in the simulations, the shape of ``npositions`` is ``(nnodes,3)``. This attribute exists only if "nodes*.csv" files are present in the result directory.
    nvelocities : list of numpy arrays
        Nodes' velocities for every saved steps. Noting nnodes the number of nodes in the simulations, the shape of ``nvelocities[i]`` is ``(nnodes,3)``.
    naccelerations : list of numpy arrays
        Nodes' acceleration, solution of the motion equation, for every saved steps. Noting nnodes the number of nodes in the simulations, the shape of ``naccelerations[i]`` is ``(nnodes,3)``.
    next_forces : list of numpy arrays
        External forces on all nodes for each step. Noting nnodes the number of nodes in the simulations, the shape of ``next_forces[i]`` is ``(nnodes,3)``.
    nint_forces : list of numpy arrays
        Internal forces on all nodes for each step. Noting nnodes the number of nodes in the simulations, the shape of ``nint_forces[i]`` is ``(nnodes,3)``.
    nfrict_forces : list of numpy arrays
        Frictional forces on all nodes for each step. Noting nnodes the number of nodes in the simulations, the shape of ``nfrict_forces[i]`` is ``(nnodes,3)``.
    nunb_forces : list of numpy arrays
        Unbalanced forces on all nodes for each step, computed as the nodal mass times its acceleration (Cundall's damping is then included). Noting nnodes the number of nodes in the simulations, the shape of ``nunb_forces[i]`` is ``(nnodes,3)``.
    nmasses : list of numpy arrays
        Nodes' masses for every saved steps. Noting nnodes the number of nodes in the simulations, the shape of ``nmasses[i]`` is ``(nnodes,)`` for any i. This attribute exists only if "nodes*.csv" files are present in the result directory.
    nfrict_work : list of numpy arrays
        Cumulated work of the frictional forces for every saved steps. Noting nnodes the number of nodes in the simulations, the shape of ``nfrict_work[i]`` is ``(nnodes,)`` for any i. This attribute exists only if "nodes*.csv" files are present in the result directory.
    raw_nodes_data : list of pandas dataframes
        All data saved in the nodes CSV files. The data is stored for each time step as a dataframe.
    has_node_data : bool
        Wether or not load data were loaded.
    steps : list of ints
        All saved steps. 
    times : list of floats
        All times corresponding to saved steps.
    dt : float
        Time step used for this simulation.
    ndims : int
        Number of dimensions in this simulation.
    detailed_timing : dict
        Dictionary containing all the timing data (extracted from `timing.json`)
    main_loop_time : float
        Time spent executing the main loop
    total_time : float
        Time spend executing the simulation (including the initialisation)
    nthreads : int
        Number of threads used to run the simulation
    average_speed : float
        Average speed computed over all the iteration in the main MPM loop
    speed_fct_steps : numpy array
        Array of shape `(verbosity+1, 2)` containing the values of the averaged speed (column 1) for at a specific step (column 0)
    main_dir : str
        Path to the simulation's directory
    res_dir : str
        Path to the simulation's results directory
    fill_nan : int
        Number of additional `numpy.nan` at the end of the results
    """
    def __init__(self, directory, load_step=1, load_nodes_data=False, fill_nan=0):
        if directory[-1] != '/': directory += '/'
        self.main_dir = directory
        self.res_dir = directory + "results/"

        self.fill_nan = fill_nan
        
        self.load_nodes_data = load_nodes_data

        with open(self.main_dir + "input_file.json", 'r') as fil: lines = fil.readlines()
        for l in lines:
            if '"title"' in l: self.title = l.split('"')[-2]
            if '"dt"' in l: self.dt = float(l.split(' ')[-1][:-2])
            if '"node_type"' in l: self.ndims = 3 if "N3D" in l else 2

        self.data_dir = self.res_dir + self.title + '/'
        
        self.__extract_data(load_step)

        self.times = [self.dt*step for step in self.steps]
    
    def load_simulation(self):
        """Load the simulation object used to write the input files

        Returns
        -------
        :class:`~pycbg.preprocessing.Simulation` object
            The simulation object used to create the results loaded with :class:`~pycbg.postprocessing.ResultsReader`.
        
        """
        save_name = self.main_dir + self.title + ".Simulation"
        with open(save_name, 'rb') as fil : sim = pickle.load(fil)
        
        return sim
    
    def get_shapefn(self):
        """Get the value of the saved shape functions. Only works if the parameter `save_shapefn` in :class:`~pycbg.preprocessing.Mesh` is not empty.
        
        Returns
        -------
        tuple (dict, numpy.array)
            Tuple containing 1) a dictionary mapping the nodes id to the column in 2) the numpy array of shape `(shapefn_resolution**n_dims, n_dims + len(save_shapefn))`.
        """
        shapefn_file = self.res_dir + "shapefn.csv"
        if not os.path.exists(shapefn_file): raise FileNotFoundError("The shape function CSV file does not exists. Please make sure to set the `save_shapefn` parameter in the Mesh object.")
        with open(shapefn_file, "r") as fil: header = fil.readline().split("\t")
        header[-1] = header[-1][:-1] # Remove the trailing '\n'
        dict = {int(col_lab.split("_")[-1]): i_col for i_col, col_lab in enumerate(header) if "node_" in col_lab}
        return dict, np.genfromtxt(shapefn_file, delimiter='\t', skip_header=1)
    
    def get_gradshapefn(self):
        """Get the value of the saved shape functions gradient. Only works if the parameter `save_shapefn` in :class:`~pycbg.preprocessing.Mesh` is not empty and `save_shapefn_grad` is True.
        
        Returns
        -------
        tuple (dict, numpy.array)
            Tuple containing 1) a dictionary mapping the nodes id to the column in 2) the numpy array of shape `(shapefn_resolution**n_dims, n_dims + len(save_shapefn))`.
        """
        gradshapefn_file = self.res_dir + "gradshapefn.csv"
        if not os.path.exists(gradshapefn_file): raise FileNotFoundError("The shape function CSV file does not exists. Please make sure to set the `save_shapefn` and `save_shapefn_grad` parameters in the Mesh object.")
        with open(gradshapefn_file, "r") as fil: header = fil.readline().split("\t")
        header[-1] = header[-1][:-1] # Remove the trailing '\n'
        dict = {int(col_lab.split("_")[-1]): i_col for i_col, col_lab in enumerate(header) if "node_" in col_lab}
        return dict, np.genfromtxt(gradshapefn_file, delimiter='\t', skip_header=1)
    
    def __extract_data(self, load_step=1):
        files = os.listdir(self.data_dir)
        p_files, n_files = [], []
        for f in files:
            if f[-4:]=='.csv' and "particles" in f: p_files.append(f)
            if f[-4:]=='.csv' and "nodes" in f and self.load_nodes_data: n_files.append(f)

        def sort_key(filename): return int(''.join(re.findall(r'\d', filename)))
        p_files.sort(key=sort_key)
        n_files.sort(key=sort_key)
        
        if not n_files and self.load_nodes_data: warnings.warn("No CSV files found for nodes, please make sure the `write_nodes_csv` analysis parameter was set to `True` during preprocessing", NewFeatureWarning)

        if type(load_step)==str:
            str_test = load_step.lower()
            if str_test=="first": p_files, n_files = p_files[:1], n_files[:1]
            elif str_test=="last": p_files, n_files = p_files[-1:], n_files[-1:]
            else: raise ValueError("`load_step` set to {:}. If `load_step` is a string, it should be either 'first' or 'last' (case insensitive).".format(load_step))
        elif type(load_step)==int:
            if load_step>1: p_files, n_files = p_files[::load_step], n_files[::load_step]
            elif load_step<1: raise ValueError("`load_step` set to {:d}. If `load_step` is an integer, it should be at least 1.".format(load_step))
        else: raise ValueError("`load_step` is of type {:}, while it should be either an integer or a string.".format(type(load_step)))

        self.raw_data, self.steps = [], []
        for f in p_files: 
            self.raw_data.append(pd.read_csv(self.data_dir + f, sep="\t", header=0))
            self.steps.append(int(f[9:-4]))
            
        self.raw_nodes_data = [pd.read_csv(self.data_dir + f, sep="\t", header=0) for f in n_files]

        for i_nan in range(self.fill_nan):
            self.steps.append(np.nan)

            p_df = pd.DataFrame(np.nan, index=self.raw_data[0].index, columns=self.raw_data[0].columns)
            p_df["id"] = self.raw_data[-1]["id"]
            self.raw_data.append(p_df)

            if n_files:
                n_df = pd.DataFrame(np.nan, index=self.raw_nodes_data[0].index, columns=self.raw_nodes_data[0].columns)
                n_df["id"] = self.raw_nodes_data[-1]["id"]
                self.raw_nodes_data.append(n_df)

        # Get the initial number of material points and nodes
        with open(self.main_dir+"particles.txt", 'r') as fil: n_mp_init = int(fil.readline()[:-1])
        with open(self.main_dir+"mesh.txt", 'r') as fil: n_nodes = int(fil.readline()[:-1].split("\t")[0])
        
        # Check if some motion integration related columns are present in the results
        aa_mi_used, t_mi_used = [False]*2
        if self.raw_data and "B_xx" in self.raw_data[0]: # Affine augmented motion integration strategy was used
            aa_mi_used = True
            self.Bs, self.Ds, self.Cs = [], [], []
        elif self.raw_data and "gV_xx" in self.raw_data[0]: # Taylor motion integration strategy was used
            t_mi_used, self.gVs = True, []
            
        self.ppositions, self.pvelocities = [], []
        self.pstresses, self.pstrains, self.ppressures = [], [], []
        self.pmasses, self.pvolumes, self.pmaterials = [], [], []
        self.pcell_ids = []
        for i_res, df in enumerate(self.raw_data):
            ids = list(df["id"])

            # Positions
            ppos = np.full([n_mp_init, 3], np.nan)
            ppos_df = np.array([df[key] for key in ["coord_x", "coord_y", "coord_z"]]).T
            for i, p_id in enumerate(ids): ppos[p_id,:] = ppos_df[i,:]
            self.ppositions.append(ppos)

            # Velocities
            pvel = np.full([n_mp_init, 3], np.nan)
            pvel_df = np.array([df[key] for key in ["velocity_x", "velocity_y", "velocity_z"]]).T
            for i, p_id in enumerate(ids): pvel[p_id,:] = pvel_df[i, :]
            self.pvelocities.append(pvel)

            # Stresses
            psig = np.full([n_mp_init, 6], np.nan)
            psig_df = np.array([df[key] for key in ["stress_xx", "stress_yy", "stress_zz", "tau_xy", "tau_yz", "tau_xz"]]).T
            for i, p_id in enumerate(ids): psig[p_id,:] = psig_df[i, :]
            self.pstresses.append(psig)
            
            # Strains
            peps = np.full([n_mp_init, 6], np.nan)
            peps_df = np.array([df[key] for key in ["strain_xx", "strain_yy", "strain_zz", "gamma_xy", "gamma_yz", "gamma_xz"]]).T
            for i, p_id in enumerate(ids): peps[p_id,:] = peps_df[i, :]
            self.pstrains.append(peps)

            # Cell ids
            self.pcell_ids.append(df['cell_id'].to_numpy())

            # Pressures
            ppre = np.full([n_mp_init], np.nan)
            ppre_df = df['pressure'].values
            for i, p_id in enumerate(ids): ppre[p_id] = ppre_df[i]
            self.ppressures.append(ppre)

            # Materials
            pmat = np.full([n_mp_init], np.nan)
            pmat_df = df['material_id'].values
            for i, p_id in enumerate(ids): pmat[p_id] = pmat_df[i]
            self.pmaterials.append(pmat)

            # Volumes
            pvol = np.full([n_mp_init], np.nan)
            pvol_df = df['volume'].values
            for i, p_id in enumerate(ids): pvol[p_id] = pvol_df[i]
            self.pvolumes.append(pvol)

            # Masses
            pmas = np.full([n_mp_init], np.nan)
            pmas_df = df['mass'].values
            for i, p_id in enumerate(ids): pmas[p_id] = pmas_df[i]
            self.pmasses.append(pmas)
            
            # B matrix, if present
            if aa_mi_used:
                Bps = np.full([n_mp_init, self.ndims, self.ndims], np.nan)
                if self.ndims == 3: # Test before looping, so there are less tests performed
                    for i, p_id in enumerate(ids):
                        Bps[p_id] = np.array([
                            [df['B_xx'].values[i], df['B_xy'].values[i], df['B_xz'].values[i]],
                            [df['B_yx'].values[i], df['B_yy'].values[i], df['B_yz'].values[i]],
                            [df['B_zx'].values[i], df['B_zy'].values[i], df['B_zz'].values[i]]
                        ])
                elif self.ndims == 2:
                    for i, p_id in enumerate(ids):
                        Bps[p_id] = np.array([
                            [df['B_xx'].values[i], df['B_xy'].values[i]],
                            [df['B_yx'].values[i], df['B_yy'].values[i]]
                        ])
                self.Bs.append(Bps)
                
            # D matrix, if present
                Dps = np.full([n_mp_init, self.ndims, self.ndims], np.nan)
                if self.ndims == 3: # Test before looping, so there are less tests performed
                    for i, p_id in enumerate(ids):
                        Dps[p_id] = np.array([
                            [df['D_xx'].values[i], df['D_xy'].values[i], df['D_xz'].values[i]],
                            [df['D_xy'].values[i], df['D_yy'].values[i], df['D_yz'].values[i]],
                            [df['D_xz'].values[i], df['D_yz'].values[i], df['D_zz'].values[i]]
                        ])
                elif self.ndims == 2:
                    for i, p_id in enumerate(ids):
                        Dps[p_id] = np.array([
                            [df['D_xx'].values[i], df['D_xy'].values[i]],
                            [df['D_xy'].values[i], df['D_yy'].values[i]]
                        ])
                self.Ds.append(Dps)
                
            # C matrix, computed from B and D
                Cps = np.full([n_mp_init, self.ndims, self.ndims], np.nan)
                for i, p_id in enumerate(ids):
                    Bp, Ds = self.Bs[-1][i], self.Ds[-1][i]
                    try: Cps[p_id] = Bp.dot(np.linalg.inv(Ds))
                    except np.linalg.LinAlgError:
                        warnings.warn(f"The D matrix could not be inverted for material point n°{p_id} at step n°{self.steps[i_res]} (t={self.times[i_res]:.2e} s), the corresponding element in Cs will be `np.nan`", RuntimeWarning)
                self.Cs.append(Cps)
                
            # Velocity gradient, if present
            if t_mi_used:
                gVps = np.full([n_mp_init, self.ndims, self.ndims], np.nan)
                if self.ndims == 3: # Test before looping, so there are less tests performed
                    for i, p_id in enumerate(ids):
                        gVps[p_id] = np.array([
                            [df['gV_xx'].values[i], df['gV_xy'].values[i], df['gV_xz'].values[i]],
                            [df['gV_yx'].values[i], df['gV_yy'].values[i], df['gV_yz'].values[i]],
                            [df['gV_zx'].values[i], df['gV_zy'].values[i], df['gV_zz'].values[i]]
                        ])
                elif self.ndims == 2:
                    for i, p_id in enumerate(ids):
                        gVps[p_id] = np.array([
                            [df['gV_xx'].values[i], df['gV_xy'].values[i]],
                            [df['gV_yx'].values[i], df['gV_yy'].values[i]]
                        ])
                self.gVs.append(gVps)
        
        if len(self.raw_nodes_data)>0:
            self.has_node_data = True
            # self.nvolumes, self.npressures = [[] for _ in range(2)]
            self.nmasses, self.nfrict_work = [[] for _ in range(2)]
            self.nvelocities, self.naccelerations, self.next_forces, self.nint_forces, self.nfrict_forces, self.nunb_forces = [[] for _ in range(6)]
            for df in self.raw_nodes_data:
                # Masses
                self.nmasses.append(np.array(df['mass'].values))
                
                # The following fields exist in the CSV file (and in CB-Geo MPM) but are always 0, probably because this data on nodes is useless
                # Volumes
                # self.nvolumes.append(df['volume'].values)
                
                # # Pressures
                # self.npressures.append(df['pressure'].values)
                
                # Friction energy
                self.nfrict_work.append(df['friction_energy'].values)
                
                # Velocities
                self.nvelocities.append(np.array([df[key] for key in ["velocity_x", "velocity_y", "velocity_z"]]).T)
                
                # Accelerations
                self.naccelerations.append(np.array([df[key] for key in ["acceleration_x", "acceleration_y", "acceleration_z"]]).T)
                
                # External forces
                self.next_forces.append(np.array([df[key] for key in ["ext_force_x", "ext_force_y", "ext_force_y"]]).T)
                
                # Internal forces
                self.nint_forces.append(np.array([df[key] for key in ["int_force_x", "int_force_y", "int_force_y"]]).T)
                
                # Internal forces
                self.nfrict_forces.append(np.array([df[key] for key in ["frict_force_x", "frict_force_y", "frict_force_z"]]).T)
                
                # Unbalanced force
                self.nunb_forces.append(self.naccelerations[-1] * self.nmasses[-1][:, np.newaxis]) # Includes Cundall's damping
                
                
            # Positions
            self.npositions = np.array([df[key] for key in ["coord_x", "coord_y", "coord_z"]]).T # using the last df object
        else: self.has_node_data = False
        
        # Loading the data from the Json timing file
        timing_json_path = self.data_dir + "timing.json"
        try:
            with open(timing_json_path) as f: timing_dict = json.load(f)
            self.main_loop_time = timing_dict["main_loop_time"]
            self.total_time = timing_dict["total_time"]
            self.nthreads = timing_dict["nthreads"]
            self.average_speed = timing_dict["average_speed"]
            
            try: self.detailed_timing = timing_dict["detailed_timing"]
            except KeyError:
                warnings.warn("`detailed_timing` could not be loaded, please check your version of CB-Geo MPM and the value of the TIMING_DEPTH configuration variable", NewFeatureWarning)
        except FileNotFoundError:
            warnings.warn(f"{timing_json_path} file not found, the attributes `detailed_timing`, `main_loop_time`, `total_time`, `nthreads` and `average_speed` will not be defined, please check your version of CB-Geo MPM", NewFeatureWarning)
            
        # Loading the speed data from the CSV file
        speed_csv_path = self.data_dir + "speed.csv"
        try:
            self.speed_fct_steps = np.genfromtxt(speed_csv_path, skip_header=1, delimiter="\t")
        except FileNotFoundError:
            warnings.warn(f"{speed_csv_path} file not found, the attribute `speed_fct_steps` will not be defined, please check your version of CB-Geo MPM", NewFeatureWarning)

__ind_sgmts = [[0,1], [1,2], [2,3], [3,0],
               [4,5], [5,6], [6,7], [7,4],
               [0,4], [1,5], [2,6], [3,7]]

__ind_gimp_sgmts = [[8,19], [9, 18], [24,31], [25,30], 
                    [17,21], [16,20], [12,22], [13,23],
                    [14,10], [15,11], [28,26], [29,27],
                    [16,12], [17,13], [20,22], [21,23],
                    [8,24], [9,25], [19,31], [18,30],
                    [14,28], [15,29], [10,26], [11,27],
                    [32,52], [35,53], [34,54], [33,55],
                    [39,50], [36,49], [37,48], [48,51],
                    [47,41], [44,40], [46,42], [45,43]]

def plot_mesh(mesh, fig=None, ax=None):
    if fig is None and ax is None: 
        fig = plt.figure(1, figsize=(15,10))
        ax = fig.add_subplot(111, projection='3d')

    added_segments, added_dotted_segments = [], []
    for cell in mesh.cells:
        nodes = [mesh.nodes[i_node] for i_node in cell]
        # for i, node in enumerate(nodes): ax.text(*node, str(i)) # to print node numbers
        xs = [[nodes[i][0], nodes[j][0]] for i,j in __ind_sgmts]
        ys = [[nodes[i][1], nodes[j][1]] for i,j in __ind_sgmts]
        zs = [[nodes[i][2], nodes[j][2]] for i,j in __ind_sgmts]

        for seg in zip(xs, ys, zs): 
            if seg not in added_segments: 
                ax.plot(*seg, color="black")
                added_segments.append(seg)

        if not mesh.cell_type=="ED3H64G": continue

        xds = [[nodes[i][0], nodes[j][0]] for i,j in __ind_gimp_sgmts]
        yds = [[nodes[i][1], nodes[j][1]] for i,j in __ind_gimp_sgmts]
        zds = [[nodes[i][2], nodes[j][2]] for i,j in __ind_gimp_sgmts]

        for seg in zip(xds, yds, zds): 
            if seg not in added_dotted_segments: 
                ax.plot(*seg, color="gray", linestyle="dotted")
                added_dotted_segments.append(seg)

    
    ax.set_xlabel(r"x", labelpad=10)
    ax.set_ylabel(r"y", labelpad=10)
    ax.set_zlabel(r"z", labelpad=10)

    return fig 

class BatchResultsReader():
    def __init__(self, directory, njobs=1, load_step=1, load_nodes_data=True, fail_flag=True, fill_missing=False, load_sim_ids="all"):
        # Get bacth directory 
        if directory[-1] != '/': directory += '/'
        self.batch_dir = directory
        
        # Set attributes
        self.load_step = load_step
        self.fill_missing = fill_missing
        self.load_nodes_data = load_nodes_data
        self._fail_flag = fail_flag
        self.njobs = njobs
        self.load_sim_ids = load_sim_ids
        
        # Load parameter sets table
        self.sims_vars, self.batch_parameters = self._load_parameter_sets_table()
        self.nsims = len(self.sims_vars)
        self.nparams = len(self.batch_parameters)
        
        # Determine how much NaN have to be added to which simulation, if fill_missing is True
        nan_fill = self._get_nan_quantity()
        
        # Load all simulations
        self.all_results = list(self._load_all_sims(nan_fill))
        self.sims = self._load_sim_objects()
    
    def get_attr_all_sims(self, attribute, fixed_batch_params={}):
        for param, val in fixed_batch_params.items():
            if param not in self.batch_parameters.keys():
                raise KeyError(f"The parameter {param} is not among the batch parameters")
            if val not in self.batch_parameters[param]:
                raise ValueError(f"The parameter {param} didn't have the value {val} for this batch")
            
        if isinstance(attribute, list): several_attr = True
        elif isinstance(attribute, str): several_attr = False
        else: raise TypeError(f"The attribute {attribute} should be either a `str` or a `list`, you passed a {type(attribute)}")
        
        all_attr, sim_nums = [], []
        for i_sim, results in enumerate(self.all_results):
            if not self._sim_meet_cond(fixed_batch_params, self.sims_vars[i_sim]): continue
            if several_attr:
                vals_list = [getattr(results, attr) for attr in attribute]
                all_attr.append(vals_list)
            else: all_attr.append(getattr(results, attribute))
            sim_nums.append(i_sim)

        if not several_attr: return sim_nums, all_attr
        
        return sim_nums, [attr_vals for attr_vals in zip(*all_attr)]
            
    def _sim_meet_cond(self, fixed_batch_params, sim_vars):
        for param, val in fixed_batch_params.items():
            if val!=sim_vars[param]: return False
        return True

    def _load_parameter_sets_table(self):
        # Read the table file (handling table file name for older version of PyCBG)
        try:
            with open(self.batch_dir + "parameters_sets.table", 'r') as fil: lines = fil.readlines() 
        except FileNotFoundError: 
            with open(self.batch_dir + "parameters_set.table", 'r') as fil: lines = fil.readlines()
        
        # Check if the user wants to load all simulations
        load_all = False
        if isinstance(self.load_sim_ids, str):
            if self.load_sim_ids != "all": raise ValueError(f"`load_sim_ids` Can only have the string value 'all', you've set it to {self.load_sim_ids}")
            load_all = True
            self._sims_ids = list(range(len(lines)-1))
        elif isinstance(self.load_sim_ids, list): self._sims_ids = self.load_sim_ids
        else: raise TypeError(f"`load_sim_ids` should be either a string, or a list of integers, you've passed an object of type {type(self.load_sim_ids)}")
        
        # Extract data
        header = lines[0][:-1].split("\t")
        sims_vars = {}
        for i_sim, line in enumerate(lines[1:]):
            # Check if the user want to load some specific sims
            if not load_all and i_sim not in self.load_sim_ids: continue
                
            # Split the line into a list of variable of relevant type
            sl = []
            for i in line.split("\t"):
                try: sl.append(float(i)) # handle numerical data
                except ValueError: sl.append(i.strip("\n")) # handle string data
            dic = {}
            
            # Construct the dictionary containing the values of all columns, identified by the column name
            for key, val in zip(header, sl): dic[key] = val
            
            # Determine the simulation directory
            sim_dir = self.batch_dir + "sim{:d}".format(i_sim)
            
            # Put all variables specific to this simulation in a dictionary, under the key it was given in the first column of the table 
            vars_dict = {"sim_id": dic[header[0]], "sim_dir": sim_dir, "sim_number": i_sim, **dic}
            sims_vars[dic[header[0]]] = vars_dict
                # Make possible to access the simulation varable dictionary using a second key (an alias), if it does not conflict with any sim_id
            if i_sim not in sims_vars.keys(): sims_vars[i_sim] = vars_dict
        
        # Determine how many values each batch parameter can have
        all_vals_list = [[dic[param] for dic in sims_vars.values()] for param in header[1:]]
        all_vals_set = [set(vals) for vals in all_vals_list]
        params_possible_vals = {param: all_vals_set[i_p] for i_p, param in enumerate(header[1:])}
        
        return sims_vars, params_possible_vals
    
    def _get_nan_quantity(self):
        if self.fill_missing:
            nfiles = []
            for sim_vars in self.sims_vars.values():
                sim_dir = sim_vars["sim_dir"]
                i_sim = sim_vars["sim_number"]
                nfiles.append(len(glob.glob(f"{sim_dir}/results/sim{i_sim}/particles*.csv"))) 
            return [max(nfiles) - nf for nf in nfiles]
        else: return [0]*self.nsims
        
    def _load_all_sims(self, nan_fill):
        sim_dirs = [dic["sim_dir"] for dic in self.sims_vars.values()]
        if self.njobs==1: all_results = map(partial(load_sim_results, load_step=self.load_step, fail_flag=self._fail_flag, load_nodes_data=self.load_nodes_data), sim_dirs, nan_fill)
        elif self.njobs>1:
            self.njobs = min(self.njobs, self.nsims)
            inputs = [{"sim_dir": sim_dir, "load_step": self.load_step, "fail_flag": self._fail_flag, "load_nodes_data": self.load_nodes_data, "fill_nan": n_nan} for sim_dir, n_nan in zip(sim_dirs, nan_fill)]
            all_results = parmap(load_sim_results, inputs, self.njobs)
        elif self.njobs<1: raise ValueError(f"`self.njobs` is set to {self.njobs}, while it should be at least 1")
        
        return all_results

    def _load_sim_objects(self):
        sims = {}
        for i_sim, r in zip(self._sims_ids, self.all_results):
            sim = r.load_simulation()
            sims[self.sims_vars[i_sim]["sim_id"]] = sim
            if i_sim not in sims.keys(): sims[i_sim] = sim
        return sims
    
    def _get_old_load_batch_out(self):
        new_keys = ["sim_dir", "sim_number"]
        old_dics = [{key: val for key, val in dic.items() if key not in new_keys} for dic in self.sims_vars.values()]
        return [(dic, res) for dic,res in zip(old_dics, self.all_results)]
        

def load_batch_results(*args, **kwargs):
    """Load all simulations within a batch.

    Parameters
    ----------
    directory : str
        Directory in which all simulations' directories (sim0, sim1, ...) are located.
    njobs : int, optional
        Number of processes running in parallel when loading data. Each process will load a specific simulation. Default to 1.
    load_step : int or str among {'first', 'last'}, optional
        Can be used to skip some `particles*.csv` files when loading data, in the case of heavy simulations. See :class:`~pycbg.postprocessing.ResultsReader` for more details.
    load_nodes_data : bool
        Whether to load nodes CSV files, if present. Default to `False`.
    fail_flag : bool, optional
        If set to `True`, an error is raised in the eventuality that some files are missing. If set to `False`, a warning message is displayed and the data loading continues. Default to `True`.
    fill_missing : bool, optional
        If set to `True`, the results object of the simulations with the fewer CSV files will be filled with `numpy.nan` until the results has as much values as the results with the most CSV files. Useful when post-processing a batch when all simulations aren't over yet. Default is `False`.

    Returns
    -------
    list of tuples, e.g. [(<class 'dict'>, <class 'pycbg.postprocessing.ResultsReader'>)]
        List including as many tuple items as simulations in the batch, where each tuple associates a dictionary containing the used parameter set  together with a ResultsReader instance for that simulation and its results. If a simulation was not found and the fail_flag was set to `False`, the tuple corresponding to a missing simulations is of type (<class 'dict'>, None).
    """
    warnings.warn("The `load_batch_results` function has been replace with the `BatchResultsReader` class, please update your script. Redirecting input to `BatchResultsReader(inputs)._get_old_load_batch_out()`", DeprecationWarning)
    return BatchResultsReader(*args, **kwargs)._get_old_load_batch_out()
    

def load_sim_results(sim_dir, fill_nan=0, load_step=1, fail_flag=True, load_nodes_data=False):
    if fail_flag: results = ResultsReader(sim_dir, load_step, load_nodes_data)
    else:
        try: results = ResultsReader(sim_dir, load_step, load_nodes_data, fill_nan=fill_nan)
        except FileNotFoundError:
            warnings.warn(f"Loading simulation {sim_dir} failed because a file was missing, skipped it")
            return
    return results

# Taken from stackoverflow answer 16071616, because the multiprocessing.Pool object doesn't work well in this case
def __fun(f, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, f(**x)))

# Taken from stackoverflow answer 16071616
def parmap(f, X, nprocs=mp.cpu_count()):
    q_in = mp.Queue(1)
    q_out = mp.Queue()

    proc = [mp.Process(target=__fun, args=(f, q_in, q_out)) for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(X)]
    [q_in.put((None, None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in sorted(res)]
