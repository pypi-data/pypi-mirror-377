import numpy as np
from numba import jit
from vorpy.src.calculations.sorting import box_search
from vorpy.src.calculations.sorting import get_balls
from vorpy.src.calculations.vert import verify_site
from vorpy.src.calculations.calcs import calc_dist
from vorpy.src.visualize import plot_balls


@jit(nopython=True)
def calc_circ_coefs(l0, l1, l2, r0, r1, r2):
    """
    Calculates the coefficients for finding the tangential circle between three spheres.

    This function computes the mathematical coefficients needed to determine the center
    and radius of a circle that is tangent to three given spheres. The calculation is
    based on the relative positions and radii of the spheres.

    Parameters:
    -----------
    l0 : array-like
        Center coordinates of the first sphere [x, y, z]
    l1 : array-like
        Center coordinates of the second sphere [x, y, z]
    l2 : array-like
        Center coordinates of the third sphere [x, y, z]
    r0 : float
        Radius of the first sphere
    r1 : float
        Radius of the second sphere
    r2 : float
        Radius of the third sphere

    Returns:
    --------
    tuple
        A tuple containing:
        - Fs: A tuple of coefficients (F, Fx0, Fx1, Fy0, Fy1, Fz0, Fz1) used in the circle calculation
        - abcs: A list of lists containing the coefficients [a1, a2, a3], [b1, b2, b3], [c1, c2, c3]
    """
    # Move the other balls to the location of the first
    x2, y2, z2 = l1[0] - l0[0], l1[1] - l0[1], l1[2] - l0[2]
    x3, y3, z3 = l2[0] - l0[0], l2[1] - l0[1], l2[2] - l0[2]
    # Calculate coefficients
    a1, b1, c1, d1, f1 = 2 * x2, 2 * y2, 2 * z2, 2 * (r0 - r1), r0 ** 2 - r1 ** 2 + x2 ** 2 + y2 ** 2 + z2 ** 2
    a2, b2, c2, d2, f2 = 2 * x3, 2 * y3, 2 * z3, 2 * (r0 - r2), r0 ** 2 - r2 ** 2 + x3 ** 2 + y3 ** 2 + z3 ** 2
    a3, b3, c3 = y2 * z3 - z2 * y3, z2 * x3 - x2 * z3, x2 * y3 - y2 * x3
    abcs = [[a1, a1, a3], [b1, b2, b3], [c1, c2, c3]]
    # More coefficients
    F = a3 * b2 * c1 - a2 * b3 * c1 - a3 * b1 * c2 + a1 * b3 * c2 + a2 * b1 * c3 - a1 * b2 * c3
    Fx0 = b3 * c2 * f1 - b2 * c3 * f1 - b3 * c1 * f2 + b1 * c3 * f2
    Fx1 = b3 * c2 * d1 - b2 * c3 * d1 - b3 * c1 * d2 + b1 * c3 * d2
    Fy0 = - a3 * c2 * f1 + a2 * c3 * f1 + a3 * c1 * f2 - a1 * c3 * f2
    Fy1 = - a3 * c2 * d1 + a2 * c3 * d1 + a3 * c1 * d2 - a1 * c3 * d2
    Fz0 = a3 * b2 * f1 - a2 * b3 * f1 - a3 * b1 * f2 + a1 * b3 * f2
    Fz1 = a3 * b2 * d1 - a2 * b3 * d1 - a3 * b1 * d2 + a1 * b3 * d2
    Fs = F, Fx0, Fx1, Fy0, Fy1, Fz0, Fz1

    return Fs, abcs


@jit(nopython=True)
def calc_circ_abcs(Fs, r0):
    """
    Calculates the coefficients for the quadratic equation used to determine the radius of a circle tangent to three spheres.

    This function takes the coefficients from calc_circ_coefs and uses them to compute the quadratic equation
    coefficients (a, b, c) that will be used to solve for the radius of the tangential circle.

    Parameters:
    -----------
    Fs : tuple
        A tuple containing the coefficients (F, Fx0, Fx1, Fy0, Fy1, Fz0, Fz1) from calc_circ_coefs
    r0 : float
        Radius of the first sphere

    Returns:
    --------
    tuple
        A tuple containing the quadratic equation coefficients (a, b, c) where:
        - a: Coefficient of r² term
        - b: Coefficient of r term
        - c: Constant term
    """
    F, Fx0, Fx1, Fy0, Fy1, Fz0, Fz1 = Fs
    # Find the radius of the tangential circle using the quadratic formula
    a = (Fx1 ** 2 + Fy1 ** 2 + Fz1 ** 2) / F ** 2 - 1
    b = 2 * (Fx0 * Fx1 + Fy0 * Fy1 + Fz0 * Fz1) / F ** 2 - 2 * r0
    c = (Fx0 ** 2 + Fy0 ** 2 + Fz0 ** 2) / F ** 2 - r0 ** 2
    return a, b, c


def calc_circ(l0, l1, l2, r0, r1, r2, return_both=False):
    """
    Calculates the center and radius of a circle inscribed between three spheres.

    This function computes the geometric properties of a circle that is tangent to three given spheres.
    The solution involves solving a system of equations derived from the geometric constraints
    of tangency between the circle and each sphere.

    Parameters:
    -----------
    l0 : array-like
        Center coordinates of the first sphere [x, y, z]
    l1 : array-like
        Center coordinates of the second sphere [x, y, z]
    l2 : array-like
        Center coordinates of the third sphere [x, y, z]
    r0 : float
        Radius of the first sphere
    r1 : float
        Radius of the second sphere
    r2 : float
        Radius of the third sphere
    return_both : bool, optional
        If True, returns both possible solutions when they exist (default: False)

    Returns:
    --------
    tuple or None
        If a solution exists:
        - When return_both=False: Returns (center, radius) where center is [x,y,z] and radius is float
        - When return_both=True: Returns (center1, radius1, center2, radius2) for both solutions
        Returns None if no valid solution exists
    """
    # Make sure the locations are arrays
    l0, l1, l2 = np.array(l0), np.array(l1), np.array(l2)

    Fs, abcs = calc_circ_coefs(l0, l1, l2, r0, r1, r2)
    # Catch for F=0 (i.e. no circle exists)
    if Fs[0] == 0:
        return
    a, b, c = calc_circ_abcs(Fs, r0)
    # Calculate the discriminant.
    disc = b ** 2 - 4 * a * c
    r2 = None
    # If the discriminant is negative then the tangential circle does not exist.
    if round(disc, 10) > 0:
        # Grab the two roots
        rs = [_ for _ in np.roots(np.array([a, b, c])) if np.isreal(_)]
        # If there is only one root return it
        if len(rs) == 1:
            r = rs[0]
        # If there are 2 roots choose between them
        else:
            # If the smaller of the two roots is negative return the other root
            if min(rs) < 0:
                r = max(rs)
            # If they're both positive, return the smaller of the two
            elif rs[0] > 0 and rs[1] > 0:
                if return_both:
                    r2 = max(rs)
                r = min(rs)
            # If they're both negative return
            else:
                return
        # Calculate the vertex based off of our coefficient values and the sphere's radius
        F, Fx0, Fx1, Fy0, Fy1, Fz0, Fz1 = Fs
        # Calculate the vertex based off of our coefficient values and the sphere's radius
        x = Fx0 / F + r * Fx1 / F + l0[0]
        y = Fy0 / F + r * Fy1 / F + l0[1]
        z = Fz0 / F + r * Fz1 / F + l0[2]
        # Return the first circle
        if not return_both or r2 is None:
            return np.array([x, y, z]), r
        # Calculate the second circle
        x2 = Fx0 / F + r2 * Fx1 / F + l0[0]
        y2 = Fy0 / F + r2 * Fy1 / F + l0[1]
        z2 = Fz0 / F + r2 * Fz1 / F + l0[2]
        # Return the second circle
        return np.array([x, y, z]), r, np.array([x2, y2, z2]), r2


# Find projection values. Calculates the 181L end and projection points for the edge
@jit(nopython=True)
def calc_edge_proj_pt(pv0, pv1, loc):
    """
    Calculates the projection point for an edge between two vertices.

    This function computes a reference point that lies on the projection plane of an edge,
    which is used to determine the direction and position of the edge's projection.

    Parameters:
    -----------
    pv0 : numpy.ndarray
        First vertex point coordinates [x, y, z]
    pv1 : numpy.ndarray
        Second vertex point coordinates [x, y, z]
    loc : numpy.ndarray
        Location point coordinates [x, y, z] used to determine projection direction

    Returns:
    --------
    numpy.ndarray
        A 3D point that lies on the projection plane, representing the reference point
        for edge projection calculations [x, y, z]
    """
    # Find the point in between the two vertex points
    r01 = pv1 - pv0  # Vector between vertices
    r_mag = np.linalg.norm(r01)  # Magnitude of the vector between the two vertex points
    rn01 = r01 / r_mag  # Normal to the vector between the vertices
    pc01 = pv0 + 0.5 * rn01 * r_mag  # Center point

    # Determine if the theoretical center of the edge is inside the vertices or not
    dr = 1
    if np.sqrt(sum(np.square(loc - pv0))) < r_mag or np.sqrt(sum(np.square(loc - pv1))) < r_mag:
        dr = -1

    # Find the vector normal to the projection plane
    p_norm = dr * np.cross(loc - pc01, pv1 - pc01)
    # Find the vector perpendicular to the plane's normal (i.e. in the plane) and the vector between vertices
    r_pcr = - np.cross(p_norm, rn01)
    rn_pcr = r_pcr / np.linalg.norm(r_pcr)
    # Calculate the reference point
    return pc01 + 0.5 * r_mag * rn_pcr


def calc_edge_dir1(locs, rads, eballs, vlocs, edub=False):
    """
    Determines the edge type and calculates the direction vectors for edge point generation.

    This function analyzes the geometric configuration of an edge between two vertices to:
    1. Identify the edge type based on the relative positions of vertices and their connecting circles
    2. Calculate the appropriate direction vectors needed to generate points along the edge

    Parameters:
    -----------
    locs : list of numpy.ndarray
        List of ball center coordinates [x, y, z] for all balls in the system
    rads : list of float
        List of radii for all balls in the system
    eballs : list of int
        Indices of the two balls forming the edge
    vlocs : list of numpy.ndarray
        Vertex locations [x, y, z] for the edge endpoints
    edub : bool, optional
        Flag indicating if this is a double edge case (default: False)

    Returns:
    --------
    dict
        Dictionary containing edge information including:
        - 'loc': Center point of the edge circle
        - 'rad': Radius of the edge circle
        - 'loc2': Optional second center point for double edge cases
        - 'rad2': Optional second radius for double edge cases
        - 'vdist': Distance between vertices
        - 'vnorm': Normalized vector between vertices
        - 'vmid': Midpoint between vertices
        - 'pnorm': Normal vector to the projection plane
        - Additional geometric parameters for edge point generation
    """
    # Calculate the circle
    circ = calc_circ(*[locs[_] for _ in eballs], *[rads[_] for _ in eballs], return_both=True)
    # Set up the loc2 and rad2 variables
    loc2, rad2 = None, None
    # Check the number of returned items
    if len(circ) == 2:
        loc, rad = circ
    elif len(circ) == 4:
        loc, rad, loc2, rad2 = circ
    else:
        return None
    # Calculate the distance between the vertices
    vdist = np.sqrt(sum([np.square(vlocs[0][i] - vlocs[1][i]) for i in range(3)]))
    # Get the center point of the vertices
    vdir = vlocs[1] - vlocs[0]
    # Normalize the vertex vector
    vnorm = vdir / vdist
    # Get the halfway point
    vmid = vlocs[0] + 0.5 * vdist * vnorm
    # Find the plane normal direction
    pprime = np.cross(loc - vlocs[0], loc - vlocs[1])
    # Normalize this direction
    pnorm = pprime / np.linalg.norm(pprime)
    # Create the edge info dictionary
    edge_info = {'loc': loc, 'rad': rad, 'loc2': loc2, 'rad2': rad2, 'vdist': vdist, 'vnorm': vnorm, 'vmid': vmid,
                 'pnorm': pnorm, 'check': False, 'outside': False, 'case': None, 'dnorm': None, 'dnorm0': None,
                 'dnorm1': None, 'vmid0': None, 'vmid1': None, 'pa': None, 'pa0': None, 'pa1': None}
    # Find the vector perpendicular to the plane normal and the normal of the two vertex points
    dnorm = np.cross(vnorm, pnorm)

    # In the case that it is a case 1 or case 2 edge,

    # Set up the location verified variables
    loc_verified, loc2_verified = False, False
    # First get the loc box
    loc_box = box_search(loc)
    # Make sure the box for the location of the edge is not too far out of the boundary
    if loc_box is not None:
        # Get the surrounding balls for the edge sphere
        loc_balls = [_ for _ in get_balls(loc_box, rad) if _ not in eballs]
        # Verify if the edge
        if verify_site(loc, rad, np.array([locs[_] for _ in loc_balls]), np.array([rads[_] for _ in loc_balls])):
            loc_verified = True

    # Gotta check first
    if loc2 is not None:
        # If loc2 is not None, we need to verify that as well
        loc2_box = box_search(loc2)
        # Make sure the box for the 2nd location of the edge is not too far out of the boundary
        if loc2_box is not None:
            # Get the surrounding balls for the edge sphere
            loc2_balls = [_ for _ in get_balls(loc2_box, rad2) if _ not in eballs]
            # Verify if the edge
            if verify_site(loc2, rad2, np.array([locs[_] for _ in loc2_balls]), np.array([rads[_] for _ in loc2_balls])):
                loc2_verified = True

    # If there is no 2nd location, we have a case 1 or 2.
    if loc2 is None:
        # set the variable telling us if the edge is toward or away from the center
        dir_away = False
        # Check the direction of dnorm and if it is facing the edge center or not
        if np.dot(dnorm, loc - vmid) < 0:
            dir_away = True
        # First check the doublet case
        if edub:
            # Revert to the location based checking where the edge loc is closer to the verts than they are to eachother
            if calc_dist(loc, vlocs[0]) > vdist or calc_dist(loc, vlocs[1]) > vdist:
                # Set the case
                edge_info['case'] = '6'
                # Turn the dnorm away from the center
                if not dir_away:
                    dnorm = -dnorm
            else:
                if dir_away:
                    dnorm = -dnorm
        # If the location is verified it is a case 1 edge
        elif loc_verified:
            # Set the case variable
            edge_info['case'] = '1'
            if dir_away:
                dnorm = -dnorm

        else:
            # Set the case variable
            edge_info['case'], edge_info['outside'] = '2', True
            # The center is outside so we need to set the direction opposite the direction of the center
            if not dir_away:
                dnorm = -dnorm
        # Set the edge info values
        edge_info['dnorm'] = dnorm
        # Return the information
        return edge_info

    # Check if either is not verified making it a case 3 situation
    if loc_verified != loc2_verified:
        # Set the case
        edge_info['case'] = '3'
        # Point towards the correct location
        point_towards = loc
        if loc2_verified:
            point_towards = loc2

        ####### Insert Split Hereeeeeeee ########

        # Check the direction of dnorm
        if np.dot(dnorm, point_towards - vmid) < 0:
            # Flip dnorm
            dnorm = -dnorm
        # Set the edge info values
        edge_info['dnorm'] = dnorm
        # Return the information
        return edge_info

    # If neither locations are verified
    if not loc_verified and not loc2_verified:
        # Set the cas variable
        edge_info['case'], edge_info['outside'] = '4', True
        # If both locs are outside the vertices we point away from the loc
        if np.dot(dnorm, loc - vmid) > 0:
            # Flip the dnorm value
            dnorm = - dnorm
        # Set the edge info values
        edge_info['dnorm'] = dnorm

        # Return the information
        return edge_info

    # At this point we have an ellipse edge and we have both locs verifiable. This is worst case and the edge will need
    # to be split into thirds. The first will be between the vertex closest to ec1 and ec1, the next will be between ec1
    # and ec2 and the last will be between ec2 and the vertex closest to ec2

    # Mark the case
    edge_info['case'] = '5'
    print('case 5: {}'.format(eballs))

    # First swap the locs if needed
    if calc_dist(edge_info['loc'], vlocs[1]) < calc_dist(edge_info['loc'], vlocs[0]):
        edge_info['loc'], edge_info['loc2'] = edge_info['loc2'], edge_info['loc']

    # Get the direction for the first sub_edge
    vdir0 = edge_info['loc'] - vlocs[0]
    # calculate the distance between the points
    vdist0 = np.linalg.norm(vdir0)
    # Get the normal to this
    vnorm0 = vdir0 / vdist0
    # Get the perpendicular guy to this and the plane
    dnorm0 = np.cross(vnorm0, pnorm)
    # Get the middle of the two
    vmid0 = vlocs[0] + 0.5 * vdist0 * vnorm0
    # Check the direction
    if np.dot(edge_info['loc2'] - vmid0, dnorm0) > 0:
        dnorm0 = - dnorm0
    # Set the edge_info values
    edge_info['dnorm0'], edge_info['vmid0'], edge_info['vnorm0'], edge_info['vdist0'] = dnorm0, vmid0, vnorm0, vdist0
    # Set the pa
    edge_info['pa0'] = vmid0 - 0.5 * vdist0 * dnorm0

    # Get the direction for the first sub_edge
    vdir = edge_info['loc2'] - edge_info['loc']
    # calculate the distance between the points
    vdist = np.linalg.norm(vdir)
    # Get the normal to this
    vnorm = vdir / vdist
    # Get the perpendicular guy to this and the plane
    dnorm = np.cross(vnorm, pnorm)
    # Get the middle of the two
    vmid = edge_info['loc'] + 0.5 * vdist * vnorm
    # Check the direction
    if np.dot(vlocs[0] - vmid, dnorm) > 0:
        dnorm = - dnorm
    # Set the edge_info values
    edge_info['dnorm'], edge_info['vmid'], edge_info['vnorm'], edge_info['vdist'] = dnorm, vmid, vnorm, vdist
    # Set the pa
    edge_info['pa'] = vmid - 0.5 * vdist * dnorm

    # Get the direction for the first sub_edge
    vdir1 = vlocs[1] - edge_info['loc2']
    # calculate the distance between the points
    vdist1 = np.linalg.norm(vdir1)
    # Get the normal to this
    vnorm1 = vdir1 / vdist1
    # Get the perpendicular guy to this and the plane
    dnorm1 = np.cross(vnorm1, pnorm)
    # Get the middle of the two
    vmid1 = edge_info['loc2'] + 0.5 * vdist1 * vnorm1
    # Check the direction
    if np.dot(edge_info['loc'] - vmid1, dnorm1) > 0:
        dnorm1 = - dnorm1
    # Set the edge_info values
    edge_info['dnorm1'], edge_info['vmid1'], edge_info['vnorm1'], edge_info['vdist1'] = dnorm1, vmid1, vnorm1, vdist1
    # Set the pa
    edge_info['pa1'] = vmid1 - 0.5 * vdist1 * dnorm1

    # Return the information
    return edge_info


def calc_edge_dir(locs, rads, eballs, vlocs, edub=False):
    """
    Determines the edge type and calculates direction vectors for edge point generation.

    This function analyzes the geometric configuration of an edge between two vertices to:
    1. Identify the edge type based on the relative positions of vertices and their connecting circles
    2. Calculate the appropriate direction vectors needed to generate points along the edge

    Parameters:
    -----------
    locs : list of numpy.ndarray
        List of ball center coordinates [x, y, z] for all balls in the system
    rads : list of float
        List of radii for all balls in the system
    eballs : list of int
        Indices of the two balls forming the edge
    vlocs : list of numpy.ndarray
        Vertex locations [x, y, z] for the edge endpoints
    edub : bool, optional
        Flag indicating if this is a double edge case (default: False)

    Returns:
    --------
    dict
        Dictionary containing edge information including:
        - 'loc': Center point of the edge circle
        - 'rad': Radius of the edge circle
        - 'loc2': Optional second center point for double edge cases
        - 'rad2': Optional second radius for double edge cases
        - 'vdist': Distance between vertices
        - 'vnorm': Normalized vector between vertices
        - 'vmid': Midpoint between vertices
        - 'pnorm': Normal vector to the projection plane
        - Additional geometric parameters for edge point generation
    """
    # Calculate the circle
    circ = calc_circ(*[locs[_] for _ in eballs], *[rads[_] for _ in eballs], return_both=True)
    # Set up the loc2 and rad2 variables
    loc2, rad2 = None, None
    # Check the number of returned items
    if len(circ) == 2:
        loc, rad = circ
    elif len(circ) == 4:
        loc, rad, loc2, rad2 = circ
    else:
        return None
    # Calculate the distance between the vertices
    vdist = np.sqrt(sum([np.square(vlocs[0][i] - vlocs[1][i]) for i in range(3)]))
    # Get the center point of the vertices
    vdir = vlocs[1] - vlocs[0]
    # Normalize the vertex vector
    vnorm = vdir / vdist
    # Get the halfway point
    vmid = vlocs[0] + 0.5 * vdist * vnorm
    # Find the plane normal direction
    pprime = np.cross(loc - vlocs[0], loc - vlocs[1])
    # Normalize this direction
    pnorm = pprime / np.linalg.norm(pprime)
    # Create the edge info dictionary
    edge_info = {'loc': loc, 'rad': rad, 'loc2': loc2, 'rad2': rad2, 'vdist': vdist, 'vnorm': vnorm, 'vmid': vmid,
                 'pnorm': pnorm, 'check': False, 'outside': False, 'case': None, 'dnorm': None, 'dnorm0': None,
                 'dnorm1': None, 'vmid0': None, 'vmid1': None, 'pa': None, 'pa0': None, 'pa1': None}
    # Find the vector perpendicular to the plane normal and the normal of the two vertex points
    dnorm = np.cross(vnorm, pnorm)

    # Check the type of circle
    if loc2 is None:
        # Calculate the relevant distances and sort them small to large
        v0_dist, v1_dist = sorted([calc_dist(vlocs[0], loc), calc_dist(vlocs[1], loc)])
        # Calculate the distance between the center to the edge center
        # vmid_dist = calc_dist(vmid, loc)
        # # Set up the tracking variables
        # if v1_dist <
        # Check the orientation
        # Determine if the center is outside the vertices by checking the distance between the vertices and the center
        if v1_dist > vdist:
            # The center is outside so we need to set the direction opposite the direction of the center
            if np.dot(dnorm, loc - vmid) > 0:
                dnorm = - dnorm
                edge_info['case'] = '1a'
            else:
                edge_info['case'] = '1b'
            edge_info['outside'] = True
        # The center is inside the vertices we want to point dnorm towards the center
        else:
            if np.dot(dnorm, loc - vmid) < 0:
                edge_info['case'] = '1c'
                dnorm = - dnorm
            else:
                edge_info['case'] = '1d'
        # Set the edge info values
        edge_info['dnorm'] = dnorm
        # Set the pa
        edge_info['pa'] = vmid - 0.5 * vdist * dnorm
        # Return the information
        return edge_info

    # If the locations of the circle are both outside the vertices we have a simple aim away case
    if all([any([np.sqrt(sum([np.square(vlocs[j][i] - _[i]) for i in range(3)])) > vdist for j in range(2)]) for _ in [loc, loc2]]):
        # If both locs are outside the vertices we point away from the loc
        if np.dot(dnorm, loc - vmid) > 0:
            # Flip the dnorm value
            edge_info['case'] = '2a'
            dnorm = - dnorm
        else:
            edge_info['case'] = '2b'
        # Set the edge info values
        edge_info['dnorm'], edge_info['outside'] = dnorm, True
        # Calculate the distance between the middle of the vertices and the two locs
        loc_vmid_dist = calc_dist(vmid, loc)
        loc2_vmid_dist = calc_dist(vmid, loc2)
        # If the loc2 distance is closer swap them boys
        if loc2_vmid_dist < loc_vmid_dist:
            edge_info['loc'], edge_info['rad'], edge_info['loc2'], edge_info['rad2'] = (
                edge_info['loc2'], edge_info['rad2'], edge_info['loc'], edge_info['rad'])
        # Set the pa
        edge_info['pa'] = vmid - 0.5 * vdist * dnorm
        # Return the information
        return edge_info

    # First test loc2 to see if it overlaps with any other balls. Best case bc rad2 > rad so less likely
    # Get the loc2 box for getting ready to gather the balls around it
    loc2_box = box_search(loc2)
    # If we dont get a box for loc2 its out of bounds
    if loc2_box is not None:
        # Gather the balls within the range of the loc2
        loc2_balls = [_ for _ in get_balls(loc2_box, rad2) if _ not in eballs]
        # Verify the loc2. If the loc2 interacts with another ball, then the edge needs to be projected toward loc
        if not verify_site(loc2, rad2, np.array([locs[_] for _ in loc2_balls]), np.array([rads[_] for _ in loc2_balls])):
            # If dnorm is facing loc, return it as normal because it cant be facing loc2
            if np.dot(dnorm, loc - vmid) < 0:
                # Flip the dnorm value because it is facing away from loc
                edge_info['case'] = '3a'
                # print("Case 3a: {}".format(eballs))
                dnorm = - dnorm
            else:
                edge_info['case'] = '3b'
                # print("Case 3b: {}".format(eballs))
            # Set the edge info values
            edge_info['dnorm'] = dnorm
            # Set the pa
            edge_info['pa'] = vmid - 0.5 * vdist * dnorm
            # Return the information
            return edge_info
    else:
        # If dnorm is facing loc, flip dnorm since loc is not verified and therefore not in the edge
        if np.dot(dnorm, loc - vmid) < 0:
            edge_info['case'] = '4a1'
            # print("Case 4a1: {}".format(eballs))
            # Flip the dnorm value because it is facing away from loc
            dnorm = - dnorm
        else:
            edge_info['case'] = '4b1'
            # print("Case 4b1: {}".format(eballs))

        # Set the edge info values
        edge_info['dnorm'] = dnorm
        # If the loc2 distance is closer swap them boys
        if calc_dist(edge_info['loc'], vmid) < calc_dist(edge_info['loc2'], vmid):
            edge_info['loc'], edge_info['rad'], edge_info['loc2'], edge_info['rad2'] = (
                edge_info['loc2'], edge_info['rad2'], edge_info['loc'], edge_info['rad'])
        # Set the pa
        edge_info['pa'] = vmid - 0.5 * vdist * dnorm
        # Return the information
        return edge_info

    # Next test loc to see if it overlaps with any other balls. 2nd Best case
    # Get the loc box for getting ready to gather the balls around it
    loc_box = box_search(loc)
    # If we dont get a box for loc it is out of bounds
    if loc_box is not None:
        # Gather the balls within the range of the loc2
        loc_balls = [_ for _ in get_balls(loc_box, rad2) if _ not in eballs]
        # Verify the loc. If the loc2 interacts with another ball, then the edge needs to be projected toward loc
        if not verify_site(loc, rad2, np.array([locs[_] for _ in loc_balls]), np.array([rads[_] for _ in loc_balls])):
            # If dnorm is facing loc, flip dnorm since loc is not verified and therefore not in the edge
            if np.dot(dnorm, loc - vmid) > 0:
                edge_info['case'] = '4a'
                # print("Case 4a: {}".format(eballs))
                # Flip the dnorm value because it is facing away from loc
                dnorm = - dnorm
            else:
                edge_info['case'] = '4b'
                # print("Case 4b: {}".format(eballs))

            # Set the edge info values
            edge_info['dnorm'] = dnorm
            # If the loc2 distance is closer swap them boys
            if calc_dist(edge_info['loc'], vmid) < calc_dist(edge_info['loc2'], vmid):
                edge_info['loc'], edge_info['rad'], edge_info['loc2'], edge_info['rad2'] = (
                    edge_info['loc2'], edge_info['rad2'], edge_info['loc'], edge_info['rad'])
            # Set the pa
            edge_info['pa'] = vmid - 0.5 * vdist * dnorm
            # Return the information
            return edge_info
    else:
        # If dnorm is facing loc, return it as normal because it cant be facing loc2
        if np.dot(dnorm, loc - vmid) < 0:
            # Flip the dnorm value because it is facing away from loc
            edge_info['case'] = '3a1'
            # print("Case 3a1: {}".format(eballs))
            dnorm = - dnorm
        else:
            edge_info['case'] = '3b1'
            # print("Case 3b1: {}".format(eballs))
        # Set the edge info values
        edge_info['dnorm'] = dnorm
        # Set the pa
        edge_info['pa'] = vmid - 0.5 * vdist * dnorm
        # Return the information
        return edge_info

    # At this point we have an ellipse edge and we have both locs verifiable. This is worst case and the edge will need
    # to be split into thirds. The first will be between the vertex closest to ec1 and ec1, the next will be between ec1
    # and ec2 and the last will be between ec2 and the vertex closest to ec2

    # Mark the case
    edge_info['case'] = '5'
    # print('case 5: {}'.format(eballs))

    # First swap the locs if needed
    if calc_dist(edge_info['loc'], vlocs[1]) < calc_dist(edge_info['loc'], vlocs[0]):
        edge_info['loc'], edge_info['loc2'] = edge_info['loc2'], edge_info['loc']

    # Get the direction for the first sub_edge
    vdir0 = edge_info['loc'] - vlocs[0]
    # calculate the distance between the points
    vdist0 = np.linalg.norm(vdir0)
    # Get the normal to this
    vnorm0 = vdir0 / vdist0
    # Get the perpendicular guy to this and the plane
    dnorm0 = np.cross(vnorm0, pnorm)
    # Get the middle of the two
    vmid0 = vlocs[0] + 0.5 * vdist0 * vnorm0
    # Check the direction
    if np.dot(edge_info['loc2'] - vmid0, dnorm0) > 0:
        dnorm0 = - dnorm0
    # Set the edge_info values
    edge_info['dnorm0'], edge_info['vmid0'], edge_info['vnorm0'], edge_info['vdist0'] = dnorm0, vmid0, vnorm0, vdist0
    # Set the pa
    edge_info['pa0'] = vmid0 - 0.5 * vdist0 * dnorm0

    # Get the direction for the first sub_edge
    vdir = edge_info['loc2'] - edge_info['loc']
    # calculate the distance between the points
    vdist = np.linalg.norm(vdir)
    # Get the normal to this
    vnorm = vdir / vdist
    # Get the perpendicular guy to this and the plane
    dnorm = np.cross(vnorm, pnorm)
    # Get the middle of the two
    vmid = edge_info['loc'] + 0.5 * vdist * vnorm
    # Check the direction
    if np.dot(vlocs[0] - vmid, dnorm) > 0:
        dnorm = - dnorm
    # Set the edge_info values
    edge_info['dnorm'], edge_info['vmid'], edge_info['vnorm'], edge_info['vdist'] = dnorm, vmid, vnorm, vdist
    # Set the pa
    edge_info['pa'] = vmid - 0.5 * vdist * dnorm

    # Get the direction for the first sub_edge
    vdir1 = vlocs[1] - edge_info['loc2']
    # calculate the distance between the points
    vdist1 = np.linalg.norm(vdir1)
    # Get the normal to this
    vnorm1 = vdir1 / vdist1
    # Get the perpendicular guy to this and the plane
    dnorm1 = np.cross(vnorm1, pnorm)
    # Get the middle of the two
    vmid1 = edge_info['loc2'] + 0.5 * vdist1 * vnorm1
    # Check the direction
    if np.dot(edge_info['loc'] - vmid1, dnorm1) > 0:
        dnorm1 = - dnorm1
    # Set the edge_info values
    edge_info['dnorm1'], edge_info['vmid1'], edge_info['vnorm1'], edge_info['vdist1'] = dnorm1, vmid1, vnorm1, vdist1
    # Set the pa
    edge_info['pa1'] = vmid1 - 0.5 * vdist1 * dnorm1

    # Return the information
    return edge_info


if __name__ == '__main__':
    ball_locs = [0, 4, 0], [0, 0, 0.4], [0, -4, 0]
    ball_rads = 2, 1, 2
    plot_balls(ball_locs, ball_rads)
    edge_vals = calc_edge_dir(ball_locs, ball_rads, [0, 1, 2], [np.array([0.4, 0, 4]), np.array([0.4, 0, -4])])
    print(edge_vals)


