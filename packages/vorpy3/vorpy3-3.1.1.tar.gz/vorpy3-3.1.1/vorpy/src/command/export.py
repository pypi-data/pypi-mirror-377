from vorpy.src.command.commands import *
from vorpy.src.command.group import group


def change_surf_setting(my_group):
    """
    Allows interactive modification of surface visualization settings for a group.

    This function provides an interactive interface to modify:
    1. Surface coloring scheme (distance from center, inside/outside, curvature)
    2. Color map selection (viridis, plasma, inferno, etc.)
    3. Surface resolution

    Parameters:
    -----------
    my_group : Group
        The group object whose surface settings will be modified

    Returns:
    --------
    None
    """
    while True:
        # Print the main prompt
        print("{} Surface Settings: 1. Color Scheme = {} 2. Color Map = {} 3. resolution = {} (type \'q\' to quit)"
              .format(my_group.name, my_group.surf_scheme, my_group.surf_color, my_group.surf_res))
        # Input
        surf_set_npt = input("Surface setting (1-3) >>>   ")
        surf_set_npt.strip()
        if surf_set_npt in quits:
            break
        if surf_set_npt.lower() in ['1', '1.', 'one', 'scheme', 'sc']:
            # Print the coloring schemes
            print("Surface Coloring Schemes: 1. Distance from center of surface 2. Inside vs Outside 3. Curvature")
            my_scheme_npt = input("coloring scheme (1-3) >>>   ")
            my_scheme_npt.strip()
            if my_scheme_npt.lower() in ['1', '1.', 'one']:
                my_group.surf_scheme = 'dist'
                print("Coloring scheme changed to Distance from center of surface")
            if my_scheme_npt.lower() in ['2', '2.', 'two']:
                my_group.surf_scheme = 'ins_out'
                print("Coloring scheme changed to Inside vs Outside")
            if my_scheme_npt.lower() in ['3', '3.', 'three']:
                my_group.surf_scheme = 'curv'
                print("Coloring scheme changed to curvature")
        if surf_set_npt.lower() in ['2', '2.', 'two', 'map', 'cm']:
            print("Surface Color Maps: 1. viridis 2. plasma 3. inferno 4. cividis 5. Greys 6. Reds 7. Greens 8. Blues")
            my_color_npt = input("color map (1-8) >>>   ")
            my_color_npt.strip()
            if my_color_npt.isdigit() and 1 <= int(my_color_npt) <= 8:
                my_colors = ["viridis", "plasma", "inferno", "cividis", "Greys", "Reds", "Greens", "Blues"]
                my_group.surf_color = my_colors[int(my_color_npt) - 1]
        if surf_set_npt.lower() in ['3', '3.', 'three', 'surfs', 'surfaces']:
            print("Surface Resolution - Current Resolution = {}".format(my_group.surf_res))
            change_npt = input("change resolution >>>   ")
            if change_npt.isdecimal():
                my_group.surf_res = float(change_npt)
            elif change_npt.lower() in ys:
                resolution = input("resolution >>>   ")
                resolution.strip()
                if resolution.isdigit():
                    my_group.surf_res = float(resolution)
        if surf_set_npt.lower() in quits:
            break


def export_surfs(my_group):
    """
    Exports surfaces from a group based on user specifications.

    This function provides an interactive interface for exporting different types of surfaces from a group:
    - Shell surfaces
    - Filled body surfaces
    - Separate surfaces
    - All surface types

    For each export type, the user can:
    1. Configure surface settings including:
       - Color scheme (distance from center, inside/outside, curvature)
       - Color map (viridis, plasma, inferno, etc.)
       - Surface resolution
    2. Export the surfaces to the group's directory

    Parameters:
    -----------
    my_group : Group
        The group object containing the surfaces to export

    Returns:
    --------
    None
    """
    while True:
        # Main prompt
        print("{} Surface Exports: 1. Shell 2. Filled Body 3. Separate Surfaces 4. All (type \'q\' to quit)".format(
            my_group.name))
        # Input
        surf_npt = input("surface exports (1-4) >>>   ")
        surf_npt.strip()
        # Export the shell
        alls = ['4', '4.', 'four', 'all', 'a']
        # If the user wants to export the shell
        if surf_npt.lower() in ['1', '1.', 'one', 'shell', 'sh'] + alls:
            # Surface setting loop
            while True:
                # Ask the user if they want to change any settings for the surfaces
                print("Surface settings - coloring_scheme = {}, color map = {},  resolution = {}"
                      .format(my_group.surf_scheme, my_group.surf_color, my_group.surf_res))
                change_setting = input("change surfaces setting (y/n) >>>   ")
                if change_setting.lower() in ys:
                    change_surf_setting(my_group)
                elif change_setting.lower() in ns + quits:
                    break
            # Export the shell
            my_group.exports(shell=True)
            print("\r{} shell surfaces exported to {}".format(my_group.name, my_group.dir))
        # If the user wants to export the filled shell
        if surf_npt.lower() in ['2', '2.', 'two', 'filled', 'fb'] + alls:
            # Surface setting loop
            while True:
                # Ask the user if they want to change any settings for the surfaces
                print("Surface settings - coloring_scheme = {}, color map = {},  resolution = {}"
                      .format(my_group.surf_scheme, my_group.surf_color, my_group.surf_res))
                # Ask the user if they want to change any settings for the surfaces
                change_setting = input("change surfaces setting (y/n) >>>   ")
                if change_setting.lower() in ys:
                    change_surf_setting(my_group)
                elif change_setting.lower() in ns + quits:
                    break
            # Export the filled shell surfaces
            my_group.exports(surfs=True)
            print("\r{} filled surfaces exported to {}".format(my_group.name, my_group.dir))
        # If the user wants to export the separate surfaces
        if surf_npt.lower() in ['3', '3.', 'three', 'surfs', 'surfaces'] + alls:
            # Surface setting loop
            while True:
                # Ask the user if they want to change any settings for the surfaces
                print("Surface settings - coloring_scheme = {}, color map = {},  resolution = {}"
                      .format(my_group.surf_scheme, my_group.surf_color, my_group.surf_res))
                change_setting = input("change surfaces setting (y/n) >>>   ")
                if change_setting.lower() in ys:
                    change_surf_setting(my_group)
                elif change_setting.lower() in ns + quits:
                    break
            # Export the surfaces
            my_group.exports(sep_surfs=True)
            print("\r{} surfaces exported to {}".format(my_group.name, my_group.dir))
        if surf_npt.lower() in quits:
            break


def export_atoms(my_group=None):
    """
    Handles the export of atom-related data from a group.

    This function provides an interactive interface for exporting different types of atom data:
    1. All atoms in the group
    2. Surrounding atoms (atoms near the surface)
    3. Exterior atoms (atoms on the surface)
    4. All atom types

    The function displays current export options and prompts the user to select which type of atoms
    to export. Each export type is saved to the group's directory in a 'surfaces' subfolder.

    Parameters:
    -----------
    my_group : Group, optional
        The group containing the atoms to export. If None, no exports will be performed.

    Returns:
    --------
    None
    """
    while True:
        # Main prompt
        print("{} Atoms Exports 1. All Atoms 2. Surrounding Atoms 3. Exterior Atoms 4. All (type \'q\' to quit)".format(
            my_group.name))
        # Input
        surf_npt = input("atoms (1-4) >>>   ")
        surf_npt.strip()
        # Export the shell
        alls = ['4', '4.', 'four', 'all', 'a']
        if surf_npt.lower() in ['1', '1.', 'one', 'atoms'] + alls:
            my_group.exports(atoms=True)
            print("\r{} atoms exported to {}".format(my_group.name, my_group.dir + "/surfaces"))
        if surf_npt.lower() in ['2', '2.', 'two', 'sur', 'sa'] + alls:
            my_group.exports(surr_atoms=True)
            print("\r{} surrounding atoms exported to {}".format(my_group.name, my_group.dir + "/surfaces"))
        if surf_npt.lower() in ['3', '3.', 'three', 'ext', 'ea'] + alls:
            my_group.exports(ext_atoms=True)
            print("\r{} exterior atoms exported to {}".format(my_group.name, my_group.dir + "/surfaces"))
        if surf_npt.lower() in quits:
            break


def export_info(my_group=None):
    """
    Handles the export of information and statistics from a group.

    This function provides an interactive interface for exporting and displaying group information:
    1. Display current group statistics (volume, surface area, etc.)
    2. Export detailed information to a file

    The function displays current export options and prompts the user to select which type of information
    to view or export. Information exports are saved to the group's directory.

    Parameters:
    -----------
    my_group : Group, optional
        The group containing the information to export. If None, no exports will be performed.

    Returns:
    --------
    None
    """
    while True:
        # Main prompt
        print("{} Information 1. Show Info 2. Info Export (type \'q\' to quit)".format(my_group.name))
        # Input Prompt
        nfo_npt = input("info (1-2) >>>   ")
        # Export the shell
        alls = ['4', '4.', 'four', 'all', 'a']
        if nfo_npt.lower() in ['1', '1.', 'one', 'show', 'sh'] + alls:
            my_group.get_info()
            print("Volume:", round(my_group.vol, 3), "Surface Area:", round(my_group.sa, 3))
        if nfo_npt.lower() in ['2', '2.', 'two'] + alls:
            my_group.exports(info=True)
            print("\r{} information file exported to {}".format(my_group.name, my_group.dir))
        if nfo_npt.lower() in quits:
            break


def export_verts(my_group=None):
    """
    Handles the export of network vertices and edges from a group.

    This function provides an interactive interface for exporting network components:
    1. Vertices - Export the main network vertices
    2. Edges - Export the main network edges
    3. Shell Vertices - Export vertices from the shell network
    4. Shell Edges - Export edges from the shell network

    The function displays current export options and prompts the user to select which type of network
    components to export. Exports are saved to the group's directory.

    Parameters:
    -----------
    my_group : Group, optional
        The group containing the network components to export. If None, no exports will be performed.

    Returns:
    --------
    None
    """
    while True:
        # Main prompt
        print("{} Network Exports 1. Vertices 2. Edges 3. Shell Vertices 4. Shell Edges (type \'q\' to quit)".format(
            my_group.name))
        # Input
        verts_npt = input("network (1-4) >>>   ")
        if verts_npt.lower() in ['1', '1.', 'one', 'verts', 'vertices']:
            my_group.exports(verts=True)
            print("\r{} vertices exported to {}".format(my_group.name, my_group.dir))
        if verts_npt.lower() in ['2', '2.', 'two', "edges", "e"]:
            my_group.exports(edges=True)
            print("\r{} edges exported to {}".format(my_group.name, my_group.dir))
        if verts_npt.lower() in ['3', '3.', 'three', 'sv', 'shell_verts']:
            my_group.exports(verts=True, shell=True)
            print("\r{} shell vertices exported to {}".format(my_group.name, my_group.dir))
        if verts_npt.lower() in ['4', '4.', 'four', "se", "shell_edges"]:
            my_group.exports(edges=True, shell=True)
            print("\r{} shell edges exported to {}".format(my_group.name, my_group.dir))
        if verts_npt.lower() in quits:
            break


def export(sys, usr_npt, my_group=None):
    """
    Handles the export of various components from a molecular system or group.

    This function provides an interactive interface for exporting different types of data:
    1. Surfaces and interfaces - Exports surface meshes and interface data
    2. Atoms - Exports atomic coordinates and properties
    3. Information - Exports metadata and system information
    4. Vertices and Edges - Exports network topology data
    5. All - Exports all available data types

    The function first ensures a valid group exists and an output directory is set.
    It then presents export options to the user and handles the export process
    based on their selection.

    Parameters:
    -----------
    sys : System
        The system containing the data to export
    usr_npt : list
        User input specifying export parameters
    my_group : Group, optional
        Specific group to export from. If None, a new group is created based on usr_npt.

    Returns:
    --------
    None
    """
    # If no group was specified, create a new one
    if my_group is None:
        my_group = group(sys, usr_npt)
    # If no output directory was set, set it
    if sys.files['dir'] is None:
        sys.set_output_directory()
    # Export loop
    while True:
        # Main prompt
        print(
            "Exports 1. Surfaces and interfaces 2. Atoms 3. Information 4. Vertices and Edges 5. All (type \'q\' to quit)")
        # Export the group exports
        xpt_npt = input("export type (1-5) >>>   ")
        xpt_npt = xpt_npt.strip()
        # Check for a quit
        if xpt_npt.lower() in quits + ns:
            return
        # Check for help request
        elif xpt_npt.lower() in helps:
            print_help()
            continue
        all_strs = ['5', '5.', 'five', 'all', 'a']
        # Export the shell:
        if xpt_npt.lower() in ['1', '1.', 'surfaces'] + all_strs:
            # Call the Surfaces function
            export_surfs(my_group=my_group)
        # Export the Surfaces
        if xpt_npt.lower() in ['2', '2.', 'atoms', 'a'] + all_strs:
            export_atoms(my_group=my_group)
        # Export the layers
        if xpt_npt.lower() in ['3', '3.', 'info', 'information', 'i'] + all_strs:
            export_info(my_group=my_group)
        # Export the atoms
        if xpt_npt.lower() in ['4', '4.', 'vertices', 'verts', 'v'] + all_strs:
            export_verts(my_group=my_group)
    # Print where the files were exported to
    print("Files were exported to: {}".format(sys.files['dir']))
