import sys, warnings, textwrap, operator, re
from collections import namedtuple, OrderedDict
from . import _version

try:
    # Python 3.8+
    from importlib.metadata import distribution, PackageNotFoundError
except ImportError:
    # for Python <3.8, need backport: pip install importlib_metadata
    from importlib_metadata import distribution, PackageNotFoundError

__version__ = _version.get_versions()['version']
__commit_sha__ = _version.get_versions()['full-revisionid']

# Exceptions and warnings definition
class NewFeatureWarning(Warning):
    """Used when a new feature handles what the user wanted to do, but the way the user did it is still supported (Similar to DeprecationWarning, but specific to PyCBG). Not displayed by default, use `warnings.simplefilter("default", pycbg.NewFeatureWarning)` to activate it.
    """
    def __new__(cls, *args, **kwargs):
        if not warnings.warn_explicit:
            return None
        return super().__new__(cls)
    
class VersionWarning(Warning):
    """Used for versions check related issues.
    """
    def __new__(cls, *args, **kwargs):
        if not warnings.warn_explicit:
            return None
        return super().__new__(cls)

class VersionError(Exception): 
    """Raised when a fatal issue occurs during versions check.
    """
    pass

    ## Because of the following line, the user has to use e.g. `warnings.simplefilter("default", pycbg.NewFeatureWarning)` to display NewFeatureWarning warnings
warnings.simplefilter("ignore", NewFeatureWarning)

# Versions check and utility

    ## Create a useful class to compare versions
        ### Define a namedtuple with fields relevant for version tracking
VersionInfo = namedtuple('VersionInfo', [
    'major', 'minor', 'micro', 
    'requirement_major', 'requirement_minor', 'requirement_micro', 
    'requirement_type'
])

    ## Define rich comparison operators as a dictionary, for convenience
rich_comparison_ops = OrderedDict() # the keys method should return the single character operators last
rich_comparison_ops["=="] = operator.eq
rich_comparison_ops["<="] = operator.le
rich_comparison_ops[">="] = operator.ge
rich_comparison_ops["<"] = operator.lt
rich_comparison_ops[">"] = operator.gt

        ### Define the useful class
str_version_format = "'major.minor[.micro] [COMP_OPERATOR req_major.req_minor[.req_micro]]' (space-insensitive)"
class Version(VersionInfo):
    """
    Represents a version with optional compatibility requirement. Supports comparison with other instances of this class and with strings (given that their format comply with the one required by the `Version.from_string` method). Inherits from the `collections.namedtuple` class and is thus iterable.

    Parameters
    ----------
    major : int 
    The major version number.
    minor : int
        The minor version number.
    micro : int or None
        The micro version number.
    requirement_major : int or None 
        Required major version for compatibility check.
    requirement_minor : int or None
        Required minor version for compatibility check.
    requirement_micro : int or None
        Required micro version for compatibility check.
    requirement_type : str among {'<', '>', '==', '<=', '>='} or None
        Type of requirement.
    version_condition : Version or None 
        Version object representing the compatibility requirement.
    """
    def __new__(cls, major, minor, micro=None, 
                requirement_major=None, requirement_minor=None, requirement_micro=None, 
                requirement_type=None):
        # Ensure first six parameters are integers
        for param_name in ['major', 'minor', 'micro', 'requirement_major', 'requirement_minor', 'requirement_micro']:
            param_value = locals()[param_name]
            if param_value is not None and not isinstance(param_value, int):
                raise TypeError(f"{param_name} must be an integer")
        
        # Ensure requirement_type is valid if provided
        if requirement_type and requirement_type not in rich_comparison_ops.keys():
            raise ValueError(f"Invalid requirement_type. Must be one of '<', '>', '==', '<=', '>=', you've passed {requirement_type}.")
        
        self = super(Version, cls).__new__(cls, major, minor, micro, 
                                           requirement_major, requirement_minor, requirement_micro,
                                           requirement_type)
        
        self.version_condition = Version(requirement_major, requirement_minor, requirement_micro) if requirement_major is not None else None
        
        return self
    
    @classmethod
    def from_string(cls, version_str):
        """Construct the `Version` object from a string (alternative to the default constructor)

        Parameters
        ----------
        version_str : str
            String to use for generating the `Version` object. Should have the format 'major.minor[.micro] [COMP_OPERATOR req_major.req_minor[.req_micro]]' (space-insensitive) 

        Raises
        ------
        VersionError
            When the format of the input string is not recognized.

        Returns
        -------
        Version
            The `Version` object constructed from the input string.

        """
        version_str = version_str.replace(" ", "") # strip all spaces
        
        comp_str, req_str, ver_str = "", "", version_str
        for comp_op in rich_comparison_ops.keys():
            if comp_op in version_str: # single character operators are at the end of the rich_comparison_ops dict
                ver_str, req_str = version_str.split(comp_op)
                comp_str = comp_op
                break
        
        v_str_full = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$") # matches e.g. 4.2.3, 4.12.3, etc
        v_str_short = re.compile(r"^[0-9]+\.[0-9]+$") # matches e.g. 4.2, 4.12, etc
        
        version_list = []
        for test_str in [ver_str, req_str]:
            if not test_str: continue
            match_full = v_str_full.match(test_str) is not None
            match_short = v_str_short.match(test_str) is not None
        
            if match_full or match_short: version_list += [int(i) for i in test_str.split(".")]
            else:
                raise VersionError(f"The string {version_str} doesn't have the expected format {str_version_format}.")
            if match_short: version_list.append(None)        
    
        if comp_str: version_list.append(comp_str)
        return cls(*version_list)
    
    def __format__(self, format_spec):
        out_str = f"{self.major}.{self.minor}"
        if format_spec == "short": return out_str
        if self.micro is not None: out_str = f"{out_str}.{self.micro}"
        
        requirement_part = ""
        if format_spec == "full":
            if self.requirement_type is not None:
                micro_extension = f".{self.requirement_micro}" if self.requirement_micro is not None else ""
                requirement_part = f" ({self.requirement_type} {self.requirement_major}.{self.requirement_minor}{micro_extension}, {self.is_compatible(True)})"
            out_str = f"{out_str}{requirement_part}"
        return out_str
    
    def __str__(self): return self.__format__("")

    def __repr__(self): return self.__format__("full")
    
    def __eq__(self, other):
        if isinstance(other, Version): return self[:3] == other[:3]
        elif isinstance(other, str): return self.__eq__(self.from_string(other))
        return NotImplemented
    
    def __lt__(self, other):
        if isinstance(other, Version): return self[:3] < other[:3]
        elif isinstance(other, str): return self.__lt__(self.from_string(other))
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, Version): return self[:3] <= other[:3]
        elif isinstance(other, str): return self.__le__(self.from_string(other))
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Version): return self[:3] > other[:3]
        elif isinstance(other, str): return self.__gt__(self.from_string(other))
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, Version): return self[:3] >= other[:3]
        elif isinstance(other, str): return self.__ge__(self.from_string(other))
        return NotImplemented
    
    def __ne__(self, other): return not self.__eq__(other)
    
    def __add__(self, other, reverse=False):
        if isinstance(other, str): transform = lambda s: s
        elif isinstance(other, Version): transform = lambda s: str(s)
        elif other is None: transform = lambda s: ""
        else: return NotImplemented
        
        terms = [str(self), transform(other)]
        if reverse: terms = terms[::-1]
        return terms[0] + terms[1]
    
    def __radd__(self, other): return self.__add__(other, True)
        
    def is_compatible(self, return_str=False):
        """Checks if this version meets its compatibility requirement.

        Parameters
        ----------
        return_str : (bool, optional) 
            Whether to return a string containing 'OK' if True or 'NOT COMPATIBLE' if False. Defaults to False.

        Returns
        -------
        bool or str
             True (or 'OK') if the version meets the compatibility requirement; False (or 'NOT COMPATIBLE') otherwise.
        """
        if self.requirement_type is None:
            compatible = True  # No requirement specified, always compatible
        else: compatible = rich_comparison_ops[self.requirement_type](self, self.version_condition)
        if not return_str: return compatible
        else: return "OK" if compatible else "NOT COMPATIBLE"

    ## Check if the python version is high enough to check the version of all modules (i.e. if importlib.metadata.get_version is available)
can_check_versions = sys.version_info[0]>=3 and sys.version_info[1]>=8

#: Dictionary containing the `pycbg.Version` objects associated to each module as keys (strings). 
versions = {"python": Version(*sys.version_info[:3])}

if can_check_versions: # if Python >=3.8
    from importlib.metadata import version as get_version
else: warnings.warn(f"The 'printAllVersions' function will not display version numbers because it requires at least Python 3.8 (detected version {versions['python']:short})", VersionWarning)

    ## Get the list of dependencies, as passed to `install_requires` in `setup.py`
try:
    dist = distribution("pycbg")
    requires = dist.requires or []
except PackageNotFoundError:
    warnings.warn("The module package was not found by importlib.metadata.distribution, list of dependencies will be empty", VersionWarning)
    requires = []
dependencies_str = [str(req) for req in requires if "extra ==" not in req] # filter out optional dependencies

    ## Put them all in a dictionary, with a corresponding Version object
for dep in dependencies_str:
    module_name, requirement = dep, []
        ### Check if a condition was defined
    comp_str, req_str = "", ""
    for comp_op in rich_comparison_ops.keys():
        if comp_op in dep: # single character operators are at the end of the rich_comparison_ops dict
            module_name, req_str = dep.split(comp_op)
            comp_str = comp_op
            break
        
        ### Create the Version object
    if can_check_versions:
        dep_version = get_version(module_name)
        try: versions[module_name] = Version.from_string(dep_version + comp_str + req_str)
        except VersionError:
            warnings.warn(f"The version of {module_name} will not be available because it doesn't have the expected format major.minor[.micro] (got {dep_version}).", VersionWarning)
            requirement = [int(i) for i in req_str.split(".")] + [comp_str] if req_str else []
            versions[module_name] = Version(*[-1]*3, *requirement)
    else: versions[module_name] = Version(*[-2]*3, *requirement)


    ## Define the function that prints all dependencies and their version
dep_versions = [key for key in versions.keys() if key not in ["python", "pycbg"]]
def printAllVersions(return_str=False, tab_width=4, spacing=2):
    """
    Prints the versions of all dependencies, and their requirement. Note that this data is also available in a dictionary `pycbg.versions` populated with instances of `Version` object (e.g. `pycbg.versions['numpy'] >= '1.25.0'`, `pycbg.versions['pandas'].is_compatible()`, `pycbg.versions['gmsh'] == pycbg.Version(4, 12, 0)`, `pycbg.versions['sphinx'] < pycbg.Version.from_string('5.5.2')`).
    
    Parameters
    ----------
    return_str : bool
        Set to True to return the string containing the versions instead of printing it
    tab_width : int
        Number of space characters to indent lines when listing dependencies
    spacing : int
        Number of space characters between columns (1,2) and (2,3) 
        
    Returns
    -------
    str or None
        The string containing all version information, if `return_str` was set to True
    """
    c1w = len(max(dep_versions, key=len)) + tab_width + 1 + spacing # first column width, accounting for dependencies indent, the column character and the space before version string
    
    col2_strings = list(versions.values()) + [__version__, "Version"]
    c2w = len(max(col2_strings, key=len)) + spacing # second column width, accounting for space before the requirement string
    
    col3_strings = []
    for key in dep_versions:
        cond_version = versions[key].version_condition
        if cond_version is None: condition_str = ""
        else: condition_str = f"{versions[key].requirement_type} {cond_version} ({versions[key].is_compatible(True)})"
        col3_strings.append(condition_str)
    c3w = len(max(col3_strings+["Requirement"], key=len)) # third column width
    
    max_line_width = c1w + c2w + c3w
    line_separator = "_"*max_line_width
    
    versions_str = textwrap.dedent(f"""
    {line_separator}
    {"Component":<{c1w}}{"Version":<{c2w}}{"Requirement":>{c3w}}
    {line_separator}
    {"python:":<{c1w}}{str(versions["python"]):<{c2w}}
    {"pycbg:":<{c1w}}{__version__:<{c2w}}
    
    Dependencies:
    """)
    
    for i_dp, dp in enumerate(dep_versions):
        name_str = dp + ":"
        versions_str += f"{' '*tab_width}{name_str:<{c1w-tab_width}}{str(versions[dp]):<{c2w}}{col3_strings[i_dp]:>{c3w}}\n"
    versions_str += line_separator
    
    if return_str: return versions_str
    print(versions_str)