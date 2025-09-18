from __future__ import annotations

from itertools import combinations
from typing import Union

import cvxpy as cp
import torch as th
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import det, matrix_rank, norm
from numpy.random import randn, uniform


class Zonotope:
    @classmethod
    def from_unit_box(cls, dim: int, c: Union[np.ndarray, None] = None) -> Zonotope:
        """create a zonotope from a unit box"""

        G = np.eye(dim)

        return cls(G, c)

    @classmethod
    def from_random(cls, n_d: int, n_g: int, c: Union[np.ndarray, None] = None) -> Zonotope:
        """
        Create a zonotope with random generators and center vector
        The strategy is to sample the generator "directions" as points on a
        norm-sphere and then scale them uniformly from [0,1].
        Refer to CORAs zonotope.generateRandom().
        """

        scaling_factors = uniform(size=n_g)

        G = np.zeros((n_d, n_g))

        for g_idx in range(n_g):
            gen_vector = randn(n_d, 1)
            gen_vector_normalized = gen_vector / norm(gen_vector)
            G[:, [g_idx]] = gen_vector_normalized * scaling_factors[g_idx]

        return cls(G, c)
    
    @classmethod
    def from_interval(cls, interval: np.ndarray):
        """
        Create a zonotope from an interval
        """
        c = interval[:, 0] + 0.5 * (interval[:, 1] - interval[:, 0])
        c = c.reshape((-1, 1))
        G = 0.5 * np.diag(interval[:, 1] - interval[:, 0])

        return cls(G, c)
    
    def __init__(self, G: Union[np.ndarray, None], c: Union[np.ndarray, None] = None):
        """class representing a zonotope Z = {c + sum_i G[:, i] * alpha_i | alpha_i in [-1,1]}"""

        if c is None:
            c = np.zeros((G.shape[0], 1))

        if len(c.shape) == 1 or c.shape[1] != 1:
            c = c.reshape((c.shape[0], 1))

        assert len(G.shape) == 2, "G must be a matrix"
        assert len(c.shape) == 2 and c.shape[1] == 1, "c must be a vector"
        assert c.shape[0] == G.shape[0], "c and G must have matching dimensions"

        self.d, self.g = np.shape(G)  # get dimension and number of generators

        self.c = c
        self.G = G

        # annotations
        # these are attributes that are expensive to compute and therefore stored in the instance
        self._volume = None
        self._vertices = None
        self.boundary_points = []

    def __add__(self, other: Zonotope) -> Zonotope:
        """minkowsi sum of two zonotopes"""

        return self.__class__(np.concatenate((self.G, other.G), axis=1), self.c + other.c)

    def __mul__(self, other: float) -> Zonotope:
        """multiplication of a zonotope with a scalar"""

        return self.__class__(self.G * other, self.c * other)

    def __rmul__(self, other: float) -> Zonotope:
        """multiplication of a zonotope with a scalar"""

        return self.__class__(self.G * other, self.c * other)

    def map(self, other: np.ndarray) -> Zonotope:
        """multiplication of a zonotope with a matrix"""

        return self.__class__(other @ self.G, other @ self.c)

    @property
    def vertices(self) -> np.ndarray:
        """
        Compute the vertices of the zonotope
        Returns:
            np.ndarray: vertices (first and last the same)
        """
        if self._vertices is None:
            # remove zero generators
            if isinstance(self.G, th.Tensor):
                tmp = np.sum(abs(self.G.numpy()), axis=0)
                ind = np.where(tmp > 0)[0]
                G = self.G[:, ind].numpy()
                c = self.c.numpy()
            else: 
                tmp = np.sum(abs(self.G), axis=0)
                ind = np.where(tmp > 0)[0]
                G = self.G[:, ind]
                c = self.c

            # size of enclosing interval
            xmax = np.sum(abs(G[0, :]))
            ymax = np.sum(abs(G[1, :]))

            # flip directions of generators so that all generators are pointing up
            ind = np.where(G[1, :] < 0)
            G[:, ind] = -G[:, ind]

            # sort generators according to their angles
            ang = np.arctan2(G[1, :], G[0, :])
            ind = np.where(ang < 0)[0]
            ang[ind] = ang[ind] + 2 * np.pi

            ind = np.argsort(ang)

            # sum the generators in the order of their angle
            n = G.shape[1]
            points = np.zeros((2, n + 1))

            for i in range(n):
                points[:, i + 1] = points[:, i] + 2 * G[:, ind[i]]

            points[0, :] = points[0, :] + xmax - np.max(points[0, :])
            points[1, :] = points[1, :] - ymax

            # mirror upper half of the zonotope to get the lower half
            tmp1 = np.concatenate((points[0, :], points[0, n] + points[0, 0] - points[0, 1 : n + 1]))
            tmp2 = np.concatenate((points[1, :], points[1, n] + points[1, 0] - points[1, 1 : n + 1]))

            tmp1 = np.resize(tmp1, (1, len(tmp1)))
            tmp2 = np.resize(tmp2, (1, len(tmp2)))

            points = np.concatenate((tmp1, tmp2), axis=0)

            # shift vertices by the center vector
            self._vertices = points + c

        return self._vertices

    def plot(self, color: str = "b", show: bool = True):
        """
        Plot a zonotope
        Args:
            color (str, optional): Color of the zonotope. Defaults to "b".
            show (bool, optional): Show the plot. Defaults to True.
        """
        points = self.vertices

        plt.plot(points[0, :], points[1, :], color)

        if show:
            plt.show()

    @property
    def volume(self) -> float:
        """
        Based on:
        [1] E. Gover and N. Krikorian, “Determinants and the volumes of parallelotopes and zonotopes”,
        Linear Algebra and its Applications, vol. 433, no. 1, pp. 28–40, 2010.
        Specifically corollary 3.4, p.39.
        """
        if self._volume is None:
            vol = 0.0

            if matrix_rank(self.G) < self.d:
                # Generator matrix of insufficient rank for volume calculation
                return 0.0

            gcombs = [x for x in combinations(range(self.g), r=self.d)]

            for comb in gcombs:
                A = self.G[:, comb]
                b = np.absolute(det(A))
                vol += b

            vol = 2**self.d * vol

            self._volume = vol

        return self._volume

    def volume_approx(self, method: str = "frob") -> float:
        """
        Approximate the volume of a zonotope.

        Args:
            method (str, optional): Method to use.
                One of:
                "frob" (Frobenius norm),
                "1" (1-norm),
                "int" (interval norm),
                "inf" (infinity norm).
                Defaults to "frob".

        Returns:
            float: appxoimate volume
        """

        if method == "frob":  # asbolute sum of all elements squared
            vol = np.linalg.norm(self.G, ord="fro")
        elif method == "1":  # max row sum
            vol = np.linalg.norm(self.G, ord=1)
        elif method == "inf":  # max column sum
            vol = np.linalg.norm(self.G, ord=np.inf)
        elif method == "int":  # absolute sum of all elements
            vol = sum([np.linalg.norm(self.G[:, i], ord=1) for i in range(self.g)])
        else:
            raise NotImplementedError("Invalid method")

        return vol

    def get_boundary_points(self, n: int, force_new: bool = False) -> np.ndarray:
        """
        Get boundary points of the zonotope in n random directions.
        If they have not yet been precoputed, n points are now precomputed.

        Args:
            n (int): Number of points, randomly sampled from precomputed points.
                If the number of available points is smaller than n, all points are returned.
            force_new (bool, optional): Force precomputation of new points.

        Returns:
            np.ndarray: boundary points
        """

        if len(self.boundary_points) == 0 or force_new:
            self.boundary_points = []
            for _ in range(n):
                direction = randn(self.d, 1)
                direction = direction / norm(direction)
                self.boundary_points.append(self.boundary_point(direction))

        if n >= len(self.boundary_points):
            return self.boundary_points
        else:
            np.random.choice(self.boundary_points, size=n, replace=False)

    def boundary_point(self, direction: np.ndarray, point: np.ndarray = None) -> np.ndarray:
        """
        Computes the boundary point of the zonotope in the given direction, starting from point.
        If point is None, the center is used.

        Args:
            direction (np.ndarray): The direction vector.
            point (np.ndarray, optional): The origin point for the direction line. Defaults to None.

        Returns:
            np.ndarray: The boundary point in the given direction.
        """

        assert direction.ndim == 2 and direction.shape[1] == 1, "direction must be a column vector"

        point = self.c if point is None else point
        assert point.ndim == 2 and point.shape[1] == 1, "point must be a column vector"

        alpha = cp.Variable()
        gamma = cp.Variable((self.g, 1))

        constraints = [
            point + alpha * direction == self.c + self.G @ gamma,
            gamma <= 1,
            -gamma <= 1,
        ]
        objective = cp.Minimize(alpha)

        # Solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        # Check solver status
        if problem.status not in [cp.OPTIMAL]:
            raise ValueError("Solver did not converge to an optimal solution.")

        return point + alpha.value * direction

    def contains_point(self, point: np.ndarray) -> bool:
        eps = 1e-4
        return self.zonotope_norm(point) <= 1 + eps

    def zonotope_norm(self, direction: np.ndarray) -> float:
        """calculate zonotope norm in the given direction
        Based on: Kulmburg, A., Althoff, M., (2021): "On the co-NP-Completeness
            of the Zonotope Containment Problem", Eq. (8).
        """

        assert len(direction.shape) == 2 and direction.shape[1] == 1, "direction must be a vector"
        assert direction.shape[0] == self.d, "direction must have the same dimension as the zonotope"

        gamma = cp.Variable((self.g, 1))
        w = cp.Variable()

        constraints = [self.G @ gamma == direction - self.c, gamma <= w, -gamma <= w]

        # Objective
        objective = cp.Minimize(w)

        # Solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve(verbose=False, solver=cp.GUROBI)

        # Check solver status
        if problem.status not in [cp.OPTIMAL]:
            raise ValueError("Solver did not converge to an optimal solution.")

        return w.value

    @staticmethod
    def point_containment_constraints(point: cp.Expression | np.ndarray,
                                      center: cp.Expression | np.ndarray,
                                      generator: cp.Expression | np.ndarray) \
            -> list[cp.Constraint]:
        """
        Construct the constraints for a point-zonotope containment problem with
        Z = <c, G> and p for p in Z.

        Based on: Kulmburg, A., Althoff, M., (2021): "On the co-NP-Completeness of the
        Zonotope Containment Problem", Eq. (6).

        Args:
            point: The point to check for containment.
            center: The center of the zonotope.
            generator: The generators of the zonotope.

        Returns:
            The constraints for the point-zonotope containment problem.
        """
        weights = cp.Variable(generator.shape[1])

        pos_constraint = point - center == generator @ weights
        size_constraint = cp.norm(weights, "inf") <= 1
        return [pos_constraint, size_constraint]

    @staticmethod
    def zonotope_containment_constraints(c1: cp.Expression | np.ndarray,
                                         g1: cp.Expression | np.ndarray,
                                         c2: cp.Expression | np.ndarray,
                                         g2: cp.Expression | np.ndarray) \
            -> list[cp.Constraint]:
        """
        Construct the constraints for a zonotope-zonotope containment problem with
        Z_1 = <c1, g1> and Z_2 = <c2, g2> for Z_1 in Z_2.

        Based on: Sadraddini, Sadra, and Russ Tedrake. "Linear encodings for polytope
        containment problems." 2019 IEEE 58th conference on decision and control (CDC).
        IEEE, 2019.

        Args:
            c1: The center of the first zonotope.
            g1: The generators of the first zonotope.
            c2: The center of the second zonotope.
            g2: The generators of the second zonotope.

        Returns:
            The constraints for the zonotope-zonotope containment problem.
        """
        weights = cp.Variable(g2.shape[1])
        mapping = cp.Variable((g2.shape[1], g1.shape[1]))

        shape_constraint = g1 == g2 @ mapping
        pos_constraint = c2 - c1 == g2 @ weights
        size_constraint = cp.norm(cp.hstack([
            mapping,
            cp.reshape(weights, (-1, 1), "C")
        ]), "inf") <= 1

        return [shape_constraint, pos_constraint, size_constraint]
    
