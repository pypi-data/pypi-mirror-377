import os
from os import path
import tkinter as tk
from tkinter import filedialog
from vorpy.src.command.commands import *
from vorpy.src.chemistry import element_names, element_radii


def get_ndx(sys, obj, ndx_npt=None):
    """
    Retrieves and validates indices for specified molecular objects from the system.

    This function handles user input for selecting indices of molecules, residues, atoms, or custom indices.
    It validates the input against the available objects in the system and returns a list of valid indices.

    Parameters:
    -----------
    sys : System
        The system containing the molecular data
    obj : str
        The type of object to get indices for ('m' for molecule, 'r' for residue, 'a' for atom, 'n' for index)
    ndx_npt : str, optional
        Pre-specified index input. If None, user will be prompted for input.

    Returns:
    --------
    list of int
        List of valid indices for the specified object type
    None
        If user quits or input is invalid
    """
    # Create the naming dictionary
    name_dict = {'m': 'Molecule', 'r': 'Residue', 'a': 'Atom', 'n': 'Index'}
    # Get the name
    name = name_dict[obj]
    # Get the list
    obj_list = []
    if obj == 'm':
        obj_list, obj_num = sys.chains, 0
    elif obj == 'r':
        obj_list, obj_num = sys.residues, 1
    elif obj == 'a':
        obj_list, obj_num = sys.balls, 2
    elif obj == 'n':
        obj_list, obj_num = sys.ndxs, 3
    # Start the ndx checking loop
    while True:
        # Get the index if the index doesn't exist
        if ndx_npt is None:
            ndx_npt = input("enter a {} index (range: 0 - {})\nindex >>>   ".format(name, len(obj_list) - 1))
        # Check for quits
        if ndx_npt.lower() in quits:
            return
        # Check for helps
        elif ndx_npt.lower in helps:
            print_help()
            continue
        # Check the input
        ndx_npt = ndx_npt.split("-")
        # Get the list of index numbers
        try:
            return [int(_) for _ in ndx_npt]
        except ValueError:
            continue


def get_obj(sys, obj=None):
    """
    Prompts the user to select a molecular object type and returns a corresponding identifier.

    This function handles user input for selecting between different types of molecular objects:
    - Molecules (chains)
    - Residues
    - Atoms
    - Indices

    The function validates user input against predefined object type commands and returns
    a single character identifier ('m', 'r', 'a', or 'n') corresponding to the selected type.

    Parameters:
    -----------
    sys : System
        The system containing molecular data
    obj : str, optional
        Pre-specified object type input. If None, user will be prompted for input.

    Returns:
    --------
    str
        Single character identifier for the object type:
        - 'm' for molecule/chain
        - 'r' for residue
        - 'a' for atom
        - 'n' for index
    None
        If user quits or input is invalid
    """
    # Keep asking the user to choose an object to export
    while True:
        # If no input was given
        if obj is None:
            # Prompt the user
            obj = input("enter an object type. (\'mol\', \'res\', \'atom\', or \'ndx\')\nobject >>>   ")
            obj = obj.split()
        # Check to see if the user gave a valid response or not
        if obj[0].lower() in quits:
            return
        elif obj[0].lower() in helps:
            print_help()
        elif obj[0].lower() not in my_objects:
            # Tell the user they suck and try again
            invalid_input(obj)
            obj = None
            continue
        # Otherwise, we have a success
        elif obj[0].lower() in chn_objs:
            return 'm'
        elif obj[0].lower() in res_objs:
            return 'r'
        elif obj[0].lower() in atom_objs:
            return 'a'
        elif obj[0].lower() in ndx_objs:
            return 'n'


def get_file(file=None):
    """
    Prompts the user to select a file or validates a provided file path.

    This function handles file selection through multiple methods:
    1. Direct file path input
    2. Relative path resolution from the vorpy directory
    3. Automatic path resolution for files in the test_data directory
    4. File browser dialog for interactive selection

    The function supports various file formats including:
    - .pdb
    - .mol
    - .cif
    - .gro

    Parameters:
    -----------
    file : str, optional
        Pre-specified file path. If None, user will be prompted for input.

    Returns:
    --------
    str
        Validated and resolved file path
    None
        If user quits or no valid file is found

    Notes:
    ------
    - Supports relative paths using './' notation
    - Automatically checks test_data directory for files
    - Launches file browser for interactive selection
    - Validates file existence and format
    """
    # Check if there is a file provided
    if file is None:
        print("enter a file address. (Use \'./\' to load a file from the \'.../vorpy\' directory):")
    # Check the file
    while True:
        # Get the file if None was specified
        if file is None:
            file = input("file >>>   ")
            if file.lower() in quits:
                return
            elif len(file) == 0:
                continue
            elif file.lower() in helps:
                print_help()
            test_file = file.split()
            if test_file[0] in load_cmds:
                file = file[len(test_file[0]) + 1:]
        # Check if the initial file works
        if path.exists(file) and len(file) > 0:
            break
        # Check if the file is in the ./Data/test_data folder
        elif path.exists("./vorpy/data/" + file) and len(file) > 0:
            file = os.getcwd() + "/vorpy/data/" + file
            break
        # Check if it is just the raw name
        elif path.exists("./vorpy/data/" + file + ".pdb") and len(file) > 0:
            file = os.getcwd() + "/vorpy/data/" + file + ".pdb"
            break
        # If the file is called as a browse keyword, launch a file browser
        elif file.lower() in browse_names:
            # Get the base file
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            file = filedialog.askopenfilename(title='Choose Ball File')
            if file[:-3] in {'pdb', 'mol', 'cif', 'gro'} and path.exists(file):
                break
        # Otherwise, tell the user to try again
        else:
            invalid_input(file)
            file = None
            continue
    # Return the file
    return file


def get_set(usr_npt=None):
    """
    Prompts the user to input a valid setting parameter and returns its standardized form.

    This function handles user input for various surface and network settings, converting
    different variations of setting names into their canonical forms. It supports settings
    for surface resolution, colors, schemes, maximum vertices, box sizes, network types,
    and atom radii.

    Returns:
    --------
    str
        The standardized setting code:
        - 'sr' for surface resolution
        - 'sc' for surface colors
        - 'ss' for surface schemes
        - 'mv' for maximum vertices
        - 'bm' for box size
        - 'nt' for network type
        - 'ar' for atom radii
    """
    # Keep asking the user to choose an object to export
    while True:
        # Check if we need to start from scratch
        if usr_npt is None:
            # Prompt the user
            usr_npt = input("setting >>>   ")
        # If they quit, then quit
        if usr_npt.lower() in quits:
            return
        elif usr_npt.lower() in helps:
            print_help()
        # Check to see if the user gave a valid response or not
        if usr_npt.lower() in surf_reses:
            # Return the base setting
            return 'sr'
        elif usr_npt.lower() in surf_colors:
            # Return the base setting
            return 'sc'
        elif usr_npt.lower() in surf_schemes:
            # Return the base setting
            return 'ss'
        elif usr_npt.lower() in max_verts:
            # Return the base setting
            return 'mv'
        elif usr_npt.lower() in box_sizes:
            # Return the base setting
            return 'bm'
        elif usr_npt.lower() in net_types:
            # Return the base setting
            return 'nt'
        elif usr_npt.lower() in atom_radii:
            # Return the base setting
            return 'ar'
        else:
            # Tell the user they suck and try again
            print("\"{}\" is not a valid input. Enter a 181L value (\'surf_res\', \'max_vert\', \'box_size\', or "
                  "\'calc_surfs\')".format(usr_npt))
            usr_npt = None


def get_val(setting=None, val=None):
    """
    Processes and validates user input values for system settings.

    This function handles the validation and processing of user-provided values for various system settings.
    It supports different types of settings including:
    - Atom radii (with element-specific radius customization)
    - Network types (Voronoi, Delaunay, Power, or Comparison)
    - Boolean values (converted to appropriate network types)

    Parameters:
    -----------
    setting : str, optional
        The setting type to validate (e.g., 'ar' for atom radii, 'nt' for network type)
    val : str or list, optional
        The user-provided value to validate and process

    Returns:
    --------
    None or processed value
        Returns None if user quits or the processed value if validation is successful
    """
    # If the setting is not in the settingsd
    if setting is None or setting.lower() not in settings_dict:
        setting = get_set()
    # Find the value for the setting
    while True:
        # If no val has been provided
        val1 = None
        if val is None:
            prompt_str = "Enter {} value \nvalue >>>   ".format(settings_dict[setting])
            val = input(prompt_str)
        if type(val) == list:
            if len(val) == 2:
                val, val1 = val
            else:
                val = val[0]
        # Quit if asked
        if val.lower() in quits or val.lower() in dones:
            return
        # Test the validity of the user's true and false skills
        if setting in atom_radii:
            if element_names[val.lower()] not in element_radii:
                val = None
            else:
                try:
                    val1 = float(val1)
                except IndexError:
                    val.append(None)
                    while True:
                        val1 = input("enter new radius for {} (current radius = {})".format(val[0].upper(),
                                                                                            element_radii[element_names[val[0].lower()]]))
                        try:
                            val1 = float(val1)
                            break
                        except ValueError:
                            val = None
                except ValueError:
                    val = None
            val = [val, val1]
        elif type(val) == str and setting in net_types:
            if val.lower() in trues + ys:
                val = 'del'
            elif val.lower() in falses + ns:
                val = 'vor'
            elif val.lower() in voronoi_vals:
                val = 'vor'
            elif val.lower() in delaunay_vals:
                val = 'del'
            elif val.lower() in power_vals:
                val = 'pow'
            elif val.lower() in compare_vals:
                val = 'com'
        # Test for a float value
        elif type(val) == str and setting in surf_reses + max_verts + box_sizes:
            try:
                val = float(val)
            except ValueError:
                val = None
        elif type(val) == str and setting in surf_colors:
            if val not in ["viridis", "plasma", "inferno", "cividis", "Greys", "Reds", "Greens", "Blues", 'rainbow', 'Purples_r']:
                val = None
        elif type(val) == str and setting in surf_schemes:
            if val not in ['dist', 'ins_out', 'curv']:
                val = None
        # Check if we cool
        if val is not None:
            break
    return val
