"""A Toolbar providing an interface to common mesh tools."""

from brg.geometry.elements.polyhedron import Polyhedron
from brg_rhino.datastructures.mesh import RhinoMesh

from brg.datastructures.mesh.algorithms.tri.subdivision import loop_subdivision

from brg.datastructures.mesh.algorithms.subdivision import quad_subdivision
from brg.datastructures.mesh.algorithms.subdivision import doosabin_subdivision
from brg.datastructures.mesh.algorithms.subdivision import _catmullclark_subdivision

import brg_rhino.utilities as rhino

try:
    import rhinoscriptsyntax as rs
except ImportError as e:
    import platform
    if platform.system() == 'Windows':
        raise e


__author__    = 'Tom Van Mele'
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT license'
__email__     = 'vanmelet@ethz.ch'


class MeshTools(object):
    """"""

    def __init__(self):
        self.mesh = None
        # read settings from settings file
        self.settings = {}
        # get layer structure from ui file
        self.layers = {'MeshTools' : {'layers': {
            'Mesh': {'layers': {}},
            'Subd': {'layers': {
                'QuadMesh' : {'layers' : {}},
                'LoopMesh' : {'layers' : {}},
                'DooSabinMesh' : {'layers' : {}},
                'CatmullClarkMesh' : {'layers' : {}},
            }},
        }}}

    # script => -_RunPythonScript ResetEngine (from brg_rhino.datastructures.toolbars.meshtools import MeshTools;mtools = MeshTools();mtools.init())
    def init(self):
        # reload settings from previous session on `init`
        rhino.create_layers(self.layers)
        rhino.clear_layers(self.layers)

    def from_xxx(self):
        options = ['mesh', 'surface', 'polyhedron', 'obj', 'json']
        option = rs.GetString('From what ...', options[0], options)
        if option not in options:
            return
        if option == 'mesh':
            guid = rhino.select_mesh()
            if guid:
                self.mesh = RhinoMesh.from_guid(guid)
                self.mesh.name = 'Mesh'
                self.mesh.layer = 'MeshTools::Mesh'
                self.mesh.draw(show_faces=False)
        if option == 'surface':
            guid = rhino.select_surface()
            if guid:
                self.mesh = RhinoMesh.from_surface(guid)
                self.mesh.name = 'Mesh'
                self.mesh.layer = 'MeshTools::Mesh'
                self.mesh.draw(show_faces=False)
        if option == 'polyhedron':
            faces = ['f4', 'f6', 'f8', 'f12', 'f20']
            f = rs.GetString('Number of faces ...', faces[0], faces)
            if f not in faces:
                return
            f = int(f[1:])
            tet = Polyhedron.generate(f)
            if tet:
                self.mesh = RhinoMesh.from_vertices_and_faces(tet.vertices, tet.faces)
                self.mesh.name = 'Mesh'
                self.mesh.layer = 'MeshTools::Mesh'
                self.mesh.draw(show_faces=False)
        if option == 'obj':
            raise NotImplementedError
        if option == 'json':
            raise NotImplementedError

    def to_xxx(self):
        options = ['obj', 'json']
        option = rs.GetString('Export format ...', options[0], options)
        if option not in options:
            return
        if option == 'obj':
            raise NotImplementedError
        if option == 'json':
            raise NotImplementedError

    def modify(self):
        """Modfy geometry and/or topology of a mesh."""
        mesh = self.mesh
        options = ['Move', 'MoveVertex', 'MoveFace', 'MoveEdge', 'SplitEdge', 'SwapEdge', 'CollapseEdge']
        option = rs.GetString('Mesh Operation ...', options[0], options)
        if option not in options:
            return
        if option == 'Move':
            raise NotImplementedError
        if option == 'MoveVertex':
            raise NotImplementedError
        if option == 'MoveFace':
            raise NotImplementedError
        if option == 'MoveEdge':
            raise NotImplementedError
        if option == 'SplitEdge':
            raise NotImplementedError
        if option == 'SwapEdge':
            raise NotImplementedError
        if option == 'CollapseEdge':
            raise NotImplementedError

    def modify_tri(self):
        """Modfy geometry and/or topology of a triangle mesh.

        The avaialable operations are specific to triangle meshes, because they
        use the properties of the triangular geometry and topology to simplify
        and speed up the operations. The effect of the operations is also slightly
        different, because they preserve the triangular nature of the mesh.

        Raises:
            Exception :
                If the selected mesh is not a triangle mesh.
        """
        mesh = self.mesh
        if not mesh.is_trimesh():
            raise Exception('TriMesh operations are only available for trianlge meshes.')
        options = ['SplitEdge', 'SwapEdge', 'CollapseEdge']
        option = rs.GetString('TriMesh Operation ...', options[0], options)
        if option not in options:
            return
        if option == 'SplitEdge':
            raise NotImplementedError
        if option == 'SwapEdge':
            raise NotImplementedError
        if option == 'CollapseEdge':
            raise NotImplementedError

    def subd(self):
        """Subdivide the control mesh and draw as separate subd mesh."""
        options = ['Quad', 'DooSabin', 'CatmullClark']
        option = rs.GetString('Subdivision scheme ...', options[0], options)
        if option not in options:
            return
        loops = ['k1', 'k2', 'k3', 'k4', 'k5']
        k = rs.GetString('Subd level ...', loops[0], loops)
        if k not in loops:
            return
        k = int(k[1:])
        if option == 'Quad':
            # Quad subdivision.
            # Interpolation
            subd = quad_subdivision(self.mesh, k=k)
            subd.name = 'QuadMesh'
            subd.layer = 'MeshTools::Subd::QuadMesh'
            subd.draw(show_vertices=False, show_edges=False)
        if option == 'DooSabin':
            # Doo-Sabin scheme for quad subdivision.
            # Approximation
            subd = doosabin_subdivision(self.mesh, k=k)
            subd.name = 'DooSabinMesh'
            subd.layer = 'MeshTools::Subd::DooSabinMesh'
            subd.draw(show_vertices=False, show_edges=False)
        if option == 'CatmullClark':
            # Catmull-Clark scheme for quad subdivision.
            # Approximation
            subd = _catmullclark_subdivision(self.mesh, k=k)
            subd.name = 'CatmullClarkMesh'
            subd.layer = 'MeshTools::Subd::CatmullClarkMesh'
            subd.draw(show_vertices=False, show_edges=False)

    def subd_tri(self):
        """Apply subdivision algorithms that are specific to trianlge meshes.

        Raises:
            Exception :
                If the selected mesh is not a tiangle mesh.
        """
        if not self.mesh.is_trimesh():
            raise Exception('TriSubdivision schemes are only available for trianlge meshes.')
        options = ['Loop']
        option = rs.GetString('TriSubdivision scheme ...', options[0], options)
        if option not in options:
            return
        loops = ['k1', 'k2', 'k3', 'k4', 'k5']
        k = rs.GetString('Subd level ...', loops[0], loops)
        if k not in loops:
            return
        k = int(k[1:])
        if option == 'Loop':
            # Loop subdivision.
            # Approximation
            subd = loop_subdivision(self.mesh, k=k)
            subd.name = 'LoopMesh'
            subd.layer = 'MeshTools::Subd::LoopMesh'
            subd.draw(show_vertices=False, show_edges=False)

    def smooth(self):
        options = ['umbrella', 'area', 'forcedensity']
        option = rs.GetString('Weighting scheme...', options[0], options)
        if option not in options:
            return
        if option == 'umbrella':
            raise NotImplementedError
        if option == 'area':
            raise NotImplementedError
        if option == 'forcedensity':
            raise NotImplementedError

    def smooth_tri(self):
        options = ['cotangent']
        option = rs.GetString('Tri Weighting scheme...', options[0], options)
        if option not in options:
            return
        if option == 'cotangent':
            raise NotImplementedError

    def relax(self):
        raise NotImplementedError


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from brg.files.rui import Rui
    from brg.files.rui import get_macros

    toolbars = [{'name' : 'MeshTools', 'items' : [
        {'type': 'normal', 'left_macro' : 'init', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'from_xxx', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'to_xxx', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'modify', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'subdivide', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'smooth', 'right_macro' : None},
        {'type': 'normal', 'left_macro' : 'relax', 'right_macro' : None},
    ]}]
    toolbargroups = [{'name' : 'MeshTools', 'toolbars' : ['MeshTools', ]}]

    rui = Rui('./mtools.rui')

    rui.init()

    macros = get_macros(MeshTools, 'mtools')

    rui.add_macros(macros)
    rui.add_toolbars(toolbars)
    rui.add_toolbargroups(toolbargroups)

    rui.write()
