
from brg.datastructures.mesh.mesh import Mesh
from brg.datastructures.mesh.exceptions import MeshError


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__version__    = '0.1'
__email__      = 'vanmelet@ethz.ch'
__status__     = 'Development'
__date__       = 'Oct 10, 2014'


class TriMesh(Mesh):
    """Data structure for mesh with triangular faces.
    """

    def add_face(self, vertices, fkey=None):
        """Add a face to the mesh.

        The number of vertices of the face should be exactly three. In this
        count the last vertex is ignored if it is the same as the first.

        Parameters:
            vertices (list): The vertices of the face.

        Returns:
            str: The key of the added face.

        Raises:
            MeshError: If the number of vertices is not exactly three.
        """
        if vertices[-1] == vertices[0]:
            del vertices[-1]
        if len(vertices) != 3:
            raise MeshError('The face has too many vertices: {0}'.format(vertices))
        return super(TriMesh, self).add_face(vertices, fkey=fkey)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    from brg.viewers.mesh import MeshViewer
    from brg.geometry.polyhedron import Polyhedron

    polyhedron = Polyhedron.generate(4)
    mesh = TriMesh(polyhedron.vertices, polyhedron.faces)

    viewer = MeshViewer(mesh, 800, 800)
    viewer.camera.zoom = 3.
    viewer.setup()
    viewer.show()
