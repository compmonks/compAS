from brg.geometry import Line


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__version__    = '0.1'
__email__      = 'vanmelet@ethz.ch'
__status__     = 'Development'
__date__       = '2015-12-03 13:43:05'


__all__ = [
    'split_edge',
]


def split_edge(mesh, u, v, t=0.5, allow_boundary=False):
    """Split and edge by inserting a vertex along its length.

    Parameters:
        u (str): The key of the first vertex of the edge.
        v (str): The key of the second vertex of the edge.
        t (float): The position of the inserted vertex.
        allow_boundary (bool): Split boundary edges, if True. Defaults to
            False.

    Returns:
        str: The key of the inserted vertex.

    Raises:
        ValueError: If `u` and `v` are not neighbours.
    """
    if t <= 0.0:
        raise ValueError('t should be greater than 0.0.')
    if t >= 1.0:
        raise ValueError('t should be smaller than 1.0.')
    # check if the split is legal
    # don't split if edge is on boundary
    fkey_uv = mesh.halfedge[u][v]
    fkey_vu = mesh.halfedge[v][u]
    if not allow_boundary:
        if fkey_uv is None or fkey_vu is None:
            return
    # the split vertex
    sp = mesh.vertex_coordinates(u)
    ep = mesh.vertex_coordinates(v)
    line = Line(sp, ep)
    line.scale(t)
    x, y, z = line.end
    # --------------------------------------------------------------------------
    u_attr = mesh.vertex[u]
    v_attr = mesh.vertex[v]
    w_attr = {}
    for name in u_attr:
        try:
            w_attr[name] = 0.5 * (u_attr[name] + v_attr[name])
        except:
            try:
                w_attr[name] = [0.5 * (u_attr[name][_] + v_attr[name][_]) for _ in range(len(u_attr[name]))]
            except:
                w_attr[name] = None
    # --------------------------------------------------------------------------
    w = mesh.add_vertex(attr_dict=w_attr, x=x, y=y, z=z)
    # split half-edge UV
    mesh.halfedge[u][w] = fkey_uv
    mesh.halfedge[w][v] = fkey_uv
    del mesh.halfedge[u][v]
    # update the UV face if it is not the `None` face
    if fkey_uv is not None:
        mesh.face[fkey_uv][u] = w
        mesh.face[fkey_uv][w] = v
    # split half-edge VU
    mesh.halfedge[v][w] = fkey_vu
    mesh.halfedge[w][u] = fkey_vu
    del mesh.halfedge[v][u]
    # update the VU face if it is not the `None` face
    if fkey_vu is not None:
        mesh.face[fkey_vu][v] = w
        mesh.face[fkey_vu][w] = u
    # return the key of the split vertex
    return w
