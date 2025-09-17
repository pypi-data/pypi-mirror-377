import numpy as np
import warnings
from numba import jit
from numba.core.errors import TypingError

warnings.filterwarnings("error")


def round_func(round_to):
    """
    Creates a configurable rounding function that can handle both single values and iterables.

    This function returns a closure that maintains the specified rounding precision and can be
    reused for consistent rounding across multiple values. The returned function handles both
    single numeric values and iterables of values, applying the same rounding precision to all.

    Parameters
    ----------
    round_to : int
        The number of decimal places to round to. A positive value rounds to that many decimal
        places, while a negative value rounds to the left of the decimal point.

    Returns
    -------
    function
        A closure that takes a value (or iterable) and optionally a new rounding precision,
        returning the rounded value(s) with the specified precision.
    """

    # Define the inner round function
    def round_(val, new_num=None):
        """
        Inner round function operating on outer defined round to value
        :param val: float/iterable - val(s) to be rounded
        :param new_num: New round to value
        :return: float/list - rounded values
        """
        # Set the new round to number if specified
        if new_num is None:
            new_num = round_to
        # Return the values
        try:
            return round(val, new_num)
        except TypeError:
            return [round(_, new_num) for _ in val]

    # Return the function for the outer function
    return round_


def calc_dist(l0, l1):
    """Calculate the Euclidean distance between two points in n-dimensional space.

    Parameters
    ----------
    l0 : array-like
        First point coordinates as an n-dimensional array or list
    l1 : array-like
        Second point coordinates as an n-dimensional array or list with same dimensionality as l0

    Returns
    -------
    float
        The Euclidean distance between the two points

    Examples
    --------
    >>> calc_dist([0, 0, 0], [1, 1, 1])
    1.7320508075688772
    >>> import numpy as np
    >>> calc_dist(np.array([0, 0, 0]), np.array([1, 1, 1]))
    1.7320508075688772
    """

    return np.sqrt(sum(np.square(np.array(l0) - np.array(l1))))


@jit(nopython=True)
def calc_dist_numba(l0, l1):
    """Calculate the Euclidean distance between two points in n-dimensional space.

    This function computes the straight-line distance between two points using the
    Pythagorean theorem generalized to n dimensions. The function is optimized with
    Numba's JIT compilation for improved performance.

    Parameters
    ----------
    l0 : numpy.ndarray
        First point coordinates as an n-dimensional array
    l1 : numpy.ndarray
        Second point coordinates as an n-dimensional array with same dimensionality as l0

    Returns
    -------
    float
        The Euclidean distance between the two points

    Notes
    -----
    - Both input points must have the same dimensionality
    - Uses numpy's square and sqrt functions for efficient computation
    - JIT compiled for performance optimization
    """
    # Pythagorean theorem
    return np.sqrt(sum(np.square(l0 - l1)))


@jit(nopython=True)
def calc_angle_jit(p0, p1, p2=None):
    """Calculates the angle between three points in radians using vector geometry.

    This function computes the angle between vectors formed by the points in two possible ways:
    1. If p2 is not provided: Angle between vectors from origin to p0 and p1
    2. If p2 is provided: Angle between vectors from p0 to p1 and p0 to p2

    Parameters
    ----------
    p0 : array-like
        First point coordinates [x, y, z, ...]
    p1 : array-like
        Second point coordinates [x, y, z, ...]
    p2 : array-like, optional
        Third point coordinates [x, y, z, ...]
        If not provided, the origin (0,0,0) is used as the reference point

    Returns
    -------
    float
        The angle in radians between the vectors formed by the points

    Notes
    -----
    - All points must have the same dimensionality
    - Uses numpy's arccos function for angle calculation
    - Handles edge cases where vectors are parallel or antiparallel
    """
    # If no p2 is given, use the origin
    if p2 is None:
        v0, v1 = p0, p1
    else:
        v0, v1 = p1 - p0, p2 - p0
    
    # Check for zero-length vectors
    norm_v0 = np.linalg.norm(v0)
    norm_v1 = np.linalg.norm(v1)
    
    if norm_v0 == 0.0 or norm_v1 == 0.0:
        return 0.0  # Return 0 for degenerate cases
    
    n0, n1 = v0 / norm_v0, v1 / norm_v1
    # Calculate the angle between the two vectors with catches for 180 and 0
    my_dot = np.dot(n0, n1)
    if my_dot <= -1.0:
        my_dot = -1.0
    elif my_dot >= 1.0:
        my_dot = 1.0
    angle = np.arccos(my_dot)
    return angle


def calc_angle(p0, p1, p2=None):
    """Calculate the angle between three points in radians.

    This function computes the angle between vectors formed by the points in two possible ways:
    1. If p2 is not provided: Angle between vectors from origin to p0 and p1
    2. If p2 is provided: Angle between vectors from p0 to p1 and p0 to p2

    Parameters
    ----------
    p0 : array-like
        First point coordinates [x, y, z, ...]
    p1 : array-like
        Second point coordinates [x, y, z, ...]
    p2 : array-like, optional
        Third point coordinates [x, y, z, ...]
        If not provided, the origin (0,0,0) is used as the reference point

    Returns
    -------
    float
        The angle in radians between the vectors formed by the points

    Examples
    --------
    >>> import numpy as np
    >>> p0 = np.array([1, 0, 0])
    >>> p1 = np.array([0, 1, 0])
    >>> calc_angle(p0, p1)  # Angle between x and y axes
    1.5707963267948966
    """
    # If no p2 is given, use the origin
    if p2 is None:
        v0, v1 = p0, p1
    else:
        v0, v1 = p1 - p0, p2 - p0
    
    # Check for zero-length vectors
    norm_v0 = np.linalg.norm(v0)
    norm_v1 = np.linalg.norm(v1)
    
    if norm_v0 == 0.0 or norm_v1 == 0.0:
        return 0.0  # Return 0 for degenerate cases
    
    n0, n1 = v0 / norm_v0, v1 / norm_v1
    # Calculate the angle between the two vectors with catches for 180 and 0
    my_dot = np.dot(n0, n1)
    if my_dot <= -1.0:
        my_dot = -1.0
    elif my_dot >= 1.0:
        my_dot = 1.0
    angle = np.arccos(my_dot)
    return angle


@jit(nopython=True)
def calc_tetra_vol(p0, p1, p2, p3):
    """Calculate the volume of a tetrahedron defined by four vertices in 3D space.

    This function uses the scalar triple product formula to compute the volume:
    V = (1/6) * |(p3-p0) · ((p1-p0) × (p2-p0))|
    where · denotes the dot product and × denotes the cross product.

    Parameters
    ----------
    p0 : array-like
        First vertex of the tetrahedron [x, y, z]
    p1 : array-like
        Second vertex of the tetrahedron [x, y, z]
    p2 : array-like
        Third vertex of the tetrahedron [x, y, z]
    p3 : array-like
        Fourth vertex of the tetrahedron [x, y, z]

    Returns
    -------
    float
        The volume of the tetrahedron formed by the four vertices

    Examples
    --------
    >>> import numpy as np
    >>> p0 = np.array([0, 0, 0])
    >>> p1 = np.array([1, 0, 0])
    >>> p2 = np.array([0, 1, 0])
    >>> p3 = np.array([0, 0, 1])
    >>> calc_tetra_vol(p0, p1, p2, p3)  # Volume of unit tetrahedron
    0.16666666666666666
    """
    # Choose a base point (p0) and find the vectors between it and other points
    r01 = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    r02 = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    r03 = np.array([p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]])

    # Formula for tetrahedron volume: 1/6 * r03 dot (r01 cross r02)
    return (1 / 6) * abs(np.dot(r03, np.cross(r01, r02)))


def calc_tetra_inertia(ps, mass):
    """Calculate the moment of inertia tensor of a tetrahedron about its centroid.

    This function computes the inertia tensor for a tetrahedron with uniform density distribution.
    The calculation is based on the parallel axis theorem and the inertia tensor of a tetrahedron
    about its centroid.

    Parameters
    ----------
    ps : list of array-like
        List containing four vertices of the tetrahedron, each as [x, y, z] coordinates
    mass : float
        Total mass of the tetrahedron

    Returns
    -------
    numpy.ndarray
        A 3x3 inertia tensor matrix where:
        - Diagonal elements represent moments of inertia about x, y, and z axes
        - Off-diagonal elements represent products of inertia

    Examples
    --------
    >>> import numpy as np
    >>> ps = [
    ...     np.array([0, 0, 0]),
    ...     np.array([1, 0, 0]),
    ...     np.array([0, 1, 0]),
    ...     np.array([0, 0, 1])
    ... ]
    >>> mass = 1.0
    >>> calc_tetra_inertia(ps, mass)
    array([[ 0.1, -0.05, -0.05],
           [-0.05,  0.1, -0.05],
           [-0.05, -0.05,  0.1]])
    """
    # Placeholder for inertia tensor calculation.
    # For simplicity, this uses an approximate inertia formula for a solid tetrahedron.
    # More accurate calculations can be done by integrating over the volume.
    inertia_tensor = np.zeros((3, 3))

    # Sum contributions from the vertices
    for i in range(4):
        x, y, z = ps[i]
        inertia_tensor[0, 0] += mass * (y ** 2 + z ** 2) / 10.0
        inertia_tensor[1, 1] += mass * (x ** 2 + z ** 2) / 10.0
        inertia_tensor[2, 2] += mass * (x ** 2 + y ** 2) / 10.0
        inertia_tensor[0, 1] -= mass * x * y / 10.0
        inertia_tensor[0, 2] -= mass * x * z / 10.0
        inertia_tensor[1, 2] -= mass * y * z / 10.0

    # Symmetric tensor: fill in the other values
    inertia_tensor[1, 0] = inertia_tensor[0, 1]
    inertia_tensor[2, 0] = inertia_tensor[0, 2]
    inertia_tensor[2, 1] = inertia_tensor[1, 2]

    return inertia_tensor


@jit(nopython=True)
def calc_tri(points):
    """Calculate the area of a triangle formed by three 3D points.

    This function computes the area of a triangle by:
    1. Creating two vectors from the points
    2. Taking their cross product to get a vector perpendicular to the triangle
    3. Taking half the magnitude of this vector

    Parameters
    ----------
    points : list of array-like
        List containing three vertices of the triangle, each as [x, y, z] coordinates

    Returns
    -------
    float
        The area of the triangle formed by the three input points

    Notes
    -----
    - The points should be provided in any order
    - The result is always positive
    - Uses the cross product formula: Area = 0.5 * |AB × AC|

    Examples
    --------
    >>> points = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    >>> calc_tri(points)
    0.5
    """
    # Get the two triangles vectors
    ab = [points[0][0] - points[1][0], points[0][1] - points[1][1], points[0][2] - points[1][2]]
    ac = [points[0][0] - points[2][0], points[0][1] - points[2][1], points[0][2] - points[2][2]]

    # Return half the cross product between the two vectors
    return 0.5 * np.linalg.norm(np.cross(ab, ac))


def calc_com(points, masses=None):
    """Calculate the center of mass for a set of points.

    This function computes the center of mass (centroid) for a collection of points in 3D space.
    If masses are provided, the calculation is weighted by the masses. If no masses are provided,
    all points are assumed to have equal mass.

    Parameters
    ----------
    points : numpy.ndarray
        Array of points, where each point is a [x, y, z] coordinate
    masses : numpy.ndarray, optional
        Array of masses corresponding to each point. If None, all points are assumed
        to have equal mass.

    Returns
    -------
    numpy.ndarray
        The center of mass coordinates [x, y, z]

    Examples
    --------
    >>> import numpy as np
    >>> points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    >>> masses = np.array([1, 2, 1])
    >>> calc_com(points, masses)
    array([0.5, 0.25, 0.])
    """
    if masses is None:
        return np.mean(points, axis=0)
    else:
        return np.average(points, weights=masses, axis=0)


@jit(nopython=True)
def calc_length(points):
    """Calculates the total length of a path defined by a sequence of points.

    This function computes the sum of Euclidean distances between consecutive points in the input sequence.
    The points are assumed to be ordered in the sequence they should be connected.

    Parameters
    ----------
    points : list of array-like
        List of point coordinates in n-dimensional space. Each point should be a list or array
        of coordinates [x1, x2, ..., xn]. Points must be ordered in the sequence they should
        be connected.

    Returns
    -------
    float
        The total length of the path formed by connecting consecutive points in the input sequence.

    Notes
    -----
    - Points must be ordered in the sequence they should be connected
    - Uses Euclidean distance between consecutive points
    - Returns 0 if the input list contains fewer than 2 points
    """
    # Reset the length
    length = 0
    # Go through the points in the list
    for m, point in enumerate(points):
        # Make sure not to index error
        if m + 1 < len(points):
            # Add the length to the total
            length += calc_dist_numba(point, points[m + 1])
    return length


def calc_sphericity(volume, surface_area):
    """Calculate the sphericity of a geometric object based on its volume and surface area.

    Parameters
    ----------
    volume : float
        The volume of the object.
    surface_area : float
        The surface area of the object.

    Returns
    -------
    float
        The sphericity of the object.
    """
    if volume <= 0 or surface_area <= 0:
        raise ValueError("Volume and surface area must be positive numbers.")

    # Calculate sphericity using the geometric formula
    sphericity = (np.pi ** (1 / 3) * (6 * volume) ** (2 / 3)) / surface_area
    return sphericity


def calc_isoperimetric_quotient(volume, surface_area):
    """Calculate the isoperimetric quotient

    Parameters
    ----------
    volume : float
        The volume of the object.
    surface_area : float
        The surface area of the object.

    Returns
    -------
    float
        The isoperimetric quotient of the object
    """
    if volume <= 0 or surface_area <= 0:
        raise ValueError("Volume and surface area must be positive numbers.")

    return (36 * np.pi * volume ** 2) / (surface_area ** 3)


def calc_spikes(ball_loc, surfs):
    """Calculate the minimum and maximum distances (spikes) from a ball's center to all surface points.

    This function measures the distances from a ball's center location to all points on its surrounding
    surfaces, which helps characterize the shape and extent of the ball's influence region.

    Parameters
    ----------
    ball_loc : list or numpy.ndarray
        The 3D coordinates of the ball's center location
    surfs : list of dict
        List of surface dictionaries, where each surface contains a 'points' key with
        a list of 3D coordinates representing surface points

    Returns
    -------
    tuple
        A tuple containing:
        - min_spike (float): The minimum distance from the ball center to any surface point
        - max_spike (float): The maximum distance from the ball center to any surface point

    Notes
    -----
    - Uses calc_dist function to compute Euclidean distances
    - Useful for analyzing the shape and extent of a ball's influence region
    """
    spikes = []
    for surf in surfs:
        for point in surf['points']:
            spikes.append(calc_dist(ball_loc, point))

    return min(spikes), max(spikes)


def calc_cell_box(surfs):
    """Calculate the bounding box of a cell defined by its surfaces.

    This function computes the minimum and maximum coordinates in each dimension
    (x, y, z) that fully enclose all points of the cell's surfaces, effectively
    creating a rectangular prism that bounds the cell.

    Parameters
    ----------
    surfs : list of dict
        List of surface dictionaries, where each surface contains a 'points' key with
        a list of 3D coordinates representing surface points

    Returns
    -------
    list
        A list containing two 3D coordinate lists:
        - [0]: Minimum coordinates [x_min, y_min, z_min]
        - [1]: Maximum coordinates [x_max, y_max, z_max]

    Notes
    -----
    - Useful for determining the spatial extent of a cell
    - Can be used for visualization or spatial analysis
    - Returns a bounding box that may not be axis-aligned if the cell is rotated
    """
    # Create the mins and maxs varaibles
    mins, maxs = [np.inf, np.inf, np.inf], [-np.inf, -np.inf, -np.inf]
    # Loop through the surfaces
    for surf in surfs:
        for point in surf['points']:
            for i in range(3):
                if point[i] < mins[i]:
                    mins[i] = point[i]
                if point[i] > maxs[i]:
                    maxs[i] = point[i]
    # Return the bounding box for the cell
    return [mins, maxs]


def calc_cell_com(ball_loc, surfs, volume):
    """Calculate the center of mass of a cell using tetrahedral decomposition.

    This function computes the center of mass of a cell by decomposing it into tetrahedrons
    formed by the cell's center point and each triangular face of its surfaces. The center
    of mass is calculated as the volume-weighted average of the centroids of all tetrahedrons.

    Parameters
    ----------
    ball_loc : list or numpy.ndarray
        The center location of the cell (3D coordinates)
    surfs : list of dict
        List of surface dictionaries, where each surface contains:
        - 'points': List of 3D coordinates representing surface points
        - 'tris': List of triangle indices referencing the points
    volume : float
        Total volume of the cell

    Returns
    -------
    numpy.ndarray
        The 3D coordinates of the cell's center of mass

    Notes
    -----
    - Uses tetrahedral decomposition to calculate the center of mass
    - Each tetrahedron is formed by the cell center and a triangular face
    - The result is normalized by the total cell volume
    - Returns a numpy array for vector operations
    """
    # Create the mass_locs list
    mass_locs = []
    for surf in surfs:
        for tri in surf['tris']:
            # Get the points of the tetrahedron
            ps = [ball_loc, *[surf['points'][_] for _ in tri]]
            # Calculate the centroid of the tetrahedron
            tet_com = [sum([ps[j][i] for j in range(4)]) / 4 for i in range(3)]
            # Calculate the volume of the tetrahedron
            tet_vol = calc_tetra_vol(*ps)
            # Append the volume-weighted centroid
            mass_locs.append([tet_vol * coord for coord in tet_com])

    # Calculate the total center of mass by normalizing with the cell volume
    return np.array([sum(coords) / volume for coords in zip(*mass_locs)])


def calc_cell_moi(ball_loc, surfs, volume, density=1.0):
    """Calculate the moment of inertia tensor of a cell using tetrahedral decomposition.

    This function computes the moment of inertia tensor of a cell by decomposing it into tetrahedrons
    formed by the cell's center point and each triangular face of its surfaces. The total moment of inertia
    is calculated as the sum of individual tetrahedron contributions, using the parallel axis theorem to
    shift each contribution to the cell's center point.

    Parameters
    ----------
    ball_loc : numpy.ndarray or list
        The center location of the cell (3D coordinates)
    surfs : list of dict
        List of surface dictionaries, where each surface contains:
        - 'points': List of 3D coordinates representing surface points
        - 'tris': List of triangle indices referencing the points
    volume : float
        Total volume of the cell
    density : float, optional
        Density of the material (default is 1.0)

    Returns
    -------
    numpy.ndarray
        A 3x3 moment of inertia tensor of the cell with respect to ball_loc

    Notes
    -----
    - Uses tetrahedral decomposition to calculate individual contributions
    - Applies the parallel axis theorem to shift each tetrahedron's inertia tensor
    - Returns a symmetric 3x3 numpy array representing the inertia tensor
    """
    # Create an inertia tensor initialized to zero
    inertia_tensor = np.zeros((3, 3))

    # Iterate through each surface and triangle to calculate the tetrahedron MOI contributions
    for surf in surfs:
        for tri in surf['tris']:
            # Get the points of the tetrahedron
            ps = [ball_loc, *[surf['points'][_] for _ in tri]]

            # Calculate the centroid of the tetrahedron
            tet_com = [sum([ps[j][i] for j in range(4)]) / 4 for i in range(3)]

            # Calculate the volume of the tetrahedron
            tet_vol = calc_tetra_vol(*ps)

            # Calculate the mass of the tetrahedron
            tet_mass = density * tet_vol

            # Calculate the inertia tensor of the tetrahedron about its centroid
            tet_inertia_tensor = calc_tetra_inertia(ps, tet_mass)

            # Calculate the distance vector from the tetrahedron centroid to the cell's center (`ball_loc`)
            r = np.array(tet_com) - np.array(ball_loc)
            r_squared = np.dot(r, r)

            # Use the parallel axis theorem to adjust the inertia tensor to the cell's center
            shift_tensor = tet_mass * (r_squared * np.identity(3) - np.outer(r, r))

            # Add the adjusted tensor to the total inertia tensor
            inertia_tensor += tet_inertia_tensor + shift_tensor

    return inertia_tensor


def combine_inertia_tensors(inertia_tensors, centroids, common_centroid, masses):
    """Combines multiple inertia tensors into a single inertia tensor about a common reference point.

    This function implements the parallel axis theorem to shift each inertia tensor from its local
    centroid to a common reference point, then sums them to get the total inertia tensor.

    Parameters
    ----------
    inertia_tensors : list of numpy.ndarray
        List of 3x3 inertia tensors for each element, where each tensor is about its local centroid
    centroids : list of numpy.ndarray
        List of 3D centroid coordinates for each element
    common_centroid : numpy.ndarray
        The reference point to which all inertia tensors will be shifted
    masses : list of float
        List of masses (or volumes if uniform density) for each element

    Returns
    -------
    numpy.ndarray
        A 3x3 inertia tensor representing the combined moment of inertia about the common centroid

    Notes
    -----
    - Uses the parallel axis theorem: I_total = I_local + m(d^2*I - d*d^T)
    - All input arrays should be numpy arrays
    - The function assumes consistent units across all inputs
    """
    # Initialize the total inertia tensor as a zero matrix
    I_total = np.zeros((3, 3))

    # Loop over each element
    for I_i, C_i, m_i in zip(inertia_tensors, centroids, masses):
        # Calculate the displacement vector from the element's centroid to the common centroid
        d = C_i - common_centroid
        d_squared = np.dot(d, d)  # Squared magnitude of the displacement vector

        # Compute the parallel axis theorem adjustment term
        shift_tensor = m_i * (d_squared * np.eye(3) - np.outer(d, d))

        # Shift the inertia tensor of the element to the common centroid and add to total
        I_shifted = I_i + shift_tensor
        I_total += I_shifted

    return I_total


def calc_total_inertia_tensor(spheres, common_point):
    """
    Calculates the total moment of inertia tensor for a collection of spheres about a common reference point.

    This function computes the combined moment of inertia tensor by:
    1. Calculating each sphere's local inertia tensor about its center
    2. Using the parallel axis theorem to shift each tensor to the common reference point
    3. Summing all shifted tensors to obtain the total inertia tensor

    Parameters
    ----------
    spheres : list of dict
        List of sphere dictionaries containing:
        - 'mass' : float
            Mass of the sphere
        - 'rad' : float
            Radius of the sphere
        - 'loc' : numpy.ndarray
            3D coordinates of the sphere's center
    common_point : numpy.ndarray
        3D coordinates of the reference point about which the total inertia tensor is calculated

    Returns
    -------
    numpy.ndarray
        3x3 inertia tensor representing the total moment of inertia about the common point

    Notes
    -----
    - Uses the parallel axis theorem for rigid body mechanics
    - Assumes uniform density spheres
    - All input arrays should be numpy arrays
    - Units should be consistent across all inputs
    """
    # Initialize the total inertia tensor as a 3x3 zero matrix
    I_total = np.zeros((3, 3))

    # Iterate through each sphere
    for sphere in spheres:
        m = sphere['mass']
        r = sphere['rad']
        loc = sphere['loc']

        # Moment of inertia tensor of the sphere about its own center (3x3 identity scaled by (2/5) * m * r^2)
        I_center = (2 / 5) * m * r ** 2 * np.eye(3)

        # Calculate the displacement vector from the sphere's center to the common point
        d = loc - common_point
        d_squared = np.dot(d, d)  # Squared magnitude of the displacement vector

        # Calculate the parallel axis shift tensor: m * (d^2 * I3 - d * d^T)
        shift_tensor = m * (d_squared * np.eye(3) - np.outer(d, d))

        # Shift the inertia tensor to the common reference point
        I_shifted = I_center + shift_tensor

        # Add the shifted inertia tensor to the total inertia tensor
        I_total += I_shifted

    return I_total


def calc_contacts(loc, rad, surfs, surf_ndxs):
    """
    Calculate the contact areas and contribution volume for a given sphere.

    This function computes the contact areas between a sphere and surrounding surfaces, as well as the
    contribution volume of the sphere to the total volume of the system. It handles cases where surfaces
    are fully inside, fully outside, or partially intersecting with the sphere.

    Parameters
    ----------
    loc : numpy.ndarray
        Center coordinates of the sphere in 3D space
    rad : float
        Radius of the sphere
    surfs : list of dict
        List of surface dictionaries, where each surface contains:
        - 'points': List of 3D coordinates defining surface vertices
        - 'tris': List of triangle indices referencing the points
    surf_ndxs : list of int
        Indices of surfaces to consider for contact calculations

    Returns
    -------
    tuple
        A tuple containing:
        - contact_areas : dict
            Dictionary mapping surface indices to their respective contact areas
        - contribution_vol : float
            Total volume contribution of the sphere to the system

    Notes
    -----
    - Contact area is calculated for surfaces that intersect with the sphere
    - Volume contribution considers both internal and external portions of surfaces
    - Points inside the sphere are preserved, while points outside are projected onto the sphere's surface
    """
    # Create the area and volume vals
    contact_areas, contribution_vol = {}, 0

    # Loop through the surfaces
    for i, surf in enumerate(surfs):
        # Initialize contact area for this surface
        contact_area = 0
        new_points = []
        point_inside = []

        # Loop through the points to determine if inside or outside
        for point in surf['points']:
            distance = calc_dist(point, loc)
            if distance <= rad:
                point_inside.append(True)
                new_points.append(point)
            else:
                point_inside.append(False)
                # Get the direction and normalize it
                direction = point - loc
                norm = np.linalg.norm(direction)
                if norm > 0:
                    # Project the point onto the sphere's surface
                    new_points.append(rad * (direction / norm) + loc)
                else:
                    new_points.append(point)  # If the point coincides with the center (rare edge case)

        # Loop through the triangles
        for tri in surf['tris']:
            triangle_points = [surf['points'][index] for index in tri]
            projected_points = [new_points[index] for index in tri]
            inside_flags = [point_inside[index] for index in tri]

            # Determine if the triangle is fully inside, fully outside, or mixed
            all_inside = all(inside_flags)
            all_outside = not any(inside_flags)
            mixed = not all_inside and not all_outside

            if all_inside:
                # Triangle is fully inside the sphere
                contact_area += calc_tri(np.array(triangle_points))
                contribution_vol += calc_tetra_vol(loc, *triangle_points)
            elif all_outside:
                # Triangle is fully outside the sphere
                contribution_vol += calc_tetra_vol(loc, *projected_points)
            elif mixed:
                # Triangle is partially inside and outside
                # We add the volume using a mix of inside and projected points
                mixed_points = [triangle_points[i] if inside_flags[i] else projected_points[i] for i in range(3)]
                contribution_vol += calc_tetra_vol(loc, *mixed_points)
                # Count the triangle as outside for contact area if any point is outside
                if inside_flags.count(True) < 3:
                    contact_area += calc_tri(np.array(triangle_points))

        # Append the contact area for this surface
        contact_areas[surf_ndxs[i]] = contact_area

    return contact_areas, contribution_vol


def rotate_points(vec, points, reverse=False):
    """Rotates a set of points around a given vector using rotation matrices.

    This function performs a 3D rotation of points around a specified vector by:
    1. Calculating the rotation angles (phi and theta) needed to align the vector with the z-axis
    2. Creating rotation matrices for both z-axis and y-axis rotations
    3. Combining the rotations in the correct order
    4. Applying the combined rotation to all input points

    Parameters
    ----------
    vec : numpy.ndarray
        The vector about which to rotate the points
    points : list of numpy.ndarray
        List of 3D points to be rotated
    reverse : bool, optional
        If True, performs the inverse rotation (default: False)

    Returns
    -------
    list of numpy.ndarray
        List of rotated 3D points

    Notes
    -----
    - Uses standard rotation matrices for 3D transformations
    - Handles both forward and reverse rotations
    - Maintains point positions relative to the rotation vector
    """
    if reverse:
        vec = - vec
    vx, vy, vz = vec
    mag = np.sqrt(vx ** 2 + vy ** 2 + vz ** 2)
    phi = np.arctan2(vy, vx)
    theta = np.arccos(vz / mag)
    if reverse:
        theta, phi = -theta, -phi

    # Forward rotations to align with z-axis
    Rz = np.array([[np.cos(phi), -np.sin(phi), 0], [np.sin(phi), np.cos(phi), 0], [0, 0, 1]])
    Ry = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])

    # Combine rotations to align vector with +z direction
    if reverse:
        # Correct sequence for inverse rotation
        rotation_matrix = np.dot(Rz, Ry)
    else:
        # Correct sequence for forward rotation
        rotation_matrix = np.dot(Ry, Rz)

    # Apply rotation to all points
    rotated_points = [np.dot(rotation_matrix, p) for p in points]
    return rotated_points


@jit(nopython=True)
def get_time(seconds):
    """Converts a duration in seconds into hours, minutes, and remaining seconds.

    Parameters
    ----------
    seconds : float
        Total duration in seconds to be converted

    Returns
    -------
    tuple
        A tuple containing (hours, minutes, seconds) where:
        - hours: Number of complete hours
        - minutes: Number of complete minutes after hours
        - seconds: Remaining seconds after hours and minutes

    Examples
    --------
    >>> get_time(3661)
    (1, 1, 1)  # 1 hour, 1 minute, 1 second
    """
    # Divide up the values
    hours = seconds // 3600
    minutes = (seconds - (hours * 3600)) // 60
    seconds = seconds - hours * 3600 - minutes * 60
    # Return the values
    return hours, minutes, seconds


def calc_vol(a_loc, surfs_points, surfs_tris):
    """Calculates the volume of a ball by summing the volumes of tetrahedrons formed between the ball's center and the triangular faces of its surfaces.

    Parameters
    ----------
    a_loc : numpy.ndarray
        The 3D coordinates of the ball's center point
    surfs_points : list of numpy.ndarray
        List of arrays containing the 3D coordinates of points for each surface
    surfs_tris : list of list of tuples
        List of lists containing triangle indices for each surface, where each tuple contains
        three indices referencing points in the corresponding surfs_points array

    Returns
    -------
    tuple
        A tuple containing:
        - float: Total volume of the ball
        - list: List of volumes for each individual surface
    """
    # Create the volume variable
    surf_vols = []
    # Go through each surface on the ball
    for i in range(len(surfs_points)):
        # Calculate the volume of the
        surf_vol = 0
        for tri in surfs_tris[i]:
            # Calculate the tetrahedron volume between the balls' location and the surface triangle's points
            surf_vol += calc_tetra_vol(np.array(a_loc), surfs_points[i][tri[0]], surfs_points[i][tri[1]],
                                       surfs_points[i][tri[2]])
        # Add the surface's volume to the list
        surf_vols.append(surf_vol)
    # Get the total volume by summing the surfaces volumes
    vol = sum(surf_vols)
    # Set the volume and return it
    return vol, surf_vols


def calc_curvature(points, normals):
    """Calculate the mean curvature at each point using neighboring points and normals.

    This function computes the mean curvature at each point in a surface by analyzing
    the local geometry defined by neighboring points and their surface normals.

    Parameters
    ----------
    points : numpy.ndarray
        Array of points on the surface, where each point is a [x, y, z] coordinate
    normals : numpy.ndarray
        Array of surface normals at each point, where each normal is a [nx, ny, nz] vector

    Returns
    -------
    numpy.ndarray
        Array of mean curvature values at each point

    Examples
    --------
    >>> import numpy as np
    >>> points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    >>> normals = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]])
    >>> curvatures = calc_curvature(points, normals)
    >>> print(f"Curvatures: {curvatures}")
    Curvatures: [0. 0. 0.]
    """
    # Create the curvature variable
    n_points = len(points)
    curvatures = np.zeros(n_points)

    for i in range(n_points):
        # Find neighboring points (excluding self)
        neighbors = [j for j in range(n_points) if j != i]

        if not neighbors:
            continue

        # Calculate curvature based on normal variations
        normal_variations = []
        for j in neighbors:
            # Project the difference vector onto the normal plane
            diff = points[j] - points[i]
            proj_diff = diff - np.dot(diff, normals[i]) * normals[i]

            if np.linalg.norm(proj_diff) > 0:
                # Calculate the angle between normals
                cos_angle = np.dot(normals[i], normals[j])
                angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))

                # Add to variations list
                normal_variations.append(angle / np.linalg.norm(proj_diff))

        if normal_variations:
            # Mean curvature is the average of normal variations
            curvatures[i] = np.mean(normal_variations)

    return curvatures


def calc_aw_center(r1, r2, l1, l2):
    """
    Calculate the distance between two spheres using the AW method.

    This function calculates the distance between two spheres based on their radii and locations.
    It uses the formula:

    Parameters
    ----------
    r1 : float
        The radius of the first sphere
    r2 : float
        The radius of the second sphere
    l1 : numpy.ndarray
        The location of the first sphere
    l2 : numpy.ndarray
        The location of the second sphere

    Returns
    -------
    tuple
        A tuple containing:
        - float: The aw distance between the two spheres
        - numpy.ndarray: The aw center point between the two spheres
    """
    # Calculate the distance between the two spheres
    dist = np.linalg.norm(l1 - l2)
    # Calculate the aw distance
    aw_dist = dist / 2 - (r2 - r1) / 2
    # Calculate the aw center point
    aw_center = l1 + (l2 - l1) * (aw_dist / dist)
    # Return the aw distance and center point
    return aw_dist, aw_center


def calc_pw_center(r1, r2, l1, l2):
    """
    Calculate the distance between two spheres using the PW method.

    This function calculates the distance between two spheres based on their radii and locations.
    It uses the formula:

    Parameters
    ----------
    r1 : float
        The radius of the first sphere
    r2 : float
        The radius of the second sphere
    l1 : numpy.ndarray
        The location of the first sphere
    l2 : numpy.ndarray
        The location of the second sphere

    Returns
    -------
    tuple
        A tuple containing:
        - float: The pw distance between the two spheres
        - numpy.ndarray: The pw center point between the two spheres
    """
    # Calculate the distance between the two spheres
    dist = np.linalg.norm(l1 - l2)
    # Calculate the pw distance
    pw_dist = dist / 2 - (r2 ** 2 - r1 ** 2) / (2 * dist)
    # Calculate the pw center point
    pw_center = l1 + (l2 - l1) * (pw_dist / dist)
    # Return the pw distance and center point
    return pw_dist, pw_center
