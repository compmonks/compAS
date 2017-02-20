from collections import deque


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'network_vertex_coloring',
]


def network_vertex_coloring(network):
    """Color the vertices of a network such that no two colors are adjacent.

    Parameters:
        network (brg.datastructures.network.Network): The network object.

    Warning:
        This is a greedy algorithm, so it might be slow for large networks.

    Example:

        .. plot::
            :include-source:

            import brg
            from brg.datastructures.network import Network
            from brg.datastructures.network.algorithms import network_vertex_coloring

            network = Network.from_obj(brg.get_data('grid_irregular.obj'))

            key_color = network_vertex_coloring(network)
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

            network.plot(
                vcolor={key: colors[key_color[key]] for key in network}
            )


    Reference:
        http://scienceblogs.com/goodmath/2007/06/28/graph-coloring-algorithms-1/

    """
    key_to_color = {}
    key_to_degree = {key: network.degree(key) for key in network}
    vertices = sorted(network.vertices(), key=lambda key: key_to_degree[key])
    uncolored = deque(vertices[::-1])
    current_color = 0
    while uncolored:
        a = uncolored.popleft()
        key_to_color[a] = current_color
        colored_with_current = [a]
        for b in uncolored:
            if not any([b in network.halfedge[key] for key in colored_with_current]):
                key_to_color[b] = current_color
                colored_with_current.append(b)
        for key in colored_with_current[1:]:
            uncolored.remove(key)
        current_color += 1
    return key_to_color


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    import brg
    from brg.datastructures.network import Network

    network = Network.from_obj(brg.get_data('grid_irregular.obj'))

    key_color = network_vertex_coloring(network)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    network.plot(
        vcolor={key: colors[key_color[key]] for key in network}
    )
