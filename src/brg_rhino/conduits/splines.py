# -*- coding: utf-8 -*-
# @Date    : 2016-03-21 09:50:20
# @Author  : Tom Van Mele (vanmelet@ethz.ch)
# @Version : $Id$

import Rhino
import scriptcontext as sc

from Rhino.Geometry import Point3d
from Rhino.Geometry import Line

from System.Collections.Generic import List
from System.Drawing.Color import FromArgb


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'Apache License, Version 2.0'
__version__    = '0.1'
__email__      = 'vanmelet@ethz.ch'
__status__     = 'Development'
__date__       = 'Oct 14, 2014'


class SplinesConduit(Rhino.Display.DisplayConduit):
    """"""
    def __init__(self, points, lines, splines,
                 thickness=1,
                 spline_thickness=5,
                 color=None,
                 spline_color=None):
        super(SplinesConduit, self).__init__()
        self.points = points
        self.lines = lines
        self.splines = splines
        self.l = len(lines)
        self.thickness = thickness
        self.spline_thickness = spline_thickness
        color = color or (255, 0, 0)
        spline_color = spline_color or (0, 0, 255)
        self.color = FromArgb(*color)
        self.spline_color = FromArgb(*spline_color)

    def DrawForeground(self, e):
        lines = List[Line](self.l)
        for i, j in self.lines:
            sp = self.points[i]
            ep = self.points[j]
            lines.Add(Line(Point3d(*sp), Point3d(*ep)))
        e.Display.DrawLines(lines, self.color, self.thickness)
        for i, (u, v) in enumerate(self.splines):
            sp = self.points[u]
            ep = self.points[v]
            th = self.spline_thickness[i]
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), self.spline_color, th)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from random import randint
    import time

    points    = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(10)]
    lines     = [(i, i + 1) for i in range(0, 4)]
    splines   = [(i, i + 1) for i in range(5, 9)]
    thickness = [2 * i for i in range(len(splines))]

    try:
        conduit = SplinesConduit(points, lines, splines, thickness=1, spline_thickness=thickness)
        conduit.Enabled = True

        for i in range(100):
            conduit.points = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(10)]

            sc.doc.Views.Redraw()
            time.sleep(0.1)
            Rhino.RhinoApp.Wait()

    except Exception as e:
        print e

    finally:
        conduit.Enabled = False
        del conduit
