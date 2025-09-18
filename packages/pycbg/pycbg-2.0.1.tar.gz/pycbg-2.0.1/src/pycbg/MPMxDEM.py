import sys, os, inspect, importlib, json, warnings, datetime, pickle
import glob as gb, numpy as np, itertools as it
from decimal import Decimal
import pycbg

def warning_format(message, category, filename, lineno, file=None, line=None): 
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return '[%s] [PyCBG] [%s] %s#%s %s\n' % (time, category.__name__, filename, lineno, message)
warnings.formatwarning = warning_format

## Beware, anything defined globally in this module (except variable whose names are in the no_auto_import list) is also imported in the main script (the one importing this module) upon calling __update_imports (which is called by several functions of this module)

no_auto_import = ["glob", "rve_directory", "pycbg_sim", "yade_sha1"]
no_yade_import = ["prefix", "libDir"]

# Initialise glob dictionary
glob = set(globals())

def __update_imports(custom_dict={}):
    global glob

    # Create a dictionary with all variables to be imported by main module
    all_vars = {**custom_dict} # **globals(), 

    # Get new keys with respect to last call
    new_keys = list(glob ^ set(all_vars))

    # Import all non-system variable into main script
    for key, val in all_vars.items():
        if key not in new_keys: continue
        if key not in no_auto_import: sys.modules['builtins'].__dict__[key] = val

    # Update glob dictionary, so at next call only new items will be processed
    glob = set(globals())

def __on_yade_setup():
    global rve_directory, pycbg_sim, yade_sha1
    # Get PyCBG simulation object
    with open(gb.glob("*.Simulation")[0], 'rb') as fil : pycbg_sim = pickle.load(fil)

    # Create rve_data directory
    rve_directory = "rve_data/"
    os.makedirs(rve_directory, exist_ok=True)

def __import_condition(varname, var): 
    sv = str(var)
    cond = not varname.startswith('_') # exclude private variables
    cond = cond and "yade" in sv # import all variables in the yade namespace
    cond = cond and varname not in no_yade_import # except the one specified in no_yade_import
    
    cond_func = "function" in sv # import all functions
    cond_func = cond_func and "Boost" not in sv # except the one defined with Boost
    cond_func = cond_func and "built-in" not in sv # and the built-in ones
    return cond or cond_func
    
def setup_yade(yade_exec="/usr/bin/yade", no_banner=True):
    """Import YADE in the current scope and create a directory for all RVEs data (samples, vtk files, ...). The YADE simulation should be set as periodic by the user (non periodic simulations are not supported).

    Parameters
    ----------
    yade_exec : str
        Full path to the YADE executable. 
    no_banner : bool
        If True, the usual banner printed to stdout upon launching YADE will not be displayed. Default to True. 
    """
    global yade_sha1, weak_refs, boost_func_dict

    # Load YADE
    exec_path, exec_name = yade_exec.rsplit("/", 1)

        ## Insert exec_path to path
    sys.path.append(exec_path)

        ## Perform an 'import *' on yade module (see https://stackoverflow.com/a/21221452)
    if no_banner: 
        fil = open(os.devnull, 'w')
        original_stdout = sys.stdout
        sys.stdout = fil

    yd = importlib.import_module(exec_name)
    yade_dict = yd.__dict__
    
    # Directly copy the strong references to Boost Python functions (they cannot be weakreferred to from Python)
    boost_func_dict = {name: val for name, val in yade_dict.items() if "Boost.Python.function" in str(val)}
    globals().update(boost_func_dict)
    sys.modules['builtins'].__dict__.update(boost_func_dict)
    
    if no_banner: 
        sys.stdout = original_stdout
        fil.close()
    
        ## Get git's SHA1
    try: yade_sha1 = yade_dict["version"].split("-")[-1]
    except NameError: yade_sha1 = "release-"

        ## Print all versions to a file
    if not os.path.isfile('yade_all_versions.txt'):
        original_stdout = sys.stdout 
        with open('yade_all_versions.txt', 'w', encoding="utf-8") as f:
            sys.stdout = f 
            yade_dict["printAllVersions"]()
            sys.stdout = original_stdout
    
    # Print pycbg version to a file
    if not os.path.isfile('pycbg_version.txt'):
        original_stdout = sys.stdout 
        with open('pycbg_version.txt', 'w') as f:
            sys.stdout = f 
            print(pycbg.__version__)
            sys.stdout = original_stdout

    try: __on_yade_setup()
    except Exception as e: 
        warnings.warn("The following Python exception occured when running extra setup steps: \n\t|{:}: {:}\n\tThe current session is then a simple YADE session.\n".format(type(e).__name__, e))

    # Update variables in main script
    yade_dict = yd.__dict__ # In case __on_yade_setup adds yade variables
    to_import = {name: val for name, val in yade_dict.items() if __import_condition(name, val)}
    __update_imports(to_import)

class DefineCallable():
    """Callable object to be called at each MPM step, with CB-Geo's required signature. The YADE periodic simulation defined in the script creating this callable object will be deformed at each MPM iteration using `O.cell.velGrad`. If `strain_rate` is set, the velocity gradient is computed using the strain increment provided by CB-Geo and the `dem_strain_rate` parameter provided by the user: `O.cell.velGrad = strain_increment_matrix / max(strain_increment_matrix) * dem_strain_rate`. If `strain_rate` is `None`, the velocity gradient is the MPM strain rate (inertial effects should probably then be accounted for). 

    Parameters
    ----------
    dem_strain_rate : float, callable or None
        Strain rate applied to the RVE. If a callable is specified, the strain rate will be set to the return value of this callable. If `None`, the MPM strain rate is used.
    fixed_strain_rate : bool
        Whether to fix the strain rate or the DEM time step to reach exactly the required deformation. If the strain rate is fixed, the DEM time step will be adjusted for the last (possibly the only) DEM iteration. If the DEM time step is fixed, the deformation time is increased to the next multiple of the DEM time step, decreasing the strain rate. If strain_rate is `None`, this parameter is not relevant. Default is `True`.
    inertial : bool
        Whether or not to account for inertial effects when computing the stress tensor global to the RVE. Default is False.
    fixed_dem_dt: bool
        Whether or not to fix the DEM time step to its initial value during all the simulation. If False, an instance of YADE's `GlobalStiffnessTimeStepper` has to be present in the engine list, it will be called automatically at the beginning of each MPM step. Default is False.  
    impose_strain_rate : bool
        Whether to strictly impose the DEM strain rate specified by the `dem_strain_rate` parameter. If True, the RVE will be deformed using `dem_strain_rate` no matter the strain rate required by the MPM. If False, The RVE will be deformed using the maximum of the `dem_strain_rate` and the strain rate required by the MPM. Default is False.
    run_on_setup : callable or None
        Name of the function to be run on RVE setup, if not None. This function is called after `rve_id` is defined, `run_on_setup` can thus refer to it.
    vtk_period : int
        Period at which VTK files are saved. If positive, `vtk_period` is the period in terms of DEM iterations (it is passed to YADE's `VTKRecorder` engine as `iterPeriod`). If negative, `-vtk_period` is the period in terms of MPM iterations (the number of MPM iterations between two VTK files). Default is 0 (no VTK file is saved).
    state_vars : list of str
        List of python expressions that should return a scalar, to be save as state variable in the CB-Geo simulation. `state_vars` should have at most 19 elements, the first element being called `svars_1` in CB-Geo, the second `svars_2`, ... . Default to `["O.iter, O.time, O.dt"]`.
    svars_dic : dict
        Dictionary in which all elements of `state_vars`are evaluated. Most users need to set `svars_dic=globals()`.
    save_final_state : bool
        Whether or not to save the RVE final state in a ".{SHA1}yade.bz2" file, where "{SHA1}" is git's last commit SHA1 of YADE. Default is `False`.
    flip_cell_period : int
        YADE's `flipCell` is called every `flip_cell_period`, which flips the RVE toward more axis-aligned base cell vectors if it is possible.
    log_inputs : bool
        Whether or not to save the inputs send by the MPM to each RVE in CSV files in the rve directory (see `DefineCallable.rve_directory`). Useful for debugging, but beware: depending on the number of MPM steps and the number of RVEs, these inputs logs might be very heavy.

    Attributes
    ----------
    dem_strain_rate : float
        Strain rate applied to the RVE.
    fixed_strain_rate : bool
        Whether to fix the strain rate or the DEM time step to reach exactly the required deformation.
    fixed_dem_dt: bool
        Whether or not to fix the DEM time step to its initial value during all the simulation.
    inertial : bool
        Whether or not to account for inertial effects when computing the stress tensor global to the RVE.
    impose_strain_rate : bool
        Whether to strictly impose the DEM strain rate specified by the `dem_strain_rate` parameter.
    run_on_setup : callable or None
        Name of the function to be run on RVE setup, if not None. This function is called after `rve_id` is defined, `run_on_setup` can thus refer to it.
    vtk_period : int
        Period at which VTK files are saved.
    state_variables : list of str
        List of python expressions that should return a scalar, to be save as state variable in the CB-Geo simulation. `state_vars` should have at most 19 elements, the first element being called `svars_1` in CB-Geo, the second `svars_2`, ... . Default to `["O.iter, O.time, O.dt"]`.
    save_final_state : bool
        Whether or not to save the RVE final state in a ".{SHA1}yade.bz2" file, where "{SHA1}" is git's last commit SHA1 of YADE. Default is `False`.
    log_inputs : bool
        Whether or not to save the inputs send by the MPM to each RVE in CSV files in the rve directory (see `DefineCallable.rve_directory`).
    rve_id : int
        The 'particle_id' of the current RVE, as numbered by CB-Geo. Before the first call of the object by CB-Geo, `rve_id=nan`, it is set to the actual particle id right before calling `run_on_setup`.
    rve_directory : str
        Path to the directory containing all RVEs data (samples, vtk files, ...), which is a subdirectory of PyCBG's simulation directory.
    pycbg_sim : :class:`~pycbg.preprocessing.Simulation` object
        PyCBG's simulation object used to create the input files.
    yade_sha1 : str
        Partial SHA1 of YADE's version
    flip_cell_period : int
        YADE's `flipCell` is called every `flip_cell_period`, which flips the RVE toward more axis-aligned base cell vectors if it is possible.
    flip_count : int
        Number of time the DEM cell has been flipped
    mpm_dt : float
        The MPM time step for the current simulation
    dem_dt : float
        The DEM time step. It is required in the background in the eventuality where the RVE deformation time is lower than the initial DEM time step.
    mpm_iter : int
        The current MPM iteration
    dstrain : numpy array of shape (3,3)
        Strain increment for the current MPM iteration
    dstress : numpy array of shape (3,3)
        Stress increment for the current MPM iteration
    deformation_time : float
        The time during which the deformation increment has been applied to the RVE. It is initialized at np.nan and is updated as soon as it is computed (right before using it).  
    """

    def __init__(self, dem_strain_rate, fixed_strain_rate=True, inertial=False, fixed_dem_dt=False, impose_strain_rate=False, run_on_setup=None, vtk_period=0, state_vars=["O.iter, O.time, O.dt"], svars_dic={}, save_final_state=False, flip_cell_period=0, log_inputs=False):
        if not callable(dem_strain_rate): 
            self.dem_strain_rate = dem_strain_rate
            self._adaptative_sr = False
        else: 
            self.dem_strain_rate = np.nan
            self._get_sr = dem_strain_rate
            self._adaptative_sr = True

        self.fixed_strain_rate = fixed_strain_rate
        self.fixed_dem_dt = fixed_dem_dt
        self.run_on_setup = run_on_setup
        self.vtk_period = vtk_period
        self.state_variables = state_vars
        self.svars_dic = svars_dic
        self.save_final_state = save_final_state
        self.rve_directory = rve_directory
        self.pycbg_sim = pycbg_sim
        self.yade_sha1 = yade_sha1
        self.rve_id = np.nan
        self.flip_cell_period = flip_cell_period
        self.flip_count = 0
        self.mpm_iter = 0
        self.mpm_dt = pycbg_sim.analysis_params["dt"]
        self.dem_dt = O.dt
        self.dstrain = np.zeros((3,3))
        self.dstress = np.zeros((3,3))
        self.sigma0 = np.zeros((3,3))
        self.deformation_time = np.nan
        self.inertial = inertial
        self.impose_strain_rate = impose_strain_rate
        self.log_inputs = log_inputs

        # Detect and kill GlobalStiffnessTimeStepper
        self._detect_gsts()

        self._vtkRec_ind = np.nan

    def __call__(self, rid, de_xx, de_yy, de_zz, de_xy, de_yz, de_xz, mpm_iteration, *state_vars):
        
        # Update mpm_iter attribute
        self.mpm_iter = mpm_iteration

        # Use usual strain, not the engineering one computed by CB-Geo
        de_xy, de_yz, de_xz = .5*de_xy, .5*de_yz, .5*de_xz

        # Set the dstrain attribute
        self.dstrain = np.array([[de_xx, de_xy, de_xz], [de_xy, de_yy, de_yz], [de_xz, de_yz, de_zz]])

        # If this function is called for the first time
        if mpm_iteration==0:
            ## Keep rve_id
            self.rve_id = int(rid)

            ## Run user's setup function
            if self.run_on_setup is not None: self.run_on_setup()

            ## Create RVE directory
            vtk_dir = rve_directory + "RVE_{:}/".format(self.rve_id) 
            if not os.path.isdir(vtk_dir): os.mkdir(vtk_dir)

            ## Add VTKRecorder to engines
            self._vtkRec_ind = len(O.engines) # VTKRecorder will be added to the end of the engine list
            if self.vtk_period>0: O.engines += [VTKRecorder(fileName=vtk_dir, recorders=["all"], iterPeriod=self.vtk_period)]
            elif self.vtk_period<0: O.engines += [VTKRecorder(fileName=vtk_dir, recorders=["all"], iterPeriod=1, dead=True)]

            ## Create the file where inputs are stored and write the header
            if self.log_inputs:
                in_param_names = list(inspect.signature(self.__call__).parameters)
                self.in_param_names = in_param_names[:-1] + ["svar{:d}:{:}".format(i+1, self.state_variables[i]) for i in range(len(eval(in_param_names[-1])))] + ["deformation_time", "max_deps"]
                self._inputs_file = rve_directory + "/RVE_{:}_inputs.csv".format(self.rve_id)
                with open(self._inputs_file, "w") as fil:
                    fil.write("\t".join(self.in_param_names) + "\n")

            ## Measure initial stress
            if self.inertial: self.sigma0 = getStress(O.cell.volume) + getTotalDynamicStress(O.cell.volume)
            else: self.sigma0 = getStress(O.cell.volume)

        # Shaping dstrain increment matrix
        dstrain_matrix = Matrix3((de_xx, de_xy, de_xz,
                                  de_xy, de_yy, de_yz,
                                  de_xz, de_yz, de_zz))

        # Get the maximum eigen value of the strain increment matrix
        try: max_deps = max([abs(i) for i in np.linalg.eig(dstrain_matrix)[0]])
        except np.linalg.LinAlgError: # Shouldn't happen as dstrain_matrix is symmetric
            warnings.warn("The strain increment matrix could not be diagonalised, using the maximum absolute coefficient instead of the maximum eigen value.")
            max_deps = max([abs(i) for i in [de_xx, de_yy, de_zz, de_xy, de_yz, de_xz]])

        # If user chose to set an adaptative strain rate, computes its value
        if self._adaptative_sr: 
            self.dem_strain_rate = self._get_sr()
            if self.dem_strain_rate==0: warnings.warn("The value of `dem_strain_rate` is zero, simulation will certainly fail. Please check your `dem_strain_rate` callable definition.")
        
        # Compute the DEM deformation time
        deformation_time = max_deps / self.dem_strain_rate if self.dem_strain_rate is not None else self.mpm_dt
        self.deformation_time = deformation_time if self.impose_strain_rate else min(deformation_time, self.mpm_dt)

        # Compute the velocity gradient, assuming no rotation
        O.cell.velGrad = dstrain_matrix / deformation_time

        # Run DEM steps
            # Set time step for the current MPM iteration
        self._set_demdt()
        self.dem_dt = O.dt # Store the DEM dt of the current MPM iteration

        if self.fixed_strain_rate: self.run_dem_steps_fsr(deformation_time) # adjust dem_dt to reach required deformation
        else: self.run_dem_steps_fdt(max_deps,dstrain_matrix) # reach required deformation without touching dem_dt

        # Write inputs to file
        if self.log_inputs:
            values = []
            for param in self.in_param_names:
                if param[:4]=="svar": values.append(eval(list(inspect.signature(self.__call__).parameters)[-1])[int(param[4:].split(":")[0])-1])
                elif param=="deformation_time": values.append(deformation_time)
                elif param=="max_deps": values.append(max_deps)
                else: values.append(eval(param))
            with open(self._inputs_file, "a") as fil: fil.write("\t".join(["{:e}".format(val) for val in values])+"\n")
        
        # Complete the MPM iteration
        mpm_iteration += 1
        if self.inertial: new_stress = getStress(O.cell.volume) + getTotalDynamicStress(O.cell.volume)
        else: new_stress = getStress(O.cell.volume)
        dsigma = new_stress - self.sigma0
        self.sigma0 = new_stress

        # Set the dstress attribute
        self.dstress = np.array(dsigma)

        # Update state variables
        state_vars = [eval(var, self.svars_dic) for var in self.state_variables]

        # If VTK files are saved depending on the MPM iterations
        if self.vtk_period<0 and self.mpm_iter%-self.vtk_period==0: self._save_vtk()

        # Save final state
        if mpm_iteration == pycbg_sim.analysis_params["nsteps"] and self.save_final_state:
            O.save(rve_directory + "RVE_{:}/".format(self.rve_id) + "rve{:d}_final_state.{:}yade.bz2".format(self.rve_id, self.yade_sha1))

        return (dsigma[0,0], dsigma[1,1], dsigma[2,2], dsigma[0,1], dsigma[1,2], dsigma[0,2], mpm_iteration) + tuple(state_vars)
    
    def run_dem_steps_fsr(self, deformation_time):
        '''Executes the appropriate number of DEM iterations through adjusting the DEM time step'''
        time_ratio = deformation_time/O.dt
        
        if time_ratio==0 : return # If MPM asks no deformation, do nothing
        
        elif time_ratio < 1: # If the deformation time is lower than the original dem time step
            O.dt = deformation_time # Use the deformation time as time step
            
        else: # If the deformation time is higher than the original dem time step
            for step in range(int(time_ratio)): self._run_dem_step() # Run steps until the remaining deformation time is lower than the original dt
            O.dt = deformation_time - O.dt*int(time_ratio) # Set the remaining deformation as time step

        self._run_dem_step()
        O.dt = self.dem_dt # Set back the DEM dt of the current MPM iteration

    def run_dem_steps_fdt(self, max_deps,dstrain_matrix):
        '''Executes the appropriate number of DEM iterations without touching on the DEM time step during this process'''
        n_dem_iter = int(np.ceil(max_deps/(self.dem_strain_rate*O.dt)))
        O.cell.velGrad = dstrain_matrix / (n_dem_iter*O.dt)
        for step in range(n_dem_iter): self._run_dem_step()

    def _run_dem_step(self):
        O.step()
        if self.flip_cell_period>0: 
                if O.iter % self.flip_cell_period == 0:
                    O.cell.flipCell()
                    self.flip_count += 1
    
    def _detect_gsts(self):
        '''Programmer function killing GlobalStiffnessTimeStepper if present and alive in O.engines'''
        for i, e in enumerate(O.engines):
            if type(e)==GlobalStiffnessTimeStepper: 
                self._gsts_ind = i
                if e.dead: return
                else: 
                    e.dead = True
                    warnings.warn("A `GlobalStiffnessTimeStepper` instance was found alive in the engine list, it has been killed. It will be called manually at the beginning of each MPM step.")
                    return
        if not self.fixed_dem_dt: warnings.warn("No instance of the `GlobalStiffnessTimeStepper` engine was found in the engine list but the parameter `fixed_dem_dt` is set to False. Please add an instance of `GlobalStiffnessTimeStepper` to `O.engines`.")
    
    def _set_demdt(self): 
        if not self.fixed_dem_dt: O.engines[self._gsts_ind]()

    def _save_vtk(self):
        O.engines[self._vtkRec_ind].dead = False
        tmp_engines = O.engines
        O.engines = [O.engines[self._vtkRec_ind]]
        O.step()
        O.engines = tmp_engines
        O.engines[self._vtkRec_ind].dead = True


def _get_bodies_walls():
    global bodies_id, walls_id
    bodies_id, walls_id = [], []
    for b in O.bodies:
        if type(b.shape) in [Facet, Box, Wall]: walls_id.append(b.id)
        else: bodies_id.append(b.id)


def write_rve_data(rve_info_file="rve_info.json", additional_data={}):
    """
    Write a json file which stores relevant RVE data. This function is meant to be called within YADE after generating an RVE, and the json file it creates is meant to be used within the preprocessing PyCBG script of a MPMxDEM simulation. It is assumed that the YADE simulation is periodic, and that all bodies are spheres made of the same material.

    Parameters
    ----------
    rve_info_file : str
        Path to the output json file. Default to "rve_info.json".
    additional_data : dict
        Dictionary containing additional parameters to be saved in the json file. Default is an empty dictionary.
    """
    yade = sys.modules["__main__"] # the __main__ module is YADE if this function is called from YADE
    stress = yade.getStress()
    sig_xx, sig_yy, sig_zz = stress[0,0], stress[1,1], stress[2,2]
    sig_xy, sig_yz, sig_xz = (stress[0,1]+stress[0,1])/2, (stress[1,2]+stress[2,1])/2, (stress[0,2]+stress[2,0])/2
    stress_formatted = [sig_xx, sig_yy, sig_zz, sig_xy, sig_yz, sig_xz]

    n = yade.porosity()
    e = n/(1-n)
    glob_density = sum([b.shape.radius**3*np.pi*4/3. for b in yade.O.bodies]) * yade.O.bodies[0].material.density / yade.O.cell.volume

    rve_infos = {"stress": stress_formatted, 
                 "porosity": n, 
                 "void_ratio": e, 
                 "global_density": glob_density}
    rve_infos.update(additional_data)
    
    with open(rve_info_file, "w") as fil: json.dump(rve_infos, fil)

def load_rve_data(rve_info_file="rve_info.json"):
    """
    Loads and returns the RVE json file saved with pycbg.MPMxDEM.write_rve_data, as a dictionary.  

    Parameters
    ----------
    rve_info_file : str
        Path to the output json file. Default to "rve_info.json".

    Returns
    -------
    dict
        Dictionary containing data from the json file.
    """

    with open(rve_info_file, "r") as fil: return json.load(fil)
