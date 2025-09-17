
<p align="center">
  <img width="300" height="300" alt="VorpyIcon" src="https://github.com/user-attachments/assets/1a05cec4-6751-40ef-999f-702b8b629fdf" />
</p>

# VorPy

![TOC-page001](https://github.com/user-attachments/assets/acbdf9f5-3770-4c8c-b922-aeb681542c96)

## Overview
Vorpy is a spatial partitioning tool designed to solve, analyze, and export Additively Weighted, Power (Leguerre), and/or Primitive (Delaunay) Voronoi diagrams for systems of 3D spheres. This tool can accept atomic coordinate files of all major file extensions (or txt files in the right format), solve their Voronoi graphs and output visualizations and analysis of their geometry. With both a grapical user interface for simple cases and a command line interface for more complicated or cases VorPy has a robust input/output abilities. 

## Usage

Vorpy is available as a PyPI package. After installing it with pip (`pip install vorpy3`), you can launch the main GUI (see [VorPy GUI](#vorpy-gui)) by running the following in a Python interpreter:

    import vorpy as vp
    vp.run()


<a name="vorpy-gui"></a>
### VorPy GUI:


<img width="2040" height="1320" alt="VorpyGUIDescription-page001" src="https://github.com/user-attachments/assets/43f33001-3ef3-427e-9293-eef0382d754c" />






For detailed documentation, please visit [the documentation website](https://jackericson98.github.io/vorpy/).

1. **Input File Name**: The name of the ball file with the extension and the folder stripped. This will be the name of the folder that will hold the output files and will hold each of the group folders.
2. **Input File Information**: Displays the general information about the input file and the groupings within it.
3. **Input Locations**: Shows where the input file, the output directory, and any other loaded files can be located.
4. **Radii/Mass Changing**: Allows the user to adjust the radii and masses of any given element and/or specific atoms in set residues (see [Radii/Mass Adjustments](#radii-mass-adjustments)).
5. **System Exports**: Shows the different options for exports at the system level. Launches another window with different options including logs, ball files, set atoms (see [System](#system))
6. **Reset**: Clears the program of any system, files, and settings that have been added.
7. **Groups Section**: Holds each of the groups to be built and all of the corresponding selections, settings, and exports (see [Groups](#groups-gui))
8. **Group Name**: Changes the name for the current group. Works as the name for the sub-directory for the given group's output files
9. **Group Selections**: Allows the user to add/delete atoms/balls, residues, chains, and molecules using and index or a range. If the range entry is unfilled only the single object's index identified in the index entry box will be chosen. The indices start at 0 and correspond to the oder in which they appear in the ball file.
10. **Group Selection Tracker**: Tracks the selections that the the user has added to the group.
11. **Group Build Settings**: Tracks the given settings the given group will be built with
12. **Group Exports**: Holds the different exports for the given group. There are three default options: small, medium, and large exports. If the user wants to export custom options, there is a custom exports button with all possible exports for the group.
13. **Run Group**: Solves the group and exports the given exports. Will only solve the current group and export the current selection.
14. **Add/Delete Groups**: Adjusts the number of groups being solved. The delete button points to the current group and will ask for permission before deleting anything.
15. **Help**: The help button launches a window that explains all of the functions of the program and the GUI and serves as a reminder for the user (see [Help Window](#help-window))
16. **Run All Groups**: Solves and exports all groups as well as the system exports. The main run function for VorPy.


<a name="radii-mass-adjustments"></a> 
#### Radii/Mass Adjustments:

When selected, the radii adjustment window will launch. 



<a name="system"></a>
#### System Exports

 The System Information frame provides an overview and management interface for your 
        system's core configuration:


• System Name: Displays the current system's name, which is typically derived from 
    the selected input file.

• Input File: Allows you to select the primary structure file (e.g., PDB) that 
    defines the molecular system to be analyzed.

• Additional Files: Lists any supplementary files (such as radii, topology, or 
    parameter files) associated with the system, if applicable.

• Output Directory: Lets you specify the folder where all generated results and 
    exports will be saved.

    
To configure your system, use the "Select File" button to choose your main input
file, and the "Select Directory" button to set the output location. The frame 
will update to reflect your selections and display relevant file information. This 
ensures that all subsequent operations and exports are performed using the correct 
files and directories.


<a name="groups-gui"></a>
#### Groups

 The Groups frame provides a comprehensive interface for managing and configuring 
distinct groups within your system. Groups allow you to organize atoms, residues, 
chains, or molecules into logical sets, each of which can be processed independently 
with its own settings.

• Group Selection: Select specific atoms/balls, residues, chains, or molecules from 
    the input file to define the members of each group. This enables targeted analysis 
    or export of particular regions or components of your system.

Key features of the Groups frame include:

• Group-Specific Build Settings: Each group contains its own build settings (see the 
    "Build Settings" tab for details), allowing you to customize parameters such as 
    network type, maximum vertex count, box size, and surface calculation options on a 
    per-group basis.

• Group Management: 
    - Add or delete groups as needed to organize your workflow.
    - Rename groups to provide meaningful identifiers for each set.
    - Use the provided tabs to easily track, switch between, and manage multiple 
    groups within your project.


• Group-Specific Export Settings: Configure export options for each group 
    individually (see the "Export Settings" tab for more information). This includes 
    selecting which data to export, output formats, and destination directories.

• Run Controls: 
    - Run calculations for all groups collectively, or execute only a specific group 
    as needed.
    - Each group can be processed independently, enabling flexible and efficient 
    workflows.

• Visual Tracking: The Groups frame uses tabs or a list to help you keep track of 
    all defined groups, their settings, and their current status.

    
The Groups frame is central to organizing your analysis, enabling you to tailor 
network construction and export options for different parts of your system. By 
leveraging group-specific settings, you can perform detailed, customized analyses 
and exports for each region of interest.


<a name="run-function"></a>
### Run Function

If the package was received using PyPi, and the user wants to run multiple files, operate the package outside of the GUI, or integrate the package into an existing script, they can use the same run funciton with a file location:

    import vorpy as vp
    my_data = vp.run('location_to_file')

This allows the user to continue to perform operations on the data afterwords, loop through several files, change settings, change groups, or change exports without running multiple scripts. 

The parameters for this operation are similar to what can be found in the GUI:

1. file - The input ball/atom file holding the locations and radii of the 



<a name="command-line"></a>
### Command line:

If the package was downloaded over github or another repository and not prepackaged, as would be found in the The general structure of the command line follows the structure outlined below:

    python vorpy/cmd.py <file>


#### File
- The first argument after `vorpy.py` should be the file address of the ball or atom file.
- If the file is located in the `vorpy/src/data` folder, specify the file name without the path or extension.
- Accepted file extensions include `.pdb`, `.mol`, `.gro`, `.cif`.


#### Load Options (Flag `-l`)
    -l <file>
Load additional files like vertex files from previous runs, log files, Voronota vertex files, or GROMACS index files.

#### Setting Options (Flag `-s`)
    -s <setting value>
Adjust various simulation parameters:
- `nt` - Network Type: Default = Additively Weighted `aw`, Power `pow`, Primitive `prm`, or Compare `com 'type1' 'type2'`
- `mv` - Maximum Vertex: Default = `40`
- `bm` - Box Multiplier: Default = `1.25`
- `sr` - Surface Resolution: Default = `0.2` 
- `sc` - Surface Color Map: Default = `viridis`, `plasma`, `rainbow`, or any other [matplotlib colormap](https://matplotlib.org/stable/gallery/color/colormap_reference.html) (note: '_r' inverts the scheme)
- `ss` - Surface Coloring Scheme: Default = curvature `curv`, inside vs outside spheres `nout`, distance from center `dist`
- `sf` - Surface Coloring Scale: Default = linear `lin`, log `log`, squared `square`, cube `cube`
- `ar` - Adjust Radii: `'element' 'value'` or `'atom name' 'value'` or `'residue' 'atom name' 'value'`. To see the current values for defaults for atomic radii go to the radii file (radii.py) or enter the radii flag`-r`

#### Group Options (Flag `-g`)
    -g <identifier>
Select specific balls or molecular elements:
- `b` - Ball Identifier. Used with a ball index `'index'` or range of indices `'index1'-'index2'`.
- `a` - Atom Identifier. Used with an atom element `'element'`, element name `'element name'`, index `'index'`, or range of indices `'index1'-'index2'`.
- `r` - Residue Identifier. Used with a residue name `'residue name'` and sequence number `'sequence number'` (optional), index `'index'`, or range of indices `'index1'-'index2'`.
- `c` - Chain Identifier. Used with a chain name `'chain name'`, index `'index'`, or range of indices `'index1'-'index2'`.

Note: If multiple of the above components are desired in the same group use the `and` qualifier between components. If multiple groups are desired use multiple group flags.  

#### Export Options (Flag `-e`)
    -e <export_type>
Specify the intensity and type of exports:
- Groups of Exports: Default = `large`, `small`, `medium`, `all`
- Export choices : 

   Molecule File - `pdb`, `mol`, `cif`, `gro`, Set Atoms Radii PyMol Script - `set_atoms`, Group Information - `info`, Network Logs - `logs`, All Surfaces in One File - `surfs`, All Surfaces in Separate Files - `sep_surfs`, All Edges in One File - `edges`, All Edges in Separate Files - `sep_edges`, All Vertices in One File - `verts`, All Vertices in Separate Files - `sep_verts`, Surrounding Surfaces - `shell`, Surrounding Edges - `shell_edges`, Surrounding Vertices - `shell_verts`, Group Atoms - `atoms`, Atoms Surrounding Group - `surr_atoms`

#### Command Line Notes
- Each option flag and its arguments must be separated by spaces.
- To use multiple commands for a single option use 'and' or repeat the flag (except for groups to avoid creating multiple groups).
- Any range can be set with a hyphen and no space (e.g. `-g a 0-100` is a group of the first 101 atoms)


<a name="requirements-and-dependencies"></a>
### Requirements and Dependencies
#### Requirements

- **Python 3.8+**  
  vorPy is developed and tested with Python 3.8 and above.

#### Python Dependencies

The following Python packages are required to run vorPy:

- `numpy`
- `scipy`
- `matplotlib`
- `pandas`
- `Pillow`
- `tkinter` (for GUI)
- `pytest` (for running tests, optional)

You can install all dependencies using:

    pip install -r requirements.txt




### Output Examples

The outputs for the program are either informative or visualizations of the data. In th



### Examples


Example 1: Simple Molecular Visualization
In this example, we look at the molecule EDTA which binds to harmful magnesium ions in food to neutralize them. The EDTA/Mg complex is preloaded into vorPy and can be run simply with the following command:

    python vorpy.py EDTA_Mg

This will solve the additively weighted Voronoi diagram for the EDTA molecule and the Mg atom. Once solved, the program will output the default outputs (see outputs). 

Example 2: 
Separately solve the tyrosine 2 and methionine 1 residues of the cambrin molecule, calculate their interface, and export the large export type of the results

    python vorpy.py cambrin -s sr 0.05 and mv 80 -g tyr 2 -g met 1 -c iface -e large

Example 3:
Calculate the primitive and power networks for the mg atom in the EDTA_Mg molecule and compare the difference

    python vorpy.py EDTA_Mg -s nt compare prm pow -g mg

Example 4:
Solve the network for hairpin and export the shell with the inside and outside parts of the surfaces highlighted at a high resolution

    python vorpy.py hairpin -s ss nout and sr 0.01 -e shell and pdb


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use VORPY in your research, please cite:

```bibtex
@software{vorpy2024,
  author = {John Ericson},
  title = {VORPY: A Python package for Voronoi analysis of molecular structures},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/jackericson98/vorpy}
}
```

## Contact
- Email: [jericson1@gsu.edu](mailto:jericson1@gsu.edu)
- Site: [ericsonlabs.com](ericsonlabs.com)
- Phone: +1 (404)-413-5491
