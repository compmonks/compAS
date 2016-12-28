"""This module defines the errors that can occur in the brg_rhino package."""


__author__    = 'Tom Van Mele'
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT license'
__email__     = 'vanmelet@ethz.ch'


class BRGRhinoError(Exception):
    pass


# ==============================================================================
# brg_rhino.geometry
# ==============================================================================


class RhinoGeometryError(BRGRhinoError):
    pass


class RhinoPointError(RhinoGeometryError):
    pass


class RhinoCurveError(RhinoGeometryError):
    pass


class RhinoSurfaceError(RhinoGeometryError):
    pass


class RhinoMeshError(RhinoGeometryError):
    pass


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
