from vorpy.src.calculations import calc_com
from vorpy.src.calculations import calc_dist
from vorpy.src.calculations import box_search
from vorpy.src.calculations import get_balls
from vorpy.src.calculations import calc_circ
from vorpy.src.network.slow import find_site_container_slow
from vorpy.src.network.fast import find_site_container
from vorpy.src.network.slow import find_site
from vorpy.src.calculations import verify_site


def find_v0(locs, rads, b_verts, max_vert, net_type, b0=None, group_ndxs=None, metrics=None, vert_ndxs=None,
            group_box=None, box=None):
    """
    Finds the initial vertex (v0) in a network by identifying a valid set of balls that form a verified vertex.

    This function searches for a valid starting vertex by:
    1. Locating an initial ball (b0) either from a specified index or by searching nearby balls
    2. Finding nearby balls (b1) to form potential edges
    3. Verifying that the combination of balls can form a valid vertex according to the network type

    Parameters
    ----------
    locs : list of numpy.ndarray
        List of ball locations in 3D space
    rads : list of float
        List of ball radii
    b_verts : dict
        Dictionary mapping ball indices to their vertices
    max_vert : float
        Maximum distance to search for vertices
    net_type : str
        Type of network ('aw', 'pow', or 'prm')
    b0 : int, optional
        Index of initial ball to start search from
    group_ndxs : list, optional
        List of ball indices in the group to constrain search
    metrics : dict, optional
        Dictionary for storing performance metrics
    vert_ndxs : list, optional
        List of existing vertex indices
    group_box : list, optional
        Bounding box for group search
    box : list, optional
        Overall search box boundaries

    Returns
    -------
    tuple or None
        If a valid vertex is found, returns a tuple containing:
        - List of ball indices forming the vertex
        - Vertex location
        - Vertex radius
        Returns None if no valid vertex is found

    Notes
    -----
    - The search is performed within specified boundaries and can be constrained to a particular group of balls
    - For group-constrained searches, only balls within the group are considered
    - The function uses a progressive search strategy, starting with nearby balls and expanding outward
    - Vertex verification depends on the network type specified
    """
    if vert_ndxs is None:
        vert_ndxs = []
    # Check to see if we need a group ball's box
    if b0 is not None:
        my_box = box_search(locs[b0])
    elif group_box is not None:
        # Get the center of the group_box
        my_box = box_search([0.5 * abs(group_box[1][i] - group_box[0][i]) + group_box[0][i] for i in range(3)])
    elif group_ndxs is not None:
        # Get the box for the
        my_box = box_search(locs[group_ndxs[int(len(group_ndxs) / 2)]])
    else:
        # Find the middle sub_box of the set of boxes and
        my_box = box_search(locs[int(len(locs) / 2)])

    # If we still haven't found an a0
    if b0 is None:
        # Reset the a0 variables
        b0s = []
        inc = 0
        # Keep searching boxes until we find an ball
        while len(b0s) < 1:
            b0s = get_balls([my_box], inc)
            if group_ndxs is not None:
                b0s = [_ for _ in b0s if _ in group_ndxs and len(b_verts[_]) == 0]
            inc += 1
        # Pull an ball from the balls list
        b0 = b0s[0]
    # Reset the a1 variables
    b1s = []
    inc = 0
    # Get the 5 closest balls to a0
    while len(b1s) < 5:
        b1s = get_balls([my_box], inc)
        inc += 1
    # Sort the a1s
    b1_dists = [calc_dist(locs[b1], locs[b0]) - (rads[b0] + rads[b1]) for b1 in b1s]
    _, b1s_sorted = zip(*sorted(zip(b1_dists, b1s), key=lambda x: x[0]))
    b1s_sorted = [_ for _ in b1s_sorted if _ != b0][:5]
    # Set up the a2s lists
    b2s, j = [], 0
    # Check the a1s for verifiable
    while len(b1s_sorted) > 0:
        # Get the a1
        b1 = b1s_sorted.pop(0)
        # Find the center of mass for a0 and a1 locations
        b0_b1_com = calc_com([locs[b0], locs[b1]])

        inc = 0
        # Find a2s near a0 and a1
        while len(b2s) < 5:
            b2s = get_balls(box_search(b0_b1_com), inc)
            inc += 1
        b2s = [_ for _ in b2s if _ not in {b0, b1}]

        my_circs = []
        # Check each of the combinations for this a1
        for b2 in b2s:
            # Set up the circle
            circle = [b0, b1, b2]
            circy_werky = (circle, calc_circ(*[locs[_] for _ in circle], *[rads[_] for _ in circle]))
            if circy_werky[1] is not None:
                my_circs.append(circy_werky)
        my_circs.sort(key=lambda x: abs(x[1][1]))
        for circ in my_circs:
            # Try to create a vertex
            if net_type in ['prm', 'pow']:
                my_vert = find_site_container(circ[0], locs=locs, rads=rads, b_verts=b_verts, vert_ndxs=vert_ndxs,
                                              max_vert=max_vert, net_type=net_type, group_ndxs=group_ndxs,
                                              metrics=metrics, box=box)
            else:
                my_vert = find_site_container_slow(circ[0], locs=locs, rads=rads, b_verts=b_verts, vert_ndxs=vert_ndxs,
                                                   max_vert=max_vert / 10, net_type=net_type, group_ndxs=group_ndxs,
                                                   metrics=metrics, box=box)
            # Check for a real site that is not a doublet
            if my_vert is not None:
                if net_type == 'aw':
                    if my_vert[0]['loc'] is not None and my_vert[0]['loc2'] is None:
                        if box is not None and any(
                                [box[0][k] > my_vert[0]['loc'][k] or my_vert[0]['loc'][k] > box[1][k] for k in range(3)]):
                            continue
                        return my_vert[0]
                return my_vert[0]
        j += 1


# still needs work


def find_v0_old(net, b_locs, b_rads, a0=None, group_balls=None):
    """
    Finds v0 using the ball finding functions to find a real verified site
    :param net: Network object to check from
    :param a0: The ball to seed from
    :param group_balls: List of balls for the building group based networks
    :return: V0 vertex
    """
    # Check to see if we need a group ball's box
    if a0 is not None:
        my_box = box_search(b_locs[a0])
    elif group_balls is not None:
        my_box = box_search(b_locs[group_balls[0]])
    else:
        # Find the middle sub_box of the set of boxes and
        mid = len(net.sub_boxes) // 2
        my_box = [mid, mid, mid]
    if a0 is None:
        a0s = []
        inc = 0
        # Keep grabbing balls until we have enough to get the current a0 increment
        while len(a0s) < 5:
            a0s = get_balls([my_box], inc)
            inc += 1
        # Pull an ball from the balls list
        a0 = a0s[0]
    a1s = []
    inc = 0
    # Get the 5 closest balls to a0
    while len(a1s) < 5:
        a1s = get_balls([my_box], inc)
        inc += 1
    # Set up the a2s lists
    a2s, j = [], 0
    # Check the a1s for verifiable
    while len(a1s) > 0:
        # Get the a1
        a1 = a1s.pop()
        # Add the circle check
        a2s.append([])
        inc = 0
        # Get the 20 closest balls to a0 and the current a1
        if len(b_locs) < 20:
            a2s[j] = [i for i in range(len(b_locs))]
        else:
            while len(a2s[j]) < 20:
                a2s[j] = get_balls([my_box], inc)
                inc += 1
        # Set up verified circles list for this a1
        verified_circles = []
        # Check each of the combinations for this a1
        for a2 in a2s[j]:
            # Use an edge object as a vehicle for calculating and verifying the inscribed circle
            circ = calc_circ(*[_.loc for _ in [a0, a1, a2]], *[_.rad for _ in [a0, a1, a2]])
            eloc, erad = None, None
            if circ is not None:
                eloc, erad = circ
            # If a circle can be made and the site does not overlap with any other balls, add it to the list
            if eloc is not None and erad < net.settings['max_vert'] and verify_site(eloc, erad, [a0, a1, a2], net,
                                                                                    net.settings['net_type']):
                verified_circles.append([a0, a1, a2])
        # Try to make a verified v0 site with the verified circles
        for circle in verified_circles:
            # Try to create a vertex
            my_vert = find_site(net, circle, group_ndxs=group_balls)
            # Check for a real site
            if my_vert is not None and my_vert[0].loc is not None:
                return my_vert[0]
        j += 1

