from __future__ import print_function

from compas.datastructures.mesh.algorithms import smooth_mesh_centroid

from compas.datastructures.mesh.operations import split_edge_trimesh
from compas.datastructures.mesh.operations import collapse_edge_trimesh
from compas.datastructures.mesh.operations import swap_edge_trimesh


__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'optimise_trimesh_topology',
]


def optimise_trimesh_topology(mesh,
                              target,
                              kmax=100,
                              target_start=1.0,
                              kmax_start=None,
                              tol=0.1,
                              divergence=0.01,
                              verbose=False,
                              allow_boundary=False,
                              ufunc=None,
                              ufunc_args=None):
    """Remesh until all edges have a specified target length.

    This involves three operations:

        * split edges that are longer than a maximum length,
        * collapse edges that are shorter than a minimum length,
        * swap edges if this improves the valency error.

    The minimum and maximum lengths are calculated based on a desired target
    length:

    Parameters:
        mesh (Mesh) : A triangle mesh.
        target (float) : The target length.
        tol (float) : Length deviation tolerance. Defaults to `0.1`
        kmax (int) : The number of iterations.
        verbose (bool) : Print feedback messages, if True.

    Returns:
        None

    Note:
        This algorithm not only changes the geometry of the mesh, but also its
        topology as needed to achieve the specified target lengths.
        Topological changes are made such that vertex valencies are well-balanced
        and close to six.

    Examples:

        .. plot::
            :include-source:

            from compas.datastructures.mesh import Mesh
            from compas.datastructures.mesh.algorithms import optimise_trimesh_topology

            vertices = [
                (0.0, 0.0, 0.0),
                (10.0, 0.0, 0.0),
                (10.0, 10.0, 0.0),
                (0.0, 10.0, 0.0),
                (5.0, 5.0, 0.0)
            ]
            faces = [
                (0, 1, 4),
                (1, 2, 4),
                (2, 3, 4),
                (3, 0, 4)
            ]

            mesh = Mesh.from_vertices_and_faces(vertices, faces)

            optimise_trimesh_topology(
                mesh,
                target=0.5,
                target_start=1.0,
                tol=0.05,
                kmax=300,
                allow_boundary=True,
                verbose=False
            )

            mesh.plot(vertexsize=0.05)


    """
    if verbose:
        print(target)

    lmin = (1 - tol) * (4.0 / 5.0) * target
    lmax = (1 + tol) * (4.0 / 3.0) * target

    edge_len = []
    for u, v in mesh.edges():
        edge_len.append(mesh.edge_length(u, v))
    target_start = max(edge_len)

    fac = float(target_start / target)

    boundary = set(mesh.vertices_on_boundary())
    count = 0

    if not kmax_start:
        kmax_start = kmax / 2.0

    kmax_start = float(kmax_start)

    for k in xrange(kmax):

        if k <= kmax_start:
            scale_val = fac * (1.0 - k / kmax_start)
            dlmin = lmin * scale_val
            dlmax = lmax * scale_val
        else:
            dlmin = 0
            dlmax = 0

        if verbose:
            print(k)

        count += 1

        if k % 20 == 0:
            num_vertices_1 = len(mesh.vertex)

        # split
        if count == 1:
            visited = set()

            for u, v in mesh.edges():
                # is this correct?
                if u in visited or v in visited:
                    continue

                if mesh.edge_length(u, v) <= lmax + dlmax:
                    continue
                if verbose:
                    print('split edge: {0} - {1}'.format(u, v))

                split_edge_trimesh(mesh, u, v, allow_boundary=allow_boundary)

                visited.add(u)
                visited.add(v)

        # collapse
        elif count == 2:
            visited = set()

            for u, v in mesh.edges():
                # is this correct?
                if u in visited or v in visited:
                    continue

                if mesh.edge_length(u, v) >= lmin - dlmin:
                    continue

                if verbose:
                    print('collapse edge: {0} - {1}'.format(u, v))

                collapse_edge_trimesh(mesh, u, v)

                visited.add(u)
                visited.add(v)

                for nbr in mesh.halfedge[u]:
                    visited.add(nbr)

        # swap
        elif count == 3:
            visited = set()

            for u, v in mesh.edges():
                if u in visited or v in visited:
                    continue

                f1 = mesh.halfedge[u][v]
                f2 = mesh.halfedge[v][u]

                if f1 is None or f2 is None:
                    continue

                v1 = mesh.face[f1][v]
                v2 = mesh.face[f2][u]
                valency1 = mesh.vertex_degree(u)
                valency2 = mesh.vertex_degree(v)
                valency3 = mesh.vertex_degree(v1)
                valency4 = mesh.vertex_degree(v2)

                if u in boundary:
                    valency1 += 2
                if v in boundary:
                    valency2 += 2
                if v1 in boundary:
                    valency3 += 2
                if v2 in boundary:
                    valency4 += 2

                current_error = abs(valency1 - 6) + abs(valency2 - 6) + abs(valency3 - 6) + abs(valency4 - 6)
                flipped_error = abs(valency1 - 7) + abs(valency2 - 7) + abs(valency3 - 5) + abs(valency4 - 5)

                if current_error <= flipped_error:
                    continue
                if verbose:
                    print('swap edge: {0} - {1}'.format(u, v))

                swap_edge_trimesh(mesh, u, v)
                visited.add(u)
                visited.add(v)
        # count
        else:
            count = 0

        if (k - 10) % 20 == 0:
            num_vertices_2 = len(mesh.vertex)

            if abs(1 - num_vertices_1 / float(num_vertices_2)) < divergence and k > kmax_start:
                break

        # smoothen
        boundary = set(mesh.vertices_on_boundary())
        smooth_mesh_centroid(mesh, fixed=boundary, kmax=1)

        if ufunc:
            ufunc(mesh, k, ufunc_args)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import time

    from compas.datastructures.mesh import Mesh

    vertices = [
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.0),
        (5.0, 5.0, 0.0)
    ]

    faces = [
        (0, 1, 4),
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4)
    ]

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    t0 = time.time()

    optimise_trimesh_topology(
        mesh,
        target=0.5,
        target_start=1.0,
        tol=0.05,
        kmax=300,
        allow_boundary=True,
        verbose=False
    )

    t1 = time.time()

    print(t1 - t0)

    mesh.plot(vertexsize=0.05)
