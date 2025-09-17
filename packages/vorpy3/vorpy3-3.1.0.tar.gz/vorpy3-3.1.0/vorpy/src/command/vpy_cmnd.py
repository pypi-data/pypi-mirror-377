import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
from vorpy.src.group import Group
from vorpy.src.command.set import sett
from vorpy.src.command.commands import *
from vorpy.src.command.group import group
from vorpy.src.command.export import export
from vorpy.src.command.interpret import get_ndx


def load_base_file(my_sys):
    """
    Loads a base molecular structure file into the system.

    This function handles the initial loading of a molecular structure file (.pdb, .gro, .mol, .cif) or
    a vertex/network file (.txt) into the system. It provides multiple ways to specify the file:
    - Direct file path input
    - File selection through a GUI file dialog
    - Default test files from the Data/test_data directory

    The function will continue prompting until a valid file is successfully loaded.

    Parameters:
    -----------
    my_sys : System
        The system object to load the file into

    Returns:
    --------
    None
    """
    # Keep asking for an atom file till one is loaded
    while True:
        # Set up the prompt
        usr_file = input("atom file >>>   ")
        # Check if the user entered load first
        usr_file = usr_file.split()
        if usr_file[0].lower() in browses:
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            usr_file = filedialog.askopenfilename(title='Select atom/ball file')

        elif len(usr_file) > 1:
            usr_file = usr_file[1]
        elif len(usr_file) == 1:
            usr_file = usr_file[0]
        else:
            my_num = np.random.randint(8)
            usr_file = ['Na5', 'EDTA_Mg', 'cambrin', 'hairpin', 'DB1976', 'Na7', 'protein_ligand_complex', 'Complex1_frame1'][my_num]
        # Check if the full path was loaded
        if os.path.exists(usr_file) and usr_file[-3:] in {"pdb", "gro", "mol", "cif", 'txt'}:
            file_path = usr_file
        # Check if the file was loaded without the directory
        elif os.path.exists("./Data/test_data/" + usr_file):
            file_path = os.getcwd() + "/Data/test_data/" + usr_file
        # Check if the path exists without the directory or the extension
        elif os.path.exists("./Data/test_data/" + usr_file + ".pdb"):
            file_path = os.getcwd() + "/Data/test_data/" + usr_file + ".pdb"
        # Else try again
        else:
            print("{} is not a valid input file".format(usr_file))
            continue
        # Create the system and return
        my_sys.load_sys(file=file_path)
        return


def load_another_file(my_sys):
    """
    Loads additional files into the system after the initial atom file has been loaded.

    This function provides an interactive interface for loading various types of files:
    - Network files (.csv) containing vorpy-generated network data
    - Voronota balls files (.txt) containing ball definitions
    - Voronota vertices files (.txt) containing vertex definitions
    - GROMACS index files (.ndx) containing atom group definitions

    The function:
    1. Prompts the user to select a file type
    2. Validates the selected file exists and has the correct extension
    3. Loads the file into the system if valid
    4. Provides appropriate error messages for invalid files

    Parameters:
    -----------
    my_sys : System
        The system object to load the additional file into

    Returns:
    --------
    bool
        True if file was successfully loaded, False otherwise
    """
    # Ask the usr what type of file they want to load
    file_type = input(
        "Enter file type: 1. Network (.csv)  2. Voronota Balls (.txt)  3. Voronota Vertices (.txt)  "
        "4. GROMACS index (.ndx)\nfile type (1-4) >>>   ")
    # If the input is a network file load it into the system
    if file_type.lower() in {"1", "1.", "one", "un", "uno", "1 "}:
        # Print the message that the network file type has been chosen
        print(
            "Network file type selected. Please enter a vorpy generated network file address "
            "(extension .csv) for \'{}\'".format(my_sys.name))
        # Ask the user to add the input file for the system name
        my_net_file = input("file address (.csv) >>>   ")
        # Check that the file is 181L
        if my_net_file[-3:] == 'csv' and os.path.exists(my_net_file):
            # Load the network file
            my_sys.load_net(my_net_file)
        else:
            print("Bad file")
            return False
    # If the input is to load a ball file
    elif file_type.lower() in {"2", "2.", "two", "to", "too", "dos", "du", "due"}:
        # Print the message that the voronota balls file type has been chosen
        print("Voronota balls file type selected. Please enter a Voronota generated balls full file address "
              "(extension .txt) for \'{}\'".format(my_sys.name))
        # Ask the user to add the input file for the system name
        my_ball_file = input("file address (.txt) >>>   ".format(my_sys.name))
        # Check that the file is 181L
        if my_ball_file[-3:] == 'txt' and os.path.exists(my_ball_file):
            # Load the network file
            my_sys.ball_file = my_ball_file
            print("Ball File Loaded")
        # Check if the ball file is in the current directory
        elif my_ball_file[-3:] == 'txt' and my_sys.vpy_dir is not None and os.path.exists(my_sys.vpy_dir + my_ball_file):
            # Load the network file
            my_sys.ball_file = my_sys.vpy_dir + my_ball_file
            print("Ball File Loaded")
        else:
            if os.path.exists(my_ball_file):
                print("Bad File: Wrong file type")
            else:
                print("File does not exist")
            return False
    # If the input is to load a ball file
    elif file_type.lower() in {"3", "3.", "three", "tre", "tres"}:
        # Print the message that the voronota balls file type has been chosen
        print("Voronota vertices file type selected. Please enter a Voronota generated vertices file address "
              "(extension .txt) for \'{}\'".format(my_sys.name))
        # Ask the user to add the input file for the system name
        my_vert_file = input("file address (.txt) >>>   ".format(my_sys.name))
        # Check that the file is 181L
        if my_vert_file[-3:] == 'txt' and os.path.exists(my_vert_file):
            # Load the network file
            my_sys.vert_file = my_vert_file
        else:
            print("Bad file")
            return False
    # If the input is to load a ball file
    elif file_type.lower() in {"4", "4.", "four", "quattro", "for", "4 "}:
        # Print the message that the voronota balls file type has been chosen
        print("GROMACS index file type selected. Please enter a GROMACS generated index file address "
              "(extension .ndx) for \'{}\'".format(my_sys.name))
        # Ask the user to add the input file for the system name
        my_ndx_file = input("file address (.ndx) >>>   ".format(my_sys.name))
        # Check that the file is 181L
        if my_ndx_file[-3:] == 'ndx' and os.path.exists(my_ndx_file):
            # Load the network file
            my_sys.load_ndx(file=my_ndx_file)
        else:
            print("Bad file")
            return False
    else:
        print("Bad Number")
        return False
    return True


def create_group(my_sys, usr_npt):
    """
    Creates a group object from the system based on user input specifications.

    This function handles group creation for different types of objects:
    - Full system ('f')
    - No solvent system ('ns')
    - Molecule groups
    - Residue groups
    - Atom groups
    - Index groups

    The function processes user input to determine:
    1. The type of object to group (molecules, residues, atoms, or indices)
    2. The specific indices or ranges to include in the group
    3. The appropriate name for the group

    Parameters:
    -----------
    my_sys : System
        The system object containing the data to group
    usr_npt : list
        List of user input parameters specifying the group type and indices

    Returns:
    --------
    Group or None
        Returns a Group object if successful, None if group creation fails
    """
    # Check for basic inputs
    if usr_npt[0].lower() == 'f':
        return Group(sys=my_sys, atoms=my_sys.atoms, name="{}_full".format(my_sys.name))
    # Check for no sol
    elif usr_npt[0].lower() == 'ns':
        return Group(sys=my_sys, chains=my_sys.chains, name=my_sys.name)

    # Create the object and index variables
    my_obj, my_ndx = None, None
    # User only input "export"
    if len(usr_npt) == 0:
        # Tell the user to pick an object and an index
        my_obj = get_obj(sys=my_sys)
        my_ndx = get_ndx(sys=my_sys, obj=my_obj)
    # User entered "export obj" and needs an index
    elif len(usr_npt) == 1:
        # Add a check for system
        # Check the object provided by the user
        my_obj = get_obj(sys=my_sys, obj=usr_npt[0])
        my_ndx = get_ndx(sys=my_sys, obj=my_obj)
    # If the user input an object and an index of their own
    elif len(usr_npt) >= 2:
        # Check the object
        my_obj = get_obj(sys=my_sys, obj=usr_npt[0])
        my_ndx = get_ndx(sys=my_sys, obj=my_obj, ndx_npt=usr_npt[1])
    # Get the group information
    obj_ndx = ['m', 'r', 'a', 'n'].index(my_obj)
    obj_list = [my_sys.chains, my_sys.residues, my_sys.atoms, my_sys.ndxs][obj_ndx]
    name_prfx = ['mol', 'resid', 'atom', 'ndx'][obj_ndx]
    my_list, name = None, None
    # Get the slice and name of the group
    if my_ndx is None:
        return
    elif len(my_ndx) == 1:
        if obj_ndx == 2:
            my_list = [my_ndx[0]]
        else:
            my_list = [obj_list[my_ndx[0]]]
        name = name_prfx + '_' + str(my_ndx[0])
    elif len(my_ndx) <= 2:
        if obj_ndx == 2:
            my_list = [_ for _ in range(max(0, my_ndx[0]), min(len(obj_list), my_ndx[1] + 1))]
        else:
            my_list = obj_list[max(0, my_ndx[0]):min(len(obj_list), my_ndx[1] + 1)]
        name = name_prfx + 's_' + str(my_ndx[0]) + '_' + str(my_ndx[1])
    # Create the group
    npt_list = [None] * 4
    npt_list[obj_ndx] = my_list
    return Group(sys=my_sys, chains=npt_list[0], residues=npt_list[1], atoms=npt_list[2])


def vorpy(my_sys):
    """
    Main interactive function that orchestrates the vorpy molecular analysis workflow.

    This function serves as the primary interface for the vorpy program, handling:
    1. Initial system setup and file loading
    2. Interactive group creation and management
    3. Network building and analysis
    4. System visualization and export

    The workflow proceeds as follows:
    1. Initial Setup:
       - Loads a base molecular structure file (PDB, GRO, MOL, CIF)
       - Optionally loads additional files (network, vertices, balls, index)
       - Displays system statistics (atoms, residues, chains)

    2. Group Management:
       - Creates default group excluding solvent
       - Allows creation of custom groups based on:
         * Molecules (m)
         * Residues (r)
         * Atoms (a)
         * Index groups (n)
       - Supports range-based selections (e.g., "r 1-10")

    3. Network Analysis:
       - Configures network parameters if not pre-loaded
       - Builds Voronoi/Delaunay networks
       - Manages surface generation

    Examples:
    --------
    Basic Usage:
    >>> vorpy()
    Welcome to vorpy. For assistance type 'h'. To quit type 'q'
    atom file >>> protein.pdb
    add files >>> n
    Default group (No Sol): 1000 atoms, 50 residues, 1 chain
    new group >>> r 1-10
    residues_1_10 group created - 200 atoms, 10 residues, 1 chain

    Returns:
    -------
    None
    """
    print("Welcome to vorpy. For assistance type \'h\'. To quit type \'q\'")
    # Load the initial input file
    load_base_file(my_sys)
    # Allow the user to keep loading files
    while True:
        # Ask the user if they have another file to load
        load_another = input("add files >>>   ")
        # Check if load another is requested
        if load_another.lower() in ns + dones + ['']:
            break
        # Give the user the interface to load files
        good_file = load_another_file(my_sys=my_sys)
        if good_file:
            continue
    # Get the number of atoms in the default grouping (if sol dne all atoms)
    atom_len = len(my_sys.balls) - len(my_sys.sol.atoms) if my_sys.sol is not None else len(my_sys.atoms)
    # Print the default grouping information for the system
    print("Default group (No Sol): {} atoms, {} residue{}, {} chain{}".format(atom_len, len(my_sys.residues), 's' if len(my_sys.residues) > 1 else '', len(my_sys.chains), 's' if (len(my_sys.chains) > 1) else ''))
    # Start the grouping loop
    while True:
        # Get an initial grouping input
        usr_npt = input("new group >>>   ")
        # Split the user input
        usr_npt = usr_npt.split()
        # Check that the user's input is valid
        if len(usr_npt) == 0 or usr_npt[0].lower() in my_objects:
            break
        elif usr_npt[0].lower() in show_cmds:
            show(my_sys, usr_npt)
            continue
        # Tell the user they f'd up
        print("Bad input")
    if len(usr_npt) == 0 or usr_npt[0] in ns:
        my_group = Group(sys=my_sys, residues=my_sys.residues, name=my_sys.name)
    else:
        # Create the group
        my_group = create_group(my_sys=my_sys, usr_npt=usr_npt)
        if my_group is not None:
            print("{} group created - {} atoms, {} residues, {} chains".format(my_group.name, len(my_group.atms),
                                                                               len(my_group.rsds), len(my_group.chns)))
    # Add the group to the system
    my_sys.groups = [my_group]
    # Check if the network has been loaded
    if my_sys.files['net_file'] is None and my_sys.files['verts_file'] is None:
        net = my_sys.groups[0].net
        # Keep asking for a setting to change
        while True:
            # Print the default settings
            print(u"\nDefault settings: net type = {}, surf res = {:.2f} \u208B,  max vert  = {:.2f} \u208B,  "
                  u"box multiplier = {:.2f} x".format(my_group.net.settings['net_type'], net.settings['surf_res'],
                                                      net.settings['max_vert'], net.settings['box_size']))
            # Print the build settings and see if the user wants to change anything
            change_settings = input("alter settings >>>   ")
            change_settings = change_settings.split()
            # If the user wants to change the settings:
            if len(change_settings) == 0:
                break
            elif change_settings[0].lower() in ys:
                sett(my_sys, ["set"], vorpy2_set=True)
            # If the user changes the settings here, insert the inp-ut into the sett function
            elif change_settings[0].lower() in settings_dict:
                sett(my_sys, change_settings, vorpy2_set=True)
            # If the user input is not a good one let them go again
            elif change_settings[0].lower() in ns + [""] + dones:
                break
        # Build the group
        my_group.net.build(my_group=my_group, print_actions=True)
    # Check if both Voronota files have been loaded
    elif my_sys.ball_file is not None and my_sys.vert_file is not None:
        my_sys.load_verts(file=my_sys.vert_file, vta_ball_file=my_sys.ball_file)
        my_sys.net.build(calc_verts=False, my_group=my_group)

    # Export basic system elements
    my_sys.exports(pdb=True, set_atoms=True, network=True, logs=True)

    # Export
    export(my_sys, usr_npt="e", my_group=my_group)

    # Exporting process
    while True:
        # Check if the user wants to export files
        export_files = input("export more files for {}? (y/n) >>>   ".format(my_group.name))
        # If the user wants to export files for the given group start the export process for the current group
        if export_files.lower() in ys:
            # Export
            export(my_sys, usr_npt="e", my_group=my_group)
        elif export_files.lower() in ns + quits:
            # Ask if the user wants to export another group
            export_another_group = input("export another group for {}? (y/n) >>>   ".format(my_sys.name))
            export_another_group = export_another_group.split()
            my_new_group = None
            if export_another_group[0] in ys:
                my_new_group = group(my_sys, [])
            elif export_another_group[0] in my_objects:
                my_new_group = group(my_sys, usr_npt)
            elif export_another_group in ns + quits:
                return
            my_group = my_new_group
            my_sys.net.build(my_group=my_group, print_actions=True)


def pre_run_display(sys_name=None, sys_file=None, sys_num_balls=None, sys_type=None, grp_name=None, grp_num_balls=None,
                    grp_vol=None, grp_sa=None, set_net_type=None, set_surf_res=None, set_max_vert=None,
                    net_num_verts=None, net_num_surfs=None, net_num_edges=None, out_type=None, out_descr=None,
                    other_file1=None, other_file1_type=None, other_file2=None, other_file2_type=None, other_file3=None,
                    other_file3_type=None):
    if out_descr is None:
        out_descr = ""
    out_descr1 = ""
    if len(out_descr) > 15:
        out_descr1 = out_descr[15:min(len(out_descr), 30)]
        out_descr = out_descr[:15]
    var_list = []
    for _ in [sys_name, grp_name, set_net_type, sys_file, grp_num_balls, set_surf_res, sys_num_balls, grp_vol,
              set_max_vert, sys_type, net_num_verts, grp_sa, out_type, other_file1, other_file1_type, net_num_surfs,
              out_descr, other_file2, other_file2_type, net_num_edges, out_descr1, other_file3, other_file3_type]:
        if _ is None:
            var_list.append("")
        else:
            var_list.append(_)

    print(" _______________________________________________________________________________________________________\n"
          "|                                              VORPY                                                    |\n"
          "|            - System -             |            - Group -           |          - Settings -            |\n"
          "|  Name:       {:>20s} |  Name:         {:>15s} |  Network Type:    {:9s} (nt) |\n"
          "|  File:       {:.20s} |  # Balls:      {:>15s} |  Surf Resolution: {:9s} (sr) |\n"
          "|  # Balls:    {:>20s} |  Volume:       {:>15s} |  Max Vertex:      {:9s} (mv) |\n"
          "|  Type:       {:>20s} |  Surface Area: {:>15s} |                                  |\n"
          "|___________________________________|________________________________|__________________________________|\n"
          "|     - Network -     |             - Output -             |               - Other Files -               |\n"
          "|  # Verts: {:9s} |   Type:      {:21s} |   1. {:24s}, {:11s} |\n"
          "|  # Surfs: {:9s} |   Contents:  {:21s} |   2. {:24s}, {:11s} |\n"
          "|  # Edges: {:9s} |                                    |   3. {:24s}, {:11s} |\n"
          "|_____________________|____________________________________|____________________________________________|"
          .format(*var_list))

# pre_run_display(sys_name='EDTA_Mg', sys_file='C:/files/jacke/EDTA_Mg.pdb', sys_num_balls='90,000', sys_type='PDB', grp_name="Molecule 1", grp_num_balls="4269", grp_vol='40 A', grp_sa='155 A', set_net_type='Voronoi', set_surf_res='0.2 A', set_max_vert='10 A')
