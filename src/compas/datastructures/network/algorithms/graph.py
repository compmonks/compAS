from math import cos
from math import sin

from compas.geometry.planar import angle_smallest_vectors_2d
from compas.geometry.planar import is_intersection_segment_segment_2d


__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = '<vanmelet@ethz.ch>'


__all__ = [
    'is_network_crossed',
    'are_network_edges_crossed',
    'count_network_crossings',
    'is_network_2d',
    'is_network_planar',
    'is_network_planar_embedding',
    'embed_network_in_plane',
    'find_network_crossings',
]


def is_network_crossed(network):
    for u1, v1 in network.edges_iter():
        for u2, v2 in network.edges_iter():
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = network.vertex[u1]['x'], network.vertex[u1]['y']
                b = network.vertex[v1]['x'], network.vertex[v1]['y']
                c = network.vertex[u2]['x'], network.vertex[u2]['y']
                d = network.vertex[v2]['x'], network.vertex[v2]['y']
                if is_intersection_segment_segment_2d((a, b), (c, d)):
                    return True
    return False


def are_network_edges_crossed(edges, vertices):
    for u1, v1 in edges:
        for u2, v2 in edges:
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = vertices[u1]
                b = vertices[v1]
                c = vertices[u2]
                d = vertices[v2]
                if is_intersection_segment_segment_2d((a, b), (c, d)):
                    return True
    return False


def count_network_crossings(network):
    count = 0
    for u1, v1 in network.edges_iter():
        for u2, v2 in network.edges_iter():
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = network.vertex[u1]['x'], network.vertex[u1]['y']
                b = network.vertex[v1]['x'], network.vertex[v1]['y']
                c = network.vertex[u2]['x'], network.vertex[u2]['y']
                d = network.vertex[v2]['x'], network.vertex[v2]['y']
                if is_intersection_segment_segment_2d((a, b), (c, d)):
                    count += 1
    return count


def find_network_crossings(network):
    crossings = []
    for u1, v1 in network.edges_iter():
        for u2, v2 in network.edges_iter():
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = network.vertex_coordinates(u1, 'xy')
                b = network.vertex_coordinates(v1, 'xy')
                c = network.vertex_coordinates(u2, 'xy')
                d = network.vertex_coordinates(v2, 'xy')
                if is_intersection_segment_segment_2d((a, b), (c, d)):
                    crossings.append(((u1, v1), (u2, v2)))
    return crossings


def is_network_2d(network):
    z = None
    for key in network:
        if z is None:
            z = network[key].get('z', 0.0)
        else:
            if z != network[key].get('z', 0.0):
                return False
    return True


def is_network_planar(network):
    """Check if the network is planar.

    A network is planar if it can be drawn in the plane without crossing edges.
    If a network is planar, it can be shown that an embedding of the network in
    the plane exists, and, furthermore, that straight-line embedding in the plane
    exists.

    Warning:
        This function uses the python binding of the *edge addition planarity suite*
        in the background. The package is available on GitHub: https://github.com/hagberg/planarity.

    Parameters:
        network (compas.datastructures.network.Network): The network object.

    Returns:
        bool: ``True`` if the network is planar. ``False`` otherwise.

    Raises:
        ImportError: If the planarity package is not installed.

    Example:

        .. plot::
            :include-source:

            import compas

            from compas.datastructures.network import Network
            from compas.datastructures.network.algorithms import is_network_planar
            from compas.datastructures.network.algorithms import find_network_crossings

            network = Network.from_obj(compas.get_data('lines.obj'))

            network.add_edge(21, 29)
            network.add_edge(17, 28)

            if not is_network_planar(network):
                crossings = find_network_crossings(network)

            network.plot(
                vsize=0.15,
                vlabel={key: key for key in network},
                ecolor={edge: (255, 0, 0) for edges in crossings for edge in edges}
            )

    """
    try:
        import planarity
    except ImportError:
        print("Planarity is not installed. Get Planarity at https://github.com/hagberg/planarity.")
        raise
    return planarity.is_planar(network.edges())


# is it embedded in the plane without crossing (curved) edges
def is_network_planar_embedding(network):
    return (is_network_planar(network) and
            is_network_2d(network) and not
            is_network_crossed(network))


def embed_network_in_plane(network, fix=None, straightline=True):
    """Embed the network in the plane.

    Parameters:
        network (compas.datastructures.network.Network): The network object.

        fix (list): Optional.
            Two fixed points.
            Default is ``None``.

        straightline (bool): Optional.
            Embed using straight lines.
            Default is ``True``.

    Returns:
        bool:
        ``True`` if the embedding was successful.
        ``False`` otherwise.

    Raises:
        ImportError: If NetworkX is not installed.

    Example:

        .. plot::
            :include-source:

            import compas
            from compas.datastructures.network import Network
            from compas.datastructures.network.algorithms import embed_network_in_plane

            network = Network.from_obj(compas.get_data('fink.obj'))
            embedding = network.copy()

            fix = (1, 12)

            if embed_network_in_plane(embedding, fix=fix):

                points = []
                for key in embedding:
                    points.append({
                        'pos': embedding.vertex_coordinates(key, 'xy'),
                        'size': 0.3,
                        'text': key,
                        'facecolor': '#ff0000' if key in fix else '#ffffff'
                    })

                lines = []
                for u, v in embedding.edges():
                    lines.append({
                        'start': embedding.vertex_coordinates(u, 'xy'),
                        'end': embedding.vertex_coordinates(v, 'xy')
                    })

                network.plot(
                    vsize=0.3,
                    vertices_on=False,
                    vlabel={key: key for key in fix},
                    ecolor={(u, v): '#cccccc' for u, v in network.edges()},
                    lines=lines,
                    points=points
                )

    """
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX is not installed. Get NetworkX at https://networkx.github.io/.")
        raise
    count = 100
    is_embedded = False
    edges = network.edges()
    while count:
        graph = nx.Graph(edges)
        pos = nx.spring_layout(graph)
        if not are_network_edges_crossed(edges, pos):
            is_embedded = True
            break
        count -= 1
    if not is_embedded:
        return False
    if fix:
        a, b = fix
        vec0 = [network[b][axis] - network[a][axis] for axis in 'xy']
        vec1 = [pos[b][axis] - pos[a][axis] for axis in (0, 1)]
        # rotate
        a = -angle_smallest_vectors_2d(vec0, vec1)
        a = 3.14159 * a / 180
        cosa = cos(a)
        sina = sin(a)
        for key in pos:
            x, y = pos[key]
            pos[key][0] = cosa * x - sina * y
            pos[key][1] = sina * x + cosa * y
        # scale
        l0 = (vec0[0] ** 2 + vec0[1] ** 2) ** 0.5
        l1 = (vec1[0] ** 2 + vec1[1] ** 2) ** 0.5
        scale = l0 / l1
        for key in pos:
            pos[key][0] *= scale
            pos[key][1] *= scale
        # translate
        t = network[fix[0]]['x'] - pos[fix[0]][0], network[fix[0]]['y'] - pos[fix[0]][1]
        for key in pos:
            pos[key][0] += t[0]
            pos[key][1] += t[1]
    # update network vertex coordinates
    for key in network:
        network[key]['x'] = pos[key][0]
        network[key]['y'] = pos[key][1]
    return True


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import compas
    from compas.datastructures.network import Network
    from compas.datastructures.network.algorithms import embed_network_in_plane

    network = Network.from_obj(compas.get_data('fink.obj'))
    embedding = network.copy()

    fix = (1, 12)

    if embed_network_in_plane(embedding, fix=fix):

        points = []
        for key in embedding:
            points.append({
                'pos': embedding.vertex_coordinates(key, 'xy'),
                'size': 0.3,
                'text': key,
                'facecolor': '#ff0000' if key in fix else '#ffffff'
            })

        lines = []
        for u, v in embedding.edges():
            lines.append({
                'start': embedding.vertex_coordinates(u, 'xy'),
                'end': embedding.vertex_coordinates(v, 'xy')
            })

        network.plot(
            vsize=0.3,
            vertices_on=False,
            vlabel={key: key for key in fix},
            ecolor={(u, v): '#cccccc' for u, v in network.edges()},
            lines=lines,
            points=points
        )
