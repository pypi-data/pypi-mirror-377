"""
Module to search for the supergroup symmetry
"""

import functools
import itertools
import operator
from copy import deepcopy

import numpy as np
import pymatgen.analysis.structure_matcher as sm
from numpy.random import Generator
from scipy.optimize import minimize

import pyxtal.symmetry as sym
from pyxtal.lattice import Lattice
from pyxtal.operations import apply_ops, get_best_match
from pyxtal.wyckoff_site import atom_site
from pyxtal.wyckoff_split import wyckoff_split

ALL_SHIFTS = np.array(
    [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1],
        [0, 1, 1],
        [1, 1, 0],
        [1, 0, 1],
        [1, 1, 1],
    ]
)


def write_poscars(H_struc, G_struc, mappings, splitters, wyc_sets, N_images=3):
    """
    Write the intermediate POSCARs between H and G structure.

    The key is to continuously change G to subgroup representations with zero
    displacements. Finally, call ``write_poscars_intermediate``.

    Args:
        H_struc: PyXtal low symmetry structure
        G_struc: PyXtal high symmetry structure
        mappings: List of atomic mappings
        splitters: List of splitter objects
        wyc_sets: List of wyc_set transformations
        N_images: Number of intermediate structures between H and G. Default is 3.

    Returns:
        List of POSCARs between H and G structure.
    """
    raise NotImplementedError


def new_structure(struc, refs):
    """
    Check if struc is already in the reference solutions.
    """
    g1 = struc.group.number
    pmg1 = struc.to_pymatgen()
    for ref in refs:
        g2 = ref.group.number
        if g1 == g2:
            pmg2 = ref.to_pymatgen()
            if sm.StructureMatcher().fit(pmg1, pmg2):
                return False
    return True


def new_path(path, paths):
    """
    Check if it is a new path.
    """
    return all(path[: len(ref)] != ref for ref in paths)


def find_mapping_per_element(sites1, sites2):
    """
    Search for all mappings for a given splitter.

    Args:
        sites1 (list): e.g., l layer ['4a', '8b', '4c']
        sites2 (list): e.g., 2 layers [['4a'], ['8b', '4c']]

    Returns:
        unique solutions: e.g. 3 layers: [[[0], [1,2]]]
    """

    unique_letters = list(set(sites1))
    site1_letter_indices = [[i for i, x in enumerate(sites1) if x == letter] for letter in unique_letters]
    site2_letter_bins = [[unique_letters.index(x) for x in lbin] for lbin in sites2]

    combo_list = []
    for s in site2_letter_bins:
        ls = list(set(s))
        rs = [s.count(r) for r in ls]
        p = []
        for i, l in enumerate(ls):
            combo = itertools.combinations(site1_letter_indices[l], rs[i])
            combo = [list(x) for x in combo]
            p.append(deepcopy(combo))
        pr = p[0]
        for i in range(1, len(p)):
            pr = itertools.product(pr, p[i])
            pr = [functools.reduce(operator.iadd, list(x), []) for x in pr]
        combo_list.append(pr)
    unique_solutions = [[x] for x in combo_list[0]]
    for i in range(1, len(combo_list)):
        unique_solutions = [
            [*x, y]
            for x in unique_solutions
            for y in combo_list[i]
            if len(set(functools.reduce(operator.iadd, x, [])).intersection(y)) == 0
        ]
    return unique_solutions


def find_mapping(atom_sites, splitter):
    """
    Search for all mappings for a given splitter.

    Args:
        atom_sites: list of wp object
        splitter: wp_splitter object

    Returns:
        unique solutions
    """
    eles = {site.specie for site in atom_sites}

    # loop over the mapping for each element
    # then propogate the possible mapping via itertools.product
    lists = []

    for ele in eles:
        # ids of atom sites
        site_ids = [id for id, site in enumerate(atom_sites) if site.specie == ele]

        # ids to be assigned
        wp2_ids = [id for id, e in enumerate(splitter.elements) if e == ele]

        letters1 = [atom_sites[id].wp.letter for id in site_ids]
        letters2 = []

        for id in wp2_ids:
            wp2 = splitter.wp2_lists[id]
            letters2.append([wp.letter for wp in wp2])
        # print(ele, letters1, letters2)

        res = find_mapping_per_element(letters1, letters2)
        lists.append(res)

    # resort the mapping
    mappings = list(itertools.product(*lists))
    ordered_mappings = []

    for mapping in mappings:
        ordered_mapping = [None] * len(splitter.wp2_lists)

        for i, ele in enumerate(eles):
            site_ids = [id for id, site in enumerate(atom_sites) if site.specie == ele]
            count = 0

            for j, wp2 in enumerate(splitter.wp2_lists):
                if splitter.elements[j] == ele:
                    ordered_mapping[j] = [site_ids[m] for m in mapping[i][count]]
                    count += 1
        # print("res", ordered_mapping)
        ordered_mappings.append(ordered_mapping)

    return ordered_mappings


def search_G1(G, rot, tran, pos, wp1, op):
    """
    Search the best matched position in the G1 basis.

    Args:
        G: Target space group object
        rot: Rotation matrix (3x3)
        tran: Translation vector (1x3)
        pos: Starting position
        wp1: Wyckoff position symmetry
        op: Symmetry operation

    Returns:
        tuple: (closest_position, distance)
            - closest_position: The best matched position in G1 basis
            - distance: Distance between original and matched positions
    """

    shifts = ALL_SHIFTS if np.linalg.det(rot) < 1 else np.array([[0, 0, 0]])

    diffs = []
    coords = []
    # loop over all nearby translations
    for shift in shifts:
        res = np.dot(rot, pos + shift) + tran.T
        tmp = sym.search_cloest_wp(G, wp1, op, res)
        diff = res - tmp
        diff -= np.rint(diff)
        dist = np.linalg.norm(diff)
        diffs.append(dist)
        coords.append(tmp)
        if dist < 1e-1:
            break
    # choose the one returns minimum difference
    diffs = np.array(diffs)
    minID = np.argmin(diffs)
    tmp = coords[minID]
    tmp -= np.rint(tmp)
    return tmp, np.min(diffs)


def search_G2(rot, tran, pos1, pos2, cell=None):
    """
    Search the best matched position in G2 basis.

    Args:
        rot: Rotation matrix (3x3)
        tran: Translation vector (1x3)
        pos1: Position in G1
        pos2: Reference position in G2
        cell: Unit cell matrix (3x3), optional

    Returns:
        tuple: (pos, dist)
            - pos: Matched position in G2 basis
            - dist: Relative distance between matched positions
    """

    pos1 -= np.rint(pos1)
    shifts = ALL_SHIFTS

    dists = []
    for shift in shifts:
        res = np.dot(rot, pos1 + shift + tran.T)
        diff = res - pos2
        diff -= np.rint(diff)
        dist = np.linalg.norm(diff)
        dists.append(dist)
        if dist < 1e-1:
            break
    dists = np.array(dists)
    dist = np.min(dists)
    shift = shifts[np.argmin(dists)]
    pos = np.dot(rot, pos1 + shift + tran.T)

    diff = pos - pos2
    diff -= np.rint(diff)

    if cell is not None:
        diff = np.dot(diff, cell)

    dist = np.linalg.norm(diff)

    return pos, dist


def find_xyz(G2_op, coord, quadrant=None):
    """
    Finds the x,y,z free parameter values for positions in the G_2 basis.

    Args:
        G2_op: a symmetry operation in G2
        coord: the coordinate that matches G2_op
        quadrant: a 3 item list (ex:[1,1,-1]) that contains information on the
            orientation of the molecule

    Returns:
        G2_holder: x,y,z parameters written in the G2 basis
    """
    if quadrant is None:
        quadrant = [0, 0, 0]
    if np.all(quadrant == [0, 0, 0]):
        for i, n in enumerate(coord):
            if n >= 0.0:
                quadrant[i] = 1
            else:
                quadrant[i] = -1

    # prepare the rotation matrix and translation vector seperately
    G2_holder = [1, 1, 1]
    G2_op = np.array(G2_op.as_dict()["matrix"])
    rot_G2 = G2_op[:3, :3].T
    tau_G2 = G2_op[:3, 3]
    b = coord - tau_G2
    for k in range(3):
        b[k] = b[k] % quadrant[k]

    # eliminate any unused free parameters in G2
    # The goal is to reduce the symmetry operations to be a full rank matrix
    # any free parameter that is not used has its spot deleted from the rot+trans
    for i, x in reversed(list(enumerate(rot_G2))):
        if set(x) == {0.0}:
            G2_holder[i] = 0
            rot_G2 = np.delete(rot_G2, i, 0)
            quadrant = np.delete(quadrant, i)

    # eliminate any leftover empty rows to have fulll rank matrix
    rot_G2 = rot_G2.T
    for i, x in reversed(list(enumerate(rot_G2))):
        if set(x) == {0.0}:
            rot_G2 = np.delete(rot_G2, i, 0)
            b = np.delete(b, i)
    while len(rot_G2) != 0 and len(rot_G2) != len(rot_G2[0]):
        rot_G2 = np.delete(rot_G2, len(rot_G2) - 1, 0)
        b = np.delete(b, len(b) - 1)

    # Later must add Schwarz Inequality check to elininate any dependent vectors
    # solves a linear system to find the free parameters
    if set(G2_holder) == {0.0}:
        return np.array(G2_holder)
    else:
        try:
            G2_basis_xyz = np.linalg.solve(rot_G2, b)
            for i in range(len(quadrant)):
                G2_basis_xyz[i] = G2_basis_xyz[i] % quadrant[i]
            # print("!ST G2 HOLDER")
            for i in range(G2_holder.count(1)):
                G2_holder[G2_holder.index(1)] = G2_basis_xyz[i]
            # print('second G## holder')
            return np.array(G2_holder)

        except:
            raise RuntimeError("unable to find free parameters in the operation")


class supergroup:
    """
    Class to find the structure with supergroup symmetry

    Args:
        struc: pyxtal structure
        G: target supergroup number
    """

    def __init__(self, struc, G, random_state=None):
        # initilize the necesary parameters
        self.solutions = []
        self.error = True
        self.G = sym.Group(G)
        group_type = "k" if self.G.point_group == struc.group.point_group else "t"
        self.group_type = group_type

        if isinstance(random_state, Generator):
            self.random_state = random_state.spawn(1)[0]
        else:
            self.random_state = np.random.default_rng(random_state)

        # list of all alternative wycsets
        strucs = struc.get_alternatives()
        for struc in strucs:
            solutions = self.G.get_splitters_from_structure(struc, group_type)
            if len(solutions) > 0:
                self.struc = struc
                self.wyc_set_id = struc.wyc_set_id
                self.elements, self.sites = struc._get_elements_and_sites()
                self.solutions = solutions
                self.cell = struc.lattice.matrix
                self.error = False
                break

    def search_supergroup(self, d_tol=0.9, max_per_G=2500, max_solutions=None):
        """
        Search for valid supergroup transition

        Args:
            d_tol (float): tolerance for atomic displacement
            max_per_G (int): maximum number of possible solution for each G
            max_solutions (int): maximum number of solutions.

        Returns:
            solutions: list of solutions with small displacements
        """
        solutions = []
        done = False
        if len(self.solutions) > 0:
            # extract the valid
            for idx, sols in self.solutions:
                if len(sols) > max_per_G:
                    print("Warning: ignore some solutions: ", len(sols) - max_per_G)
                    sols = [sols[i] for i in self.random_state.choice(len(sols), max_per_G)]
                    # sols=[(['8c'], ['4a', '4b'], ['4b', '8c', '8c'])]

                for _i, sol in enumerate(sols):
                    max_disp, trans, mapping, sp = self.calc_disps(idx, sol, d_tol * 1.1)
                    # print(i, sp.H.number, sp.G.number, sol, max_disp, mapping)
                    if max_disp < d_tol:
                        solutions.append((sp, mapping, trans, self.wyc_set_id, max_disp))
                        if max_solutions is not None and len(solutions) >= max_solutions:
                            done = True
                            break

                if done or len(solutions) > 0:
                    break
        return self.sort_solutions(solutions)

    def make_supergroup(self, solutions, show_detail=False):
        """
        Create unique supergroup structures from a list of solutions

        Args:
            solutions: list of tuples (splitter, mapping, translation, disp)
            show_detail (bool): print out the detail

        Returns:
            list of pyxtal structures
        """
        G_strucs = []
        new_sols = []
        for solution in solutions:
            (sp, mapping, translation, wyc_set_id, max_disp) = solution
            details = self.symmetrize(sp, mapping, translation)
            coords_G1, coords_G2, coords_H1, elements, ordered_mapping = details
            G_struc = self._make_pyxtal(sp, coords_G1)
            if new_structure(G_struc, G_strucs):
                if show_detail:
                    self.print_detail(solution, coords_H1, coords_G2, elements)
                G_struc.source = f"supergroup {max_disp:6.3f}"
                G_struc.disp = max_disp
                G_strucs.append(G_struc)
                new_sols.append((sp, ordered_mapping, translation, wyc_set_id, max_disp))
        return G_strucs, new_sols

    def calc_disps(self, split_id, solution, d_tol):
        """
        For a given solution, compute the minimum disp by adusting translation.

        Args:
            split_id (int): integer
            solution (list): e.g., [['2d'], ['6h'], ['2c', '6h', '12i']]
            d_tol (float): tolerance

        Returns:
            max_disp: maximum atomic displcement
            translation: overall cell translation
        """
        sites_G = []
        elements = []
        muls = []
        for i, e in enumerate(self.elements):
            sites_G.extend(solution[i])
            elements.extend([e] * len(solution[i]))
            muls.extend([int(sol[:-1]) for sol in solution[i]])

        # resort the sites_G by multiplicity, needed by the mask calculation
        ids = np.argsort(np.array(muls))
        elements = [elements[id] for id in ids]
        sites_G = [sites_G[id] for id in ids]

        splitter = wyckoff_split(self.G, split_id, sites_G, self.group_type, elements)
        mappings = find_mapping(self.struc.atom_sites, splitter)

        dists = []
        translations = []
        masks = []
        if len(mappings) > 0:
            mask = self.get_initial_mask(splitter)
            for mapping in mappings:
                dist, trans, mask = self.symmetrize_dist(splitter, mapping, mask, None, d_tol)
                dists.append(dist)
                translations.append(trans)
                masks.append(mask)

            dists = np.array(dists)
            max_disp = np.min(dists)
            id = np.argmin(dists)
            translation = translations[id]
            mask = masks[id]
            if 0.2 < max_disp < d_tol and (mask is None or len(mask) < 3):
                # optimize disp further
                def fun(translation, mapping, splitter, mask):
                    return self.symmetrize_dist(splitter, mapping, mask, translation)[0]

                res = minimize(
                    fun,
                    translations[id],
                    args=(mappings[id], splitter, mask),
                    method="Nelder-Mead",
                    options={"maxiter": 10},
                )
                if res.fun < max_disp:
                    max_disp = res.fun
                    translation = res.x
            return max_disp, translation, mappings[id], splitter
        else:
            print("bug in findding the mappings", solution)
            print(splitter.G.number, "->", splitter.H.number)
            return 1000, None, None, None

    def get_initial_mask(self, splitter):
        """
        Get the mask.
        """
        for wp2 in splitter.wp2_lists:
            for wp in wp2:
                if wp.get_dof() == 0:
                    return [0, 1, 2]
        return None

    def get_coord_H(self, splitter, id, atom_sites_H, mapping):
        """
        Extract the atomic coordinates.
        """
        # number of split sites for a given WP
        n = len(splitter.wp2_lists[id])
        if n > 1:
            letters = [atom_sites_H[mapping[id][x]].wp.letter for x in range(n)]
            letters_wp = [wp.letter for wp in splitter.wp2_lists[id]]
            seq = []
            for l in letters_wp:
                index = letters.index(l)
                seq.append(index)
                letters[index] = 0

            ordered_mapping = [mapping[id][x] for x in seq]
            # print(letters, mapping[id], '->', letters_wp, ordered_mapping)
        else:
            ordered_mapping = mapping[id]
        coord_H = [atom_sites_H[ordered_mapping[x]].position.copy() for x in range(n)]
        return np.array(coord_H), ordered_mapping

    def symmetrize_dist(self, splitter, mapping, mask, translation=None, d_tol=1.2):
        """
        For a given solution, search for the possbile supergroup structure based on a
        given ``translation`` and ``mask``.

        Args:
            splitter: Splitter object between G and H
            mapping: List of sites in H, e.g., ['4a', '8b']
            mask: If there is a need to freeze the direction
            translation: An overall shift from H to G, None or 3 vector
            d_tol: The tolerance in angstrom

        Returns:
            tuple: (max_disp, translation, mask)
                - max_disp: Maximum atomic displacement
                - translation: Cell translation vector
                - mask: Direction mask
        """

        max_disps = []
        if mask is not None and translation is not None:
            translation[mask] = 0

        for i in range(len(splitter.wp1_lists)):
            n = len(splitter.wp2_lists[i])
            coord_H, _ = self.get_coord_H(splitter, i, self.struc.atom_sites, mapping)

            if n == 1:
                res = self.symmetrize_site_single(splitter, i, coord_H[0], translation)
                (dist, _tran, _mask) = res
                if translation is None:
                    translation = _tran
                    mask = _mask
            elif n == 2:
                if splitter.group_type == "k":
                    dist = self.symmetrize_site_double_k(splitter, i, coord_H, translation)
                else:
                    dist = self.symmetrize_site_double_t(splitter, i, coord_H, translation)
            else:
                dist = self.symmetrize_site_multi(splitter, i, coord_H, translation)

            # strs = self.print_wp(splitter, i); print(strs, dist)
            if i == 0 and translation is None:
                translation = np.zeros(3)

            if dist < d_tol:
                max_disps.append(dist)
            else:
                return 10000, None, mask

        return max(max_disps), translation, mask

    def symmetrize(self, splitter, mapping, translation):
        """
        Symmetrize the structure (G) to supergroup symmetry (H)

        Args:
            splitter: Splitter object to specify the relation between G and H
            mapping: Atomic mapping between H and G
            translation: An overall shift from H to G, None or 3 vector

        Returns:
            tuple: (coords_G1, coords_G2, coords_H, elements, ordered_mapping)
                - coords_G1: Coordinates in G
                - coords_G2: Coordinates in G under the subgroup setting
                - coords_H1: Coordinates in H
                - elements: List of elements
        """
        coords_G1 = []  # position in G
        coords_G2 = []  # position in G on the subgroup bais
        coords_H = []  # position in H
        elements = []
        ordered_mapping = []

        for i, _wp1 in enumerate(splitter.wp1_lists):
            n = len(splitter.wp2_lists[i])
            coord_H, seq = self.get_coord_H(splitter, i, self.struc.atom_sites, mapping)

            if n == 1:
                res = self.symmetrize_site_single(splitter, i, coord_H[0], translation, 0)
            elif n == 2:
                if splitter.group_type == "k":
                    res = self.symmetrize_site_double_k(splitter, i, coord_H, translation, 0)
                else:
                    res = self.symmetrize_site_double_t(splitter, i, coord_H, translation, 0)
            else:
                res = self.symmetrize_site_multi(splitter, i, coord_H, translation, 0)

            coord_G1, coord_G2, coord_H = res
            coords_G1.append(coord_G1)
            coords_G2.extend(coord_G2)
            coords_H.extend(coord_H)
            elements.extend([splitter.elements[i]] * n)
            ordered_mapping.extend(seq)
            # self.print_wp(splitter, i); print(coord_G1); print(coord_G2)

        coords_G1 = np.array(coords_G1)
        coords_G2 = np.array(coords_G2)
        coords_H = np.array(coords_H)

        return coords_G1, coords_G2, coords_H, elements, ordered_mapping

    def print_wp(self, sp, id):
        """
        A short cut to print the wp information (for debug purpose)
        """
        wp1 = sp.wp1_lists[id]
        l = wp1.get_label() + "->"
        for wp in sp.wp2_lists[id]:
            l += wp.get_label() + ","
        return f"{sp.elements[id]:2s}{sp.group_type:s} ID-{id:d} {l:s}"

    def symmetrize_site_single(self, splitter, id, base, translation, run_type=1):
        """
        Symmetrize one WP to another with higher symmetry

        Args:
            splitter: splitter object
            id: index of splitter
            base: atomic position of site in H
            translation: 1*3 translation vector
            run_type: return distance or coordinates

        Returns:
            Two types of results:
            run_type=1: (dist, translation, mask)
                - dist: minimum distance
                - translation: optimal translation vector
                - mask: direction mask

            run_type=0: (coord_G1, [coord_G2], [coord_H])
                - coord_G1: coordinate in G1
                - coord_G2: coordinate in G2
                - coord_H: coordinate in H
        """
        # Some necessary items
        mask = []
        op_G1 = splitter.G1_orbits[id][0][0]
        ops_H = splitter.H_orbits[id][0]
        wp1 = splitter.wp1_lists[id]
        rot = splitter.R[:3, :3]
        tran = splitter.R[:3, 3]
        inv_rot = np.linalg.inv(rot)

        # choose the best coord1_H
        coords_H = apply_ops(base, ops_H)
        ds = [
            search_G1(splitter.G, rot, tran, coord_H + translation if translation is not None else coord_H, wp1, op_G1)[
                1
            ]
            for coord_H in coords_H
        ]

        ds = np.array(ds)
        minID = np.argmin(ds)
        coord_H = coords_H[minID]

        if run_type == 1:
            coord_G2 = coord_H + translation if translation is not None else coord_H

            tmp, _ = search_G1(splitter.G, rot, tran, coord_G2, wp1, op_G1)

            # initial guess on disp
            if translation is None:
                coord_G2, dist1 = search_G2(inv_rot, -tran, tmp, coord_H, None)
                diff = coord_G2 - coord_H
                diff -= np.rint(diff)
                translation = diff.copy()
                mask = [m for m in range(3) if abs(diff[m]) < 1e-4]
                dist = 0
            else:
                coord_G2, dist = search_G2(inv_rot, -tran, tmp, coord_H + translation, self.cell)

            return dist, translation, mask
        else:
            tmp, _ = search_G1(splitter.G, rot, tran, coord_H + translation, wp1, op_G1)
            coord_G2, _ = search_G2(inv_rot, -tran, tmp, coord_H + translation, self.cell)
            # print('XXXXXXXXX', coord_H+translation, tmp, coord_G2, dist)
            return tmp, [coord_G2], [coord_H]

    def symmetrize_site_double_k(self, splitter, id, coord_H, translation, run_type=1):
        """
        Symmetrize two WPs (wp_h1, wp_h2) to another wp_G with higher symmetry.

        Args:
            splitter (Splitter): Splitter object between G and H groups
            id (int): Index of splitter
            coord_H (array): Array of shape (2,3) containing coordinates
            translation (array): Translation vector of shape (3,)
            run_type (int): Whether to return distance (1) or coordinates (0)

        Returns:
            run_type=1:
            float: Maximum atomic displacement
            run_type=0:
            tuple: (coord_G1, coord_G2, coord_H)
                - coord_G1: coordinate in G1 basis
                - coord_G2: coordinates in G2 basis
                - coord_H: original coordinates in H basis
        """
        # For k-type splitting, restore the translation symmetry:
        # e.g. (0.5, 0.5, 0.5), (0.5, 0, 0), .etc
        # then find the best_match between coord1 and coord2,

        if translation is None:
            translation = np.zeros(3)
        rot = splitter.R[:3, :3]
        tran = splitter.R[:3, 3]
        np.linalg.inv(rot)

        wp1 = splitter.wp1_lists[id]  # wp_G
        ops_H1 = splitter.H_orbits[id][0]  # operations of wp_h1
        op_G21 = splitter.G2_orbits[id][0][0]  # operation 1 of wp_h1 in subgroup
        ops_G22 = splitter.G2_orbits[id][1]  # operations of wp_h2 in subgroup

        coord1_H, coord2_H = coord_H[0], coord_H[1]
        coord1_G2, coord2_G2 = coord1_H + translation, coord2_H + translation

        # since rotation does not change, search for the closest match on rotation
        # then we can get the translation vector
        for op_G22 in ops_G22:
            diff = (op_G22.rotation_matrix - op_G21.rotation_matrix).flatten()
            if np.sum(diff**2) < 1e-3:
                trans = op_G22.translation_vector - op_G21.translation_vector
                break
        trans -= np.rint(trans)
        coords11 = apply_ops(coord1_G2, ops_H1)
        coords11 += trans
        tmp, dist = get_best_match(coords11, coord2_G2, self.cell)

        # needed displacement
        if run_type == 1:
            return dist / 2  # np.linalg.norm(np.dot(d/2, self.cell))
        else:
            d = coord2_G2 - tmp
            d -= np.rint(d)
            op_G11 = splitter.G1_orbits[id][0][0]
            coord2_G2 -= d / 2
            coord1_G2 += d / 2
            coord1_G1, _ = search_G1(splitter.G, rot, tran, tmp, wp1, op_G11)
            return coord1_G1, [coord1_G2, coord2_G2], coord_H

    def symmetrize_site_double_t(self, splitter, id, coord_H, translation, run_type=1):
        """
        Symmetrize two WPs (wp_h1, wp_h2) to another wp_G with higher symmetry.

        Args:
            splitter (Splitter): Splitter object to specify relation between groups
            id (int): Index in the splitter
            coord_H (array): Atomic coordinates
            translation (array): 1x3 translation vector
            run_type (int): Whether to return distances (1) or coordinates (0)

        Returns:
            run_type=1:
            float: Maximum atomic displacement
            run_type=0:
            tuple: (coord_G1, coord_G2, coord_H)
                - coord_G1: Coordinates in G1 basis
                - coord_G2: Coordinates in G2 basis
                - coord_H: Original coordinates in H basis
        """

        if translation is None:
            translation = np.zeros(3)
        rot = splitter.R[:3, :3]
        tran = splitter.R[:3, 3]
        inv_rot = np.linalg.inv(rot)
        cell_G = np.dot(np.linalg.inv(splitter.R[:3, :3]).T, self.cell)
        wp1 = splitter.wp1_lists[id]  # wp_G
        ops_G11 = splitter.G1_orbits[id][0]  # operations of wp_h1 in subgroup
        ops_G12 = splitter.G1_orbits[id][1]  # operations of wp_h2 in subgroup
        ops_G1 = splitter.G[0]  # general operations of G

        coord1_H, coord2_H = coord_H[0], coord_H[1]  # coordinates in H
        coord1_G2, coord2_G2 = coord1_H + translation, coord2_H + translation  # in G

        # forward search for the best generator for wp_h1 and wp_h2 in subgroup
        coord1_G1, _ = search_G1(splitter.G, rot, tran, coord1_G2, wp1, ops_G11[0])
        coord2_G1, _ = search_G1(splitter.G, rot, tran, coord2_G2, wp1, ops_G12[0])

        # apply the operations in G
        # find the position that is closest to coord2_G1
        coords11 = apply_ops(coord1_G1, ops_G1)
        tmp, dist = get_best_match(coords11, coord2_G1, cell_G)

        # self.print_wp(splitter, id)
        if run_type == 1:
            return dist / 2
        else:
            # G1->G2->H
            d = coord2_G1 - tmp
            d -= np.rint(d)
            coord2_G1 -= d / 2

            coords22 = apply_ops(coord2_G1, ops_G1)
            coord1_G1, dist = get_best_match(coords22, coord1_G1, cell_G)
            # print("in G", l1, coord1_G1, l2, coord2_G1)

            # backward search (G->H)
            coord1_G2, dist = search_G2(inv_rot, -tran, coord1_G1, coord1_G2, self.cell)
            coord2_G2, dist = search_G2(inv_rot, -tran, coord2_G1, coord2_G2, self.cell)
            # print("in G1", l1, coord1_G2, l2, coord2_G2, dist)

            return coord2_G1, np.array([coord1_G2, coord2_G2]), coord_H

    def symmetrize_site_multi(self, splitter, id, coord_H, translation, run_type=1):
        """
        Symmetrize multiple WPs to another with higher symmetry.

        Args:
            splitter (Splitter): Splitter object between G and H groups
            id (int): Index in the splitter
            coord_H (array): Array of atomic coordinates
            translation (array): Translation vector of shape (3,)
            run_type (int): Whether to return distances (1) or coordinates (0)

        Returns:
            run_type=1:
            float: Maximum atomic displacement
            run_type=0:
            tuple: (coord_G1, coord_G2, coord_H)
            - coord_G1: Coordinate in G1 basis
            - coord_G2: Coordinates in G2 basis
            - coord_H: Original coordinates in H basis
        """

        if translation is None:
            translation = np.zeros(3)

        n = len(splitter.wp2_lists[id])
        rot = splitter.R[:3, :3]
        tran = splitter.R[:3, 3]
        inv_rot = np.linalg.inv(rot)
        cell_G = np.dot(np.linalg.inv(splitter.R[:3, :3]).T, self.cell)
        wp1 = splitter.wp1_lists[id]

        # Finds the correct quadrant to easily generate all possible_wycs
        # add translations when trying to match
        quadrant = np.array(splitter.G2_orbits[id][0][0].as_dict()["matrix"])[:3, 3]
        for k in range(3):
            if quadrant[k] >= 0.0:
                quadrant[k] = 1
            else:
                quadrant[k] = -1

        coord_G2 = coord_H + translation
        coord_G2 %= quadrant

        # uses 1st coordinate and 1st wyckoff position as starting example.
        # Finds the matching G2 operation based on the nearest G1 search
        dist_list = []
        coord_list = []
        index = []
        G2_xyz = np.zeros([n, 3])
        corresponding_ops = []

        for op in splitter.G1_orbits[id][0]:
            coord, dist = search_G1(splitter.G, rot, tran, coord_G2[0], wp1, op)
            dist_list.append(dist)
            coord_list.append(coord)

        dist_list = np.array(dist_list)
        index.append(np.argmin(dist_list))
        corresponding_ops.append(splitter.G2_orbits[id][0][index[0]])

        # Finds the free parameters xyz in the G2 basis for this coordinate
        G2_xyz[0] += find_xyz(corresponding_ops[0], coord_G2[0], quadrant)

        # Generates all possible G2 positions to match the remaining coordinates
        # Also finds the corresponding G2 free parameters xyz for each coordinate
        for j in range(1, n):
            possible_coords = [x.operate(G2_xyz[0]) for x in splitter.G2_orbits[id][j]]
            corresponding_coord, _ = get_best_match(possible_coords, coord_G2[j], cell_G)
            index.append([np.all(x == corresponding_coord) for x in possible_coords].index(True))
            corresponding_ops.append(splitter.G2_orbits[id][j][index[j]])
            G2_xyz[j] += find_xyz(corresponding_ops[j], coord_G2[j], quadrant)
        # print(G2_xyz)

        # Finds the average free parameters between all the coordinates as the best set
        # of free parameters that all coordinates must match
        final_xyz = np.mean(G2_xyz, axis=0)

        if run_type == 1:
            dist_list = []
            for j in range(n):
                d = np.dot(G2_xyz[j] - final_xyz, cell_G)
                dist_list.append(np.linalg.norm(d))
            return max(dist_list)
        else:
            coords_G1 = np.zeros([n, 3])  # xyz in G1
            coords_G2 = np.zeros([n, 3])  # xyz in G2
            # dist_list = []
            for j in range(n):
                coords_G1[j] = splitter.G1_orbits[id][j][index[j]].operate(final_xyz)
                tmp = coord_H[j] + translation
                coords_G2[j], _ = search_G2(inv_rot, -tran, coords_G1[j], tmp, self.cell)
                # dist_list.append(dist)
            # print("dist", dist)
            return coords_G1[0], coords_G2, coord_H

    def print_detail(self, solution, coords_H, coords_G, elements):
        """
        Print out the details of tranformation
        """
        (sp, mapping, translation, _, max_disp) = solution
        print("\nTransition: ", sp.H.number, "->", sp.G.number)
        print(f"Maximum displacement: {max_disp:6.3f}")
        print("Mapping:", mapping)

        count = 0
        disps = []
        for i, wp2 in enumerate(sp.wp2_lists):
            wp1 = sp.wp1_lists[i]
            for wp in wp2:
                x, y, ele = coords_H[count], coords_G[count], elements[count]
                label = wp.get_label() + "->" + wp1.get_label()
                dis = y - x - translation
                dis -= np.rint(dis)
                dis_abs = np.linalg.norm(dis.dot(self.cell))
                output = "{:2s}[{:8s}] {:8.4f}{:8.4f}{:8.4f}".format(ele, label, *x)
                output += " -> {:8.4f}{:8.4f}{:8.4f}".format(*y)
                output += " -> {:8.4f}{:8.4f}{:8.4f} {:8.4f}".format(*dis, dis_abs)
                count += 1
                disps.append(dis_abs)
                print(output)
        output = "Cell: {:7.3f}{:7.3f}{:7.3f}".format(*translation)
        output += f", Disp (A): {max(disps):6.3f}"
        print(output)

    def sort_solutions(self, solutions):
        disps = [solution[-1] for solution in solutions]
        disps = np.array(disps)
        seq = np.argsort(disps)
        return [solutions[s] for s in seq]

    def make_pyxtals_in_subgroup(self, solution, N_images=5):
        """
        Make the pyxtal according to the given solution

        Args:
            solution: a tuple of (sp, mapping, translation, wyc_set_id, max_disp)
            N_images: number of images

        Return:
            a list of pyxtal structures in low symmetry
        """
        (sp, mapping, translation, wyc_set_id, max_disp) = solution
        details = self.symmetrize(sp, mapping, translation)
        _, coords_G2, coords_H1, elements, _ = details
        # self.print_detail(solution, coords_H1, coords_G2, elements)

        # Get the list of atomic displacements
        disps = []
        count = 0
        for wp2 in sp.wp2_lists:
            for _wp in wp2:
                x, y, _ele = coords_H1[count], coords_G2[count], elements[count]
                disp = y - x - translation
                disp -= np.rint(disp)
                disps.append(disp)
                count += 1

        # Create the PyXtals
        strucs = []
        disps = np.array(disps)
        disps /= N_images - 1
        max_disp = np.max(np.linalg.norm(disps.dot(self.cell), axis=1))
        for i in range(N_images):
            coords = coords_H1 + i * disps + translation
            struc = self._make_pyxtal(sp, coords, elements, 1, False)
            struc.source = f"supergroup {i:d} {max_disp * i:6.3f}"
            strucs.append(struc)
        return strucs

    def make_pyxtal_in_supergroup(self, solution):
        """
        Make the pyxtal according to the given solution

        Args:
            solution: a tuple of (sp, mapping, translation, wyc_set_id, max_disp)

        Return:
            a pyxtal structure in high symmetry
        """
        (sp, mapping, translation, wyc_set_id, max_disp) = solution
        details = self.symmetrize(sp, mapping, translation)
        coords_G1, coords_G2, coords_H1, elements, _ = details
        struc = self._make_pyxtal(sp, coords_G1)
        struc.source = f"supergroup {max_disp:6.3f}"
        struc.disp = max_disp
        return struc

    def _make_pyxtal(self, sp, coords, elements=None, run_type=0, check=True):
        """
        Create the pyxtal with high/low symmetries

        Args:
            sp: splitter object
            coords: coordinates for each WP
            run_type: 0: high symmetry, otherwise low symmetry

        Return:
            pyxtal structure
        """
        # Create the pyxtal
        struc = self.struc.copy()
        cell_G = np.dot(np.linalg.inv(sp.R[:3, :3]).T, self.cell)
        lattice_G = Lattice.from_matrix(cell_G, ltype=sp.G.lattice_type)

        # Collect the atom_sites
        G_sites = []
        if run_type == 0:
            for i, wp in enumerate(sp.wp1_lists):
                pos = coords[i]
                pos -= np.floor(pos)
                if check:
                    # pos1 = wp.search_matched_position(sp.G[0], pos)
                    pos1 = wp.search_generator(pos, sp.G[0])
                    if pos1 is not None:
                        site = atom_site(wp, pos1, sp.elements[i])
                        G_sites.append(site)
                    else:
                        print("Group:", self.struc.group.number)
                        print("Position:", pos)
                        print(wp)
                        raise RuntimeError("cannot assign the right wp")
                else:
                    pos1 = pos
            # Update space group and lattice
            struc.group = sp.G
            struc.lattice = lattice_G
        else:
            count = 0
            for wp2 in sp.wp2_lists:
                for wp in wp2:
                    pos = coords[count]
                    pos -= np.floor(pos)
                    # pos1 = wp.search_matched_position(sp.H[0], pos)
                    pos1 = wp.search_generator(pos, sp.H[0])
                    if pos1 is not None:
                        site = atom_site(wp, pos1, elements[count])
                        G_sites.append(site)
                        count += 1
                    else:
                        print("Position:", pos)
                        print(wp)
                        print(sp)
                        raise RuntimeError("cannot assign the right wp")

            cell_U = np.dot(sp.R[:3, :3].T, lattice_G.matrix)
            struc.lattice = Lattice.from_matrix(cell_U, ltype=sp.H.lattice_type)
        struc.atom_sites = G_sites
        struc._get_formula()
        return struc


# class symmetry_mapper():
#    """
#    Class to map the symmetry relation between two structures
#    QZ: not needed now
#    Args:
#        struc_H: pyxtal structure with low symmetry (H)
#        struc_G: pyxtal structure with high symmetry (G)
#        max_d: maximum displacement to be considered
#    """
#    def __init__(self, struc_H, struc_G, max_d=1.0):
#        # initilize the necesary parameters
#        G = struc_G.group
#        H = struc_H.group
#        elements, sites = struc_G._get_elements_and_sites()
#        strucs, disp, cell, path, gts, sols = struc_G.get_transition(struc_H, d_tol=max_d)
#        if path is not None:
#            struc_G.subgroup_by_path(gts, sols)


class supergroups:
    """
    Class to search for the feasible transition to a given super group.

    Args:
        struc: PyXtal object
            Input structure with subgroup symmetry (H)
        G: int, optional
            Target supergroup space group number
        path: list, optional
            List of space group numbers defining path from H to G (e.g. [62, 59, 74])
        d_tol: float, default=1.0
            Maximum allowed atomic displacement during symmetry change
        max_per_G: int, default=100
            Maximum number of symmetry solutions to consider per group
        max_layer: int, default=5
            Maximum number of intermediate groups in path
        show: bool, default=False
            Whether to show detailed progress

    Note:
        Either G or path must be provided, but not both None.
    """

    def __init__(
        self,
        struc,
        G=None,
        path=None,
        d_tol=1.0,
        max_per_G=100,
        max_layer=5,
        show=False,
    ):
        self.struc_H = struc
        self.show = show
        self.d_tol = d_tol
        self.max_per_G = max_per_G
        self.max_layer = max_layer

        if path is None:
            if G is None:
                raise ValueError("G and path cannot be None at the same time")
            paths = struc.group.search_supergroup_paths(G, max_layer=max_layer)
        else:
            paths = [path]
            G = path[-1]
        self.G = G

        print(f"{len(paths):d} paths will be checked")
        self.strucs = None
        failed_paths = []
        for i, p in enumerate(paths):
            status = f"Path{i:2d}: {p!s:s}, "
            if new_path(p, failed_paths):
                strucs, solutions, w_path, valid = self.struc_along_path(p)
                status += f"stops at: {w_path!s:s}"
                if valid:
                    self.strucs = strucs
                    self.solutions = solutions
                    if len(strucs) > len(p):
                        self.path = [self.struc_H.group.number, *p]
                    else:
                        self.path = p
                    break
                failed_paths.append(w_path)
            else:
                status += "skipped..."

    def __str__(self):
        s = "\nTransition to super group: "
        if self.strucs is None:
            s += "Unsuccessful, check your input"
        else:
            s += f"{self.path[0]:d}"
            for i, p in enumerate(self.path[1:]):
                s += f" -> {p:d} [{self.strucs[i + 1].disp:4.3f}]"
            s += "\n"
            for struc in self.strucs:
                s += str(struc)
        return s

    def __repr__(self):
        return str(self)

    def print_solutions(self):
        for solution in self.solutions:
            (sp, mapping, trans, wyc_set_id, max_disp) = solution
            print("\nTransition: ", sp.H.number, "->", sp.G.number)
            output = "Cell: {:7.3f}{:7.3f}{:7.3f}".format(*trans)
            output += f", Disp (A): {max_disp:6.3f}"
            print(output)
            # print('mapping', mapping)
            for i, wp2 in enumerate(sp.wp2_lists):
                wp1 = sp.wp1_lists[i]
                ele = sp.elements[i]
                l2 = wp1.get_label()
                for _j, wp in enumerate(wp2):
                    l1 = wp.get_label()
                    output = f"{ele:2s} [{mapping[i]:2d}]: "
                    output += f"{l1:3s} -> {l2:3s}"
                    print(output)

    def get_transformation(self, N_images=2):
        """
        Get the series of transformed structures between H and G

        Args:
            N_images: number of structures

        Returns:
            a series of pyxtal structures
        """
        # self.print_solutions()
        # derive the backward subgroup representation
        struc0 = self.strucs[-1]
        for i in range(1, len(self.solutions) + 1):
            (sp, mapping, trans, wyc_set_id, max_disp) = self.solutions[-i]
            struc0 = struc0._subgroup_by_splitter(sp, eps=0)
            seq = [mapping.index(x) for x in list(range(len(mapping)))]
            struc0.atom_sites = [struc0.atom_sites[i] for i in seq]
            if wyc_set_id > 0:
                struc0 = struc0._get_alternative_back(wyc_set_id)
            # print(struc0)
            # print(i, sp.G.number, sp.H.number, wyc_set_id, match, trans)
        # print(self.struc_H)
        # print(struc0)
        disps, _, _, _ = self.struc_H.get_disps_sets(struc0, d_tol=1.0, keep_lattice=True)
        if disps is not None:
            cell = struc0.lattice.matrix
            return self.struc_H.make_transitions(disps, lattice=cell, N_images=N_images)
        else:
            raise RuntimeError("Cannot find the match between H and G")

    def struc_along_path(self, path):
        """
        Search for the super group structure along a given path.

        Args:
            path (list): List of space group numbers, e.g. [59, 71, 139]

        Returns:
            tuple: (strucs, valid_sols, working_path, valid)
            - strucs: List of structures along the path
            - valid_sols: List of valid solutions for each transition
            - working_path: List of space group numbers along the path
            - valid: True if successfully reached target group, False otherwise
        """
        strucs = []
        valid_sols = []
        working_path = []
        valid = False

        G_strucs = [self.struc_H]
        prev_sols = None

        for G in path:
            working_path.append(G)
            # Here we just include the first one that works
            for i, G_struc in enumerate(G_strucs):
                my = supergroup(G_struc, G)
                sols = my.search_supergroup(self.d_tol, self.max_per_G)
                new_G_strucs, new_sols = my.make_supergroup(sols, show_detail=self.show)
                if len(new_G_strucs) > 0:
                    strucs.append(G_struc)
                    if prev_sols is not None:
                        valid_sols.append(prev_sols[i])
                    G_strucs = new_G_strucs
                    prev_sols = deepcopy(new_sols)
                    break
            # Give up if the path does not work
            if len(new_G_strucs) == 0:
                break

        # add the final struc
        if len(new_G_strucs) > 0:
            ds = [st.disp for st in new_G_strucs]
            minID = np.argmin(np.array(ds))
            strucs.append(new_G_strucs[minID])
            valid_sols.append(prev_sols[i])
            valid = True
        return strucs, valid_sols, working_path, valid

    def write_cifs(self):
        """
        Dump the cif files in sequence
        """
        for i, struc in enumerate(self.strucs):
            struc.to_file(str(i) + "-G" + str(struc.group.number) + ".cif")


if __name__ == "__main__":
    from time import time
    from pyxtal import pyxtal

    data = {
        # "PVO": [12, 166],
        # "PPO": [12],
        "BTO": [123, 221],
        "lt_cristobalite": [98, 210, 227],
        "BTO-Amm2": [65, 123, 221],
        "NaSb3F10": [176, 194],
        "MPWO": [59, 71, 139, 225],
        # "NbO2": 141,
        # "GeF2": 62,
        # "lt_quartz": 180,
        # "NiS-Cm": 160,
        # "BTO-Amm2": 221,
        # "BTO": 221,
        # "lt_cristobalite": 227,
        # "NaSb3F10": 194,
        # "MPWO": 225,
    }
    cif_path = "pyxtal/database/cifs/"

    for cif in data:
        t0 = time()
        print("===============", cif, "===============")
        s = pyxtal()
        s.from_seed(cif_path + cif + ".cif")
        if isinstance(data[cif], list):
            sup = supergroups(s, path=data[cif], show=False, max_per_G=2500)
        else:
            sup = supergroups(s, G=data[cif], show=False, max_per_G=2500)
        if len(sup.strucs) > 0:
            # print(sup.strucs[-1])
            strucs = sup.get_transformation()
            pmg_0, pmg_1 = s.to_pymatgen(), sup.strucs[-1].to_pymatgen()
            pmg_2, pmg_3 = strucs[0].to_pymatgen(), strucs[1].to_pymatgen()
            print(strucs)
            dist1 = sm.StructureMatcher().get_rms_dist(pmg_0, pmg_2)[0]
            dist2 = sm.StructureMatcher().get_rms_dist(pmg_1, pmg_3)[0]
            strs = "====================================================="
            strs += f"==============={time() - t0:12.3f} seconds"
            print(strs)
            if dist1 > 1e-3 or dist2 > 1e-3:
                print("+++++++++++++++++++++++++++++++Problem in ", cif)
                break
        else:
            print("+++++++++++++++++++++++++++++++++++Problem in ", cif)
            break