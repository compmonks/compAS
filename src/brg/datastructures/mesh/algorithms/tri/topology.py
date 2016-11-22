""""""

from brg.datastructures.mesh.algorithms.smoothing import mesh_smooth_centroid

from brg.datastructures.mesh.operations.tri.split import split_edge
from brg.datastructures.mesh.operations.tri.collapse import collapse_edge
from brg.datastructures.mesh.operations.tri.swap import swap_edge

__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT'
__email__      = 'vanmelet@ethz.ch'


def remesh(mesh, target,
           tol=0.1, divergence=0.01, kmax=100,
           target_start=None, kmax_approach=None,
           verbose=False, allow_boundary=False,
           ufunc=None):
    """Remesh until all edges have a specified target length.

    This involves three operations:

        * split edges that are shorter than a minimum length,
        * collapse edges that are longer than a maximum length,
        * swap edges if this improves the valency error.

    The minimum and maximum lengths are calculated based on a desired target
    length:

    Parameters:
        target (float): The target length.
        tol (float): Length deviation tolerance. Defaults to `0.1`
        kmax (int): The number of iterations.
        verbose (bool): Print feedback messages, if True.

    Returns:
        None
    """
    if verbose:
        print
        print target
    lmin = (1 - tol) * (4.0 / 5.0) * target
    lmax = (1 + tol) * (4.0 / 3.0) * target
    
    fac = float(target_start/target)
    
    boundary = set(mesh.vertices_on_boundary())
    count = 0
    
  
    kmax_approach = float(kmax_approach)
    for k in xrange(kmax):
        
        
        if k <= kmax_approach and 1==1:
            scale_val = fac*(1.0-k/kmax_approach)
            dlmin = lmin*scale_val
            dlmax = lmax*scale_val 
        else:
            dlmin = 0
            dlmax = 0
        
        
        if verbose:
            print
            print k
        count += 1
        # split
        
        if k%20 == 0:    
            num_vertices_1 = len(mesh.vertex)
        
        if count == 1:
            
            
            visited = set()
            for u, v in mesh.edges():
                # is this correct?
                if u in visited or v in visited:
                    continue
                l = mesh.edge_length(u, v)
#                 if l <= lmax:
#                     continue
                if l <= lmax+dlmax:
                
                    continue
                if verbose:
                    print 'split edge: {0} - {1}'.format(u, v)
                split_edge(mesh, u, v, allow_boundary=allow_boundary)
                visited.add(u)
                visited.add(v)
        # collapse
        elif count == 2:
            visited = set()
            for u, v in mesh.edges():
                # is this correct?
                if u in visited or v in visited:
                    continue
                l = mesh.edge_length(u, v)
#                 if l >= lmin:
#                     continue
                if l >= lmin-dlmin:
                    continue
                if verbose:
                    print 'collapse edge: {0} - {1}'.format(u, v)
                collapse_edge(mesh, u, v)
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
                    print 'swap edge: {0} - {1}'.format(u, v)
                swap_edge(mesh, u, v)
                visited.add(u)
                visited.add(v)
        # count
        else:
            count = 0
            
        
        if (k-10)%20 == 0:    
            num_vertices_2 = len(mesh.vertex)    
            #print "number of vertices: " + str(num_vertices_1) + " and " + str(num_vertices_2) + " means: " + str(abs(1-num_vertices_1/float(num_vertices_2)))
            if abs(1-num_vertices_1/float(num_vertices_2)) < divergence and k > kmax_approach:
                #print "break"
                break
#             if not has_split and not has_collapsed and not has_swapped and dlmin == 0:
#                 termin += 1
#                 if  termin > 10:
#                     print "break asdddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
#                     break
#             else:
#                 termin = 0
            
        # smoothen
        mesh_smooth_centroid(mesh,fixed=boundary,kmax=1)  
        if ufunc:
            ufunc(mesh,k)
          
            
            
    # remesh differently based on target specifications
    # if start and steps:
    #     step = (start - target) / float(steps)
    #     for i in range(steps + 1):
    #         target = start - i * step
    #         _remesh(target)
    #     smooth(mesh, 5)
#     if start and steps:
#         step = (start - target) / float(steps)
#         kmax = max(int(kmax / float(steps)), 10)
#         for i in range(steps + 1):
#             target = start - i * step
#             _remesh(target, kmax)
#     else:
#         _remesh(target, kmax)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import time

    from brg.datastructures import Mesh
    from brg.datastructures.mesh.drawing import draw_mesh

    vertices = [
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.0),
        (5.0, 5.0, 0.0)
    ]

    faces = [
        ('0', '1', '4'),
        ('1', '2', '4'),
        ('2', '3', '4'),
        ('3', '0', '4')
    ]

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    t0 = time.time()

    remesh(mesh, target=0.5, start=1.0, steps=10, tol=0.05, kmax=300, allow_boundary=True, verbose=False)

    t1 = time.time()

    print t1 - t0

    draw_mesh(mesh)
