# -*- coding: utf-8 -*-

from brg_rhino.conduits import Conduit

try:
    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Line

    from System.Collections.Generic import List
    from System.Drawing.Color import FromArgb

except ImportError as e:

    import platform
    if platform.system() == 'Windows':
        raise e


__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


class LinesConduit(Conduit):
    """"""
    def __init__(self, lines, thickness=1, color=None):
        super(LinesConduit, self).__init__()
        self.lines = lines
        self.n = len(lines)
        self.thickness = thickness
        color = color or (255, 255, 255)
        self.color = FromArgb(*color)

    def DrawForeground(self, e):
        lines = List[Line](self.n)
        for sp, ep in self.lines:
            lines.Add(Line(Point3d(*sp), Point3d(*ep)))
        e.Display.DrawLines(lines, self.color, self.thickness)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from random import randint
    import time

    points = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(100)]
    lines  = [(points[i], points[i + 1]) for i in range(99)]

    try:
        conduit = LinesConduit(lines)
        conduit.Enabled = True

        for i in range(100):
#            points = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(100)]
#            conduit.lines = [(points[i], points[i + 1]) for i in range(99)]

            conduit.redraw()

            time.sleep(0.1)

    except Exception as e:
        print e

    finally:
        conduit.Enabled = False
        del conduit
