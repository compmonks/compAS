from __future__ import print_function

from math import acos
from math import pi
from math import sqrt
from math import fabs
from math import cos
from math import sin
from math import radians
from math import degrees

from compas.geometry.utilities import multiply_matrix_vector


__author__     = ['Tom Van Mele <vanmelet@ethz.ch>', 'Matthias Rippmann <rippmann@ethz.ch>']
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = '<vanmelet@ethz.ch>'


__all__ = [
    'vector_from_points',
    'plane_from_points',
    'bestfit_plane_from_points',
    'circle_from_points',

    'vector_component',

    'add_vectors',
    'subtract_vectors',
    'scale_vector',
    'scale_vectors',
    'normalize_vector',
    'normalize_vectors',
    'dot_vectors',
    'cross_vectors',

    'length_vector',
    'length_vector_sqrd',

    'distance_point_point',
    'distance_point_point_sqrd',
    'distance_point_line',
    'distance_point_line_sqrd',
    'distance_point_plane',
    'distance_line_line',

    'angles_points',
    'angles_points_degrees',
    'angles_vectors',
    'angles_vectors_degrees',
    'angle_smallest_points',
    'angle_smallest_points_degrees',
    'angle_smallest_vectors',
    'angle_smallest_vectors_degrees',

    'midpoint_line',
    'centroid_points',
    'center_of_mass_polygon',
    'center_of_mass_polyhedron',

    'area_polygon',
    'area_triangle',

    'volume_polyhedron',

    'normal_triangle',
    'normal_polygon',

    'bounding_box',

    'closest_point_in_cloud',
    'closest_point_on_line',
    'closest_point_on_segment',
    'closest_point_on_plane',
    'closest_point_on_polyline',

    'is_colinear',  # is_point_on_line
    'is_coplanar',  # is_point_on_plane, is_polygon_planar
    'is_polygon_convex',
    'is_point_on_plane',
    'is_point_on_line',
    'is_point_on_segment',
    'is_closest_point_on_segment',
    'is_point_on_polyline',
    'is_point_in_triangle',

    'is_intersection_line_line',
    'is_intersection_line_plane',
    'is_intersection_segment_plane',
    'is_intersection_plane_plane',
    'is_intersection_line_triangle',
    'is_intersection_box_box',

    'intersection_line_line',
    'intersection_circle_circle',
    'intersection_line_triangle',
    'intersection_line_plane',
    'intersection_segment_plane',
    'intersection_plane_plane',
    'intersection_plane_plane_plane',

    'intersection_lines',
    'intersection_planes',

    'offset_line',
    'offset_polygon',

    'translate_points',
    'translate_lines',

    'rotate_points',
    'orient_points',

    'mirror_point_point',
    'mirror_points_point',
    'mirror_point_line',
    'mirror_points_line',
    'mirror_point_plane',
    'mirror_points_plane',
    'mirror_vector_vector',

    'reflect_line_plane',
    'reflect_line_triangle',

    'project_point_plane',
    'project_points_plane',
    'project_point_line',
    'project_points_line',
]


# ------------------------------------------------------------------------------
# constructors
# ------------------------------------------------------------------------------


def vector_from_points(a, b):
    """"""
    return b[0] - a[0], b[1] - a[1], b[2] - a[2]


def plane_from_points(a, b, c):
    """Create a plane from three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        b (sequence of float): XYZ coordinates.
        c (sequence of float): XYZ coordinates.

    Returns:
        tuple: base point and normal vector (normalized).
    """
    ab = subtract_vectors(b, a)
    ac = subtract_vectors(c, a)
    n = normalize_vector(cross_vectors(ab, ac))
    return a, n


def bestfit_plane_from_points(points):
    """Fitting a plane to a list of points.

    Parameters:
        points (sequence): A sequence of XYZ coordinates.

    Returns:
        tuple: base point and normal vector (normalized).

    References:
        http://www.ilikebigbits.com/blog/2015/3/2/plane-from-points

    Warning:
        This method will minimize the squares of the residuals as perpendicular
        to the main axis, not the residuals perpendicular to the plane. If the
        residuals are small (i.e. your points all lie close to the resulting plane),
        then this method will probably suffice. However, if your points are more
        spread then this method may not be the best fit.

    """
    centroid = centroid_points(points)

    xx, xy, xz = 0., 0., 0.
    yy, yz, zz = 0., 0., 0.

    for point in points:
        rx, ry, rz = subtract_vectors(point, centroid)
        xx += rx * rx
        xy += rx * ry
        xz += rx * rz
        yy += ry * ry
        yz += ry * rz
        zz += rz * rz

    det_x = yy * zz - yz * yz
    det_y = xx * zz - xz * xz
    det_z = xx * yy - xy * xy

    det_max = max(det_x, det_y, det_z)

    if det_max == det_x:
        a = (xz * yz - xy * zz) / det_x
        b = (xy * yz - xz * yy) / det_x
        normal = (1., a, b)
    elif det_max == det_y:
        a = (yz * xz - xy * zz) / det_y
        b = (xy * xz - yz * xx) / det_y
        normal = (a, 1., b)
    else:
        a = (yz * xy - xz * yy) / det_z
        b = (xz * xy - yz * xx) / det_z
        normal = (a, b, 1.)

    return centroid, normalize_vector(normal)


def circle_from_points(a, b, c):
    """Create a circle from three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        a (sequence of float): XYZ coordinates.
        a (sequence of float): XYZ coordinates.

    Returns:
        tuple: center, radius, normal  of the circle.

    References:
        https://en.wikipedia.org/wiki/Circumscribed_circle

    """
    ab = subtract_vectors(b, a)
    cb = subtract_vectors(b, c)
    ba = subtract_vectors(a, b)
    ca = subtract_vectors(a, c)
    ac = subtract_vectors(c, a)
    bc = subtract_vectors(c, b)
    normal = normalize_vector(cross_vectors(ab, ac))
    d = 2 * length_vector_sqrd(cross_vectors(ba, cb))
    A = length_vector_sqrd(cb) * dot_vectors(ba, ca) / d
    B = length_vector_sqrd(ca) * dot_vectors(ab, cb) / d
    C = length_vector_sqrd(ba) * dot_vectors(ac, bc) / d
    Aa = scale_vector(a, A)
    Bb = scale_vector(b, B)
    Cc = scale_vector(c, C)
    center = add_vectorlist([Aa, Bb, Cc])
    radius = distance_point_point(center, a)
    return center, radius, normal


# ------------------------------------------------------------------------------
# misc
# ------------------------------------------------------------------------------


def vector_component(u, v):
    """Compute the component of u in the direction of v.

    Note:
        This is similar to computing direction cosines, or to the projection of
        a vector onto another vector. See the respective Wikipedia pages for more
        info:

            - `Direction cosine <https://en.wikipedia.org/wiki/Direction_cosine>`_
            - `Vector projection <https://en.wikipedia.org/wiki/Vector_projection>`_

    Parameters:
        u (sequence of float) : XYZ components of the vector.
        v (sequence of float) : XYZ components of the direction.

    Returns:
        tuple: XYZ components of the component.

    Examples:
        >>> vector_component([1, 2, 3], [1, 0, 0])
        [1, 0, 0]
    """
    x = dot_vectors(u, v) / length_vector_sqrd(v)
    return scale_vector(v, x)


# ------------------------------------------------------------------------------
# operations
# ------------------------------------------------------------------------------


# remove?
def add_vectorlist(vectors):
    """Adds multiple 3d vectors

    Parameters:
       vectors (list): set of vectors.

    Returns:
       Tuple: Resulting vector
    """
    x, y, z = zip(*vectors)
    return sum(x), sum(y), sum(z)


def add_vectors(u, v):
    """Adds two vectors.

    Parameters:
        u (tuple, list, Vector): The first vector.
        v (tuple, list, Vector): The second vector.

    Returns:
        Tuple: Resulting vector
    """
    return u[0] + v[0], u[1] + v[1], u[2] + v[2]


def subtract_vectors(u, v):
    """Subtracts the second vector from the first.

    Parameters:
        u (tuple, list, Vector): The first vector.
        v (tuple, list, Vector): The second vector.

    Returns:
        Tuple: Resulting vector
    """
    return u[0] - v[0], u[1] - v[1], u[2] - v[2]


def scale_vector(vector, f):
    """Scales vector by factor

    Parameters:
        vector (sequence of float): The vector.
        f (float): The scale factor.

    Returns:
        list: the scaled vector.

    """
    f = float(f)
    return [vector[0] * f, vector[1] * f, vector[2] * f]


def scale_vectors(vectors, f):
    """Scale a list of vectors by a factor.

    Parameters:
        vectors (sequence of sequence of float): XYZ coordinates of the vectors.
        f (float): the scaling factor.

    Returns:
        list: the scaled vectors.

    """
    return [scale_vector(vector, f) for vector in vectors]


def normalize_vector(vector):
    """normalizes a vector

    Parameters:
        v1 (tuple, list, Vector): The vector.

    Returns:
        Tuple: normalized vector
    """
    l = float(length_vector(vector))
    if l == 0.0:
        return vector
    return vector[0] / l, vector[1] / l, vector[2] / l


def normalize_vectors(vectors):
    return [normalize_vector(vector) for vector in vectors]


def dot_vectors(u, v):
    """Compute the dot product of two vectors.

    Parameters:
        u (tuple, list, Vector): XYZ components of the first vector.
        v (tuple, list, Vector): XYZ components of the second vector.

    Returns:
        float: The dot product of the two vectors.

    Examples:
        >>> dot_vectors([1.0, 0, 0], [2.0, 0, 0])
        2

    See Also:
        :func:`dot_2d`

    """
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def cross_vectors(u, v):
    r"""Compute the cross product of two vectors.

    Parameters:
        u (tuple, list, Vector): XYZ components of the first vector.
        v (tuple, list, Vector): XYZ components of the second vector.

    Returns:
        list: The cross product of the two vectors.

    The xyz components of the cross product of two vectors :math:`\mathbf{u}`
    and :math:`\mathbf{v}` can be computed as the *minors* of the following matrix:

    .. math::
       :nowrap:

        \begin{bmatrix}
        x & y & z \\
        u_{x} & u_{y} & u_{z} \\
        v_{x} & v_{y} & v_{z}
        \end{bmatrix}

    Therefore, the cross product can be written as:

    .. math::
       :nowrap:

        \mathbf{u} \times \mathbf{v}
        =
        \begin{bmatrix}
        u_{y} * v_{z} - u_{z} * v_{y} \\
        u_{z} * v_{x} - u_{x} * v_{z} \\
        u_{x} * v_{y} - u_{y} * v_{x}
        \end{bmatrix}

    Exmaples:
        >>> cross_vectors([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        [0.0, 0.0, 1.0]

    See Also:
        :func:`cross_2d`

    """
    return [u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]]


# ------------------------------------------------------------------------------
# length
# ------------------------------------------------------------------------------


def length_vector(v):
    """Compute the length of a vector.

    Parameters:
        v (sequence of float): XYZ components of the vector.

    Returns:
        float: The length.

    Examples:
        >>> length([2.0, 0.0, 0.0])
        2.0

    See Also:
        :func:`length_2d`

    """
    return sqrt(dot_vectors(v, v))


def length_vector_sqrd(v):
    """Computes the squared length of a vector.

    Parameters:
        vector (sequence): XYZ components of the vector.

    Returns:
        float: The squared length.

    Examples:
        >>> length_sqrd([2.0, 0.0, 0.0])
        4.0

    See Also:
        :func:`length_sqrd_2d`

    """
    return dot_vectors(v, v)


# ------------------------------------------------------------------------------
# distance
# ------------------------------------------------------------------------------


def distance_point_point(a, b):
    """Compute the distance bewteen a and b.

    Parameters:
        a (sequence of float) : XYZ coordinates of point a.
        b (sequence of float) : XYZ coordinates of point b.

    Returns:
        float: distance bewteen a and b.

    Examples:
        >>> distance([0.0, 0.0, 0.0], [2.0, 0.0, 0.0])
        2.0

    See Also:
        :func:`distance_point_point_2d`

    """
    ab = subtract_vectors(b, a)
    return length_vector(ab)


def distance_point_point_sqrd(a, b):
    """Compute the squared distance bewteen points a and b.

    Parameters:
        a (sequence of float) : XYZ coordinates of point a.
        b (sequence of float) : XYZ coordinates of point b.

    Returns:
        float: distance bewteen a and b.

    Examples:
        >>> distance([0.0, 0.0, 0.0], [2.0, 0.0, 0.0])
        4.0

    See Also:
        :func:`distance_point_point_sqrd_2d`

    """
    ab = subtract_vectors(b, a)
    return length_vector_sqrd(ab)


def distance_point_line(point, line):
    """Compute the distance between a point and a line.

    This implementation computes the *right angle distance* from a point P to a
    line defined by points A and B as twice the area of the triangle ABP divided
    by the length of AB.

    Parameters:
        point (list, tuple) : Point location.
        line (list, tuple) : Line defined by two points.

    Returns:
        float : The distance between the point and the line.

    References:
        https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line

    """
    a, b = line
    ab   = subtract_vectors(b, a)
    pa   = subtract_vectors(a, point)
    pb   = subtract_vectors(b, point)
    l    = length_vector(cross_vectors(pa, pb))
    l_ab = length_vector(ab)
    return l / l_ab


def distance_point_line_sqrd(point, line):
    """Compute the squared distance between a point and a line."""
    a, b = line
    ab   = subtract_vectors(b, a)
    pa   = subtract_vectors(a, point)
    pb   = subtract_vectors(b, point)
    l    = length_vector_sqrd(cross_vectors(pa, pb))
    l_ab = length_vector_sqrd(ab)
    return l / l_ab


def distance_point_plane(point, plane):
    r"""Compute the distance from a point to a plane defined by three points.

    The distance from a pioint to a planbe can be computed from the coefficients
    of the equation of the plane and the coordinates of the point.

    Parameters:
        point (list) : Point coordinates.
        plane (tuple) : A point and a vector defining a plane.

    Returns:
        float : Distance between point and plane.

    Note:
        The equation of a plane is

        .. math::

            Ax + By + Cz + D = 0

        where

        .. math::
            :nowrap:

            \begin{align}
                D &= - Ax_0 - Bx_0 - Cz_0 \\
                Q &= (x_0, y_0, z_0) \\
                N &= (A, B, C)
            \end{align}

        with :math:`Q` a point on the plane, and :math:`N` the normal vector at
        that point. The distance of any point :math:`P` to a plane is the
        absolute value of the dot product of the vector from :math:`Q` to :math:`P`
        and the normal at :math:`Q`.

    References:
        http://mathinsight.org/distance_point_plane

    """
    base, normal = plane
    vector = subtract_vectors(point, base)
    return fabs(dot_vectors(vector, normal))


def distance_line_line(l1, l2, tol=0.0):
    """Compute the shortest distance between two lines.

    The distance is the absolute value of the dot product of a unit vector that
    is perpendicular to the two lines, and the vector between two points on the lines.

    If each of the lines is defined by two points (:math:`l_1 = (\mathbf{x_1}, \mathbf{x_2})`,
    :math:`l_2 = (\mathbf{x_3}, \mathbf{x_4})`), then the unit vector that is
    perpendicular to both lines is...


    Parameters:
        l1 (tuple) : Two points defining a line.
        l2 (tuple) : Two points defining a line.

    Returns:
        float : The distance between the two lines.


    References:
        http://mathworld.wolfram.com/Line-LineDistance.html
        https://en.wikipedia.org/wiki/Skew_lines#Distance

    """
    a, b = l1
    c, d = l2
    ab = subtract_vectors(b, a)
    cd = subtract_vectors(d, c)
    ac = subtract_vectors(c, a)
    n = cross_vectors(ab, cd)
    l = length_vector(n)
    if l <= tol:
        return distance_point_point(closest_point_on_line(l1[0], l2), l1[0])
    n = scale_vector(n, 1.0 / l)
    return fabs(dot_vectors(n, ac))


# ------------------------------------------------------------------------------
# angles
# ------------------------------------------------------------------------------


def angles_vectors(u, v):
    """Compute the the 2 angles (radians) formed by a pair of vectors.

    Parameters:
        u (sequence of float) : XYZ components of the first vector.
        v (sequence of float) : XYZ components of the second vector.

    Returns:
        tuple: The two angles in radians.

        The smallest angle is returned first.

    """
    a = angle_smallest_vectors(u, v)
    return a, pi * 2 - a


def angles_vectors_degrees(u, v):
    """Compute the the 2 angles (degrees) formed by a pair of vectors.

    Parameters:
        u (sequence of float) : XYZ components of the first vector.
        v (sequence of float) : XYZ components of the second vector.

    Returns:
        tuple: The two angles in degrees.

        The smallest angle is returned first.

    """
    a = angle_smallest_vectors_degrees(u, v)
    return a, 360. - a


def angles_points(a, b, c):
    """Compute the two angles (radians) define by three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        b (sequence of float): XYZ coordinates.
        c (sequence of float): XYZ coordinates.

    Returns:
        tuple: The two angles in radians.

        The smallest angle in radians is returned first.

    Notes:
        The vectors are defined in the following way

        .. math::

            \mathbf{u} = \mathbf{b} - \mathbf{a} \\
            \mathbf{v} = \mathbf{c} - \mathbf{a}

        Z components may be provided, but are simply ignored.

    """
    u = subtract_vectors(b, a)
    v = subtract_vectors(c, a)
    return angles_vectors(u, v)


def angles_points_degrees(a, b, c):
    """Compute the two angles (degrees) define by three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        b (sequence of float): XYZ coordinates.
        c (sequence of float): XYZ coordinates.

    Returns:
        tuple: The two angles in degrees.

        The smallest angle in degrees is returned first.

    Notes:
        The vectors are defined in the following way

        .. math::

            \mathbf{u} = \mathbf{b} - \mathbf{a} \\
            \mathbf{v} = \mathbf{c} - \mathbf{a}

        Z components may be provided, but are simply ignored.

    """
    return degrees(angles_points(a, b, c))


def angle_smallest_vectors(u, v):
    """Compute the smallest angle (radians) between two vectors.

    Parameters:
        u (sequence of float) : XYZ components of the first vector.
        v (sequence of float) : XYZ components of the second vector.

    Returns:
        float: The smallest angle in radians.

        The angle is always positive.

    Examples:
        >>> angle_smallest([0.0, 1.0, 0.0], [1.0, 0.0, 0.0])
        

    """
    a = dot_vectors(u, v) / (length_vector(u) * length_vector(v))
    a = max(min(a, 1), -1)
    return acos(a)


def angle_smallest_vectors_degrees(u, v):
    """Compute the smallest angle (degrees) between two vectors.

    Parameters:
        u (sequence of float) : XYZ components of the first vector.
        v (sequence of float) : XYZ components of the second vector.

    Returns:
        float: The smallest angle in degrees.

        The angle is always positive.

    Examples:
        >>> angle_smallest([0.0, 1.0, 0.0], [1.0, 0.0, 0.0])
        

    """
    return degrees(angle_smallest_vectors)


def angle_smallest_points(a, b, c):
    """Compute the smallest angle (radians) between the vectors defined by three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        b (sequence of float): XYZ coordinates.
        c (sequence of float): XYZ coordinates.

    Returns:
        float: The smallest angle in radians.

        The angle is always positive.

    Note:
        The vectors are defined in the following way

        .. math::

            \mathbf{u} = \mathbf{b} - \mathbf{a} \\
            \mathbf{v} = \mathbf{c} - \mathbf{a}

        Z components may be provided, but are simply ignored.

    """
    u = subtract_vectors(b, a)
    v = subtract_vectors(c, a)
    return angle_smallest_vectors(u, v)


def angle_smallest_points_degrees(a, b, c):
    """Compute the smallest angle (degrees) between the vectors defined by three points.

    Parameters:
        a (sequence of float): XYZ coordinates.
        b (sequence of float): XYZ coordinates.
        c (sequence of float): XYZ coordinates.

    Returns:
        float: The smallest angle in degrees.

        The angle is always positive.

    Note:
        The vectors are defined in the following way

        .. math::

            \mathbf{u} = \mathbf{b} - \mathbf{a} \\
            \mathbf{v} = \mathbf{c} - \mathbf{a}

        Z components may be provided, but are simply ignored.

    """
    return degrees(angle_smallest_points(a, b, c))

# ------------------------------------------------------------------------------
# average
# ------------------------------------------------------------------------------


def centroid_points(points):
    """Compute the centroid of a set of points.

    Warning:
        Duplicate points are **NOT** removed. If there are duplicates in the
        sequence, they should be there intentionally.

    Parameters:
        points (sequence): A sequence of XYZ coordinates.

    Returns:
        list: XYZ coordinates of the centroid.

    Examples:
        >>> centroid()
    """
    p = float(len(points))
    x, y, z = zip(*points)
    return sum(x) / p, sum(y) / p, sum(z) / p


def midpoint_line(a, b):
    """Compute the midpoint of a line defined by two points.

    Parameters:
        a (sequence of float): XYZ coordinates of the first point.
        b (sequence of float): XYZ coordinates of the second point.

    Returns:
        tuple: XYZ coordinates of the midpoint.

    Examples:
        >>> midpoint()
    """
    return scale_vector(add_vectors(a, b), 0.5)


def center_of_mass_polygon(polygon):
    """Compute the center of mass of a polygon defined as a sequence of points.

    The center of mass of a polygon is the centroid of the midpoints of the edges,
    each weighted by the length of the corresponding edge.

    Parameters:
        polygon (sequence) : A sequence of XYZ coordinates representing the
            locations of the corners of a polygon.

    Returns:
        tuple of floats: The XYZ coordinates of the center of mass.

    Examples:
        >>> pts = [(0.,0.,0.),(1.,0.,0.),(0.,10.,0.)]
        >>> print("Center of mass: {0}".format(center_of_mass(pts)))
        >>> print("Centroid: {0}".format(centroid(pts)))

    """
    L  = 0
    cx = 0
    cy = 0
    cz = 0
    p  = len(polygon)
    for i in range(-1, p - 1):
        p1  = polygon[i]
        p2  = polygon[i + 1]
        d   = distance_point_point(p1, p2)
        cx += 0.5 * d * (p1[0] + p2[0])
        cy += 0.5 * d * (p1[1] + p2[1])
        cz += 0.5 * d * (p1[2] + p2[2])
        L  += d
    cx = cx / L
    cy = cy / L
    cz = cz / L
    return cx, cy, cz


def center_of_mass_polyhedron():
    """Compute the center of mass of a polyhedron"""
    raise NotImplementedError


# ------------------------------------------------------------------------------
# size
# ------------------------------------------------------------------------------


def area_polygon(polygon):
    """Compute the area of a polygon.

    Parameters:
        polygon (sequence): The XYZ coordinates of the vertices/corners of the
            polygon. The vertices are assumed to be in order. The polygon is
            assumed to be closed: the first and last vertex in the sequence should
            not be the same.

    Returns:
        float: The area of the polygon.

    """
    o = centroid_points(polygon)
    u = subtract_vectors(polygon[-1], o)
    v = subtract_vectors(polygon[0], o)
    a = 0.5 * length_vector(cross_vectors(u, v))
    for i in range(0, len(polygon) - 1):
        u = v
        v = subtract_vectors(polygon[i + 1], o)
        a += 0.5 * length_vector(cross_vectors(u, v))
    return a


def area_triangle(triangle):
    """Compute the area of a triangle defined by three points.
    """
    return 0.5 * length_vector(normal_triangle(triangle, False))


def volume_polyhedron(polyhedron):
    r"""Compute the volume of a polyhedron represented by a closed mesh.

    This implementation is based on the divergence theorem, the fact that the
    *area vector* is constant for each face, and the fact that the area of each
    face can be computed as half the length of the cross product of two adjacent
    edge vectors.

    .. math::
        :nowrap:

        \begin{align}
            V  = \int_{P} 1
              &= \frac{1}{3} \int_{\partial P} \mathbf{x} \cdot \mathbf{n} \\
              &= \frac{1}{3} \sum_{i=0}^{N-1} \int{A_{i}} a_{i} \cdot n_{i} \\
              &= \frac{1}{6} \sum_{i=0}^{N-1} a_{i} \cdot \hat n_{i}
        \end{align}


    References:
        http://www.ma.ic.ac.uk/~rn/centroid.pdf

    """
    V = 0
    for fkey in polyhedron.face:
        vertices = polyhedron.face_vertices(fkey, ordered=True)
        if len(vertices) == 3:
            faces = [vertices]
        else:
            faces = []
            for i in range(1, len(vertices) - 1):
                faces.append(vertices[0:1] + vertices[i:i + 2])
        for face in faces:
            a  = polyhedron.vertex_coordinates(face[0])
            b  = polyhedron.vertex_coordinates(face[1])
            c  = polyhedron.vertex_coordinates(face[2])
            ab = subtract_vectors(b, a)
            ac = subtract_vectors(c, a)
            n  = cross_vectors(ab, ac)
            V += dot_vectors(a, n)
    return V / 6.


# ------------------------------------------------------------------------------
# orientation
# ------------------------------------------------------------------------------


def normal_polygon(points, unitized=True):
    """Compute the normal of a polygon defined by a sequence of points.

    Note:
        The points in the list should be unique. For example, the first and last
        point in the list should not be the same.

    Parameters:
        points (sequence): A sequence of points.

    Returns:
        list: The normal vector.

    Raises:
        ValueError: If less than three points are provided.
    """
    p = len(points)
    assert p > 2, "At least three points required"
    nx = 0
    ny = 0
    nz = 0
    o = centroid_points(points)
    a = subtract_vectors(points[-1], o)
    for i in range(p):
        b = subtract_vectors(points[i], o)
        n = cross_vectors(a, b)
        a = b
        nx += n[0]
        ny += n[1]
        nz += n[2]
    if not unitized:
        return nx, ny, nz
    l = length_vector([nx, ny, nz])
    return nx / l, ny / l, nz / l


def _normal_polygon(points, unitized=True):
    """Compute the normal of a polygon defined by a sequence of points.

    Note:
        The points in the list should be unique. For example, the first and last
        point in the list should not be the same.

    Parameters:
        points (sequence): A sequence of points.

    Returns:
        list: The normal vector.

    Raises:
        ValueError: If less than three points are provided.
    """
    p = len(points)
    assert p > 2, "At least three points required"
    nx = 0
    ny = 0
    nz = 0
    for i in range(-1, p - 1):
        p1  = points[i - 1]
        p2  = points[i]
        p3  = points[i + 1]
        v1  = subtract_vectors(p1, p2)
        v2  = subtract_vectors(p3, p2)
        n   = cross_vectors(v1, v2)
        nx += n[0]
        ny += n[1]
        nz += n[2]
    if not unitized:
        return nx, ny, nz
    l = length_vector([nx, ny, nz])
    return nx / l, ny / l, nz / l


def normal_triangle(triangle, unitized=True):
    """Compute the normal vector of a triangle.
    """
    assert len(triangle) == 3, "Three points are required."
    a, b, c = triangle
    ab = subtract_vectors(b, a)
    ac = subtract_vectors(c, a)
    n  = cross_vectors(ab, ac)
    if not unitized:
        return n
    lvec = length_vector(n)
    return n[0] / lvec, n[1] / lvec, n[2] / lvec


# ------------------------------------------------------------------------------
# bounding boxes
# ------------------------------------------------------------------------------


def bounding_box(points):
    """Computes the bounding box of a list of points.
    """
    x, y, z = zip(*points)
    min_x = min(x)
    max_x = max(x)
    min_y = min(y)
    max_y = max(y)
    min_z = min(z)
    max_z = max(z)
    return [(min_x, min_y, min_z),
            (max_x, min_y, min_z),
            (max_x, max_y, min_z),
            (min_x, max_y, min_z),
            (min_x, min_y, max_z),
            (max_x, min_y, max_z),
            (max_x, max_y, max_z),
            (min_x, max_y, max_z)]


# ------------------------------------------------------------------------------
# proximity
# ------------------------------------------------------------------------------


def sort_points(point, cloud):
    """Sorts points of a pointcloud to a point.

    Notes:
        Check kdTree class for an optimized implementation (MR).

    Parameters:
        point (tuple): x,y,z make_blocks point value
        cloud (sequence): A sequence locations in three-dimensional space.

    Returns:
        list (floats): min distances
        list (tuples): sorted points
        list (ints): closest point indices

    Examples:
        >>> sort_points()
    """
    minsq = [distance_point_point_sqrd(p, point) for p in cloud]
    return sorted(zip(minsq, cloud, range(len(cloud))), key=lambda x: x[0])


def closest_point_in_cloud(point, cloud):
    """Calculates the closest point in a pointcloud.

    Notes:
        Check kdTree class for an optimized implementation (MR).

    Parameters:
        point (tuple): x,y,z make_blocks point value
        cloud (sequence): A sequence locations in three-dimensional space.

    Returns:
        float: min distance
        tuple: closest point
        int: closest point index
    """
    data = sort_points(point, cloud)
    return data[0]


def closest_point_on_line(point, line):
    """
    Computes closest point on line to a given point.

    Parameters:
        point (sequence of float): XYZ coordinates.
        line (tuple): Two points defining the line.

    Returns:
        list: XYZ coordinates of closest point.

    See Also:
        :func:`compas.geometry.transformations.project_point_line`

    """
    a, b = line
    ab = subtract_vectors(b, a)
    ap = subtract_vectors(point, a)
    c = vector_component(ap, ab)
    return add_vectors(a, c)


def closest_point_on_segment(point, segment):
    """
    Computes closest point on line segment (p1, p2) to testpoint.

    Parameters:
        point (sequence of float): XYZ coordinates.
        saegment (tuple): Two points defining the segment.

    Returns:
        list: XYZ coordinates of closest point.

    """
    a, b = segment
    p  = closest_point_on_line(point, segment)
    d  = distance_point_point_sqrd(a, b)
    d1 = distance_point_point_sqrd(a, p)
    d2 = distance_point_point_sqrd(b, p)
    if d1 > d or d2 > d:
        if d1 < d2:
            return a
        return b
    return p


def closest_point_on_polyline(point, polyline):
    # should be straight forward using the closest_point_on_line_segment function
    raise NotImplementedError


def closest_point_on_plane(point, plane):
    """
    Compute closest point on a plane to a given point.

    Parameters:
        point (sequenceof float): XYZ coordinates of point.
        plane (tuple): The base point and normal defining the plane.

    Returns:
        (list): XYZ coordinates of the closest point.

    Examples:
        >>> plane = ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        >>> point = [1.0, 2.0, 3.0]
        >>> closest_point_on_plane(point, plane)

    References:
        http://en.wikipedia.org/wiki/Distance_from_a_point_to_a_plane

    """
    base, normal = plane
    x, y, z = base
    a, b, c  = normalize_vector(normal)
    x1, y1, z1 = point
    d = a * x + b * y + c * z
    k = (a * x1 + b * y1 + c * z1 - d) / (a**2 + b**2 + c**2)
    return [x1 - k * a,
            y1 - k * b,
            z1 - k * c]


# ------------------------------------------------------------------------------
# queries
# ------------------------------------------------------------------------------


def is_colinear(a, b, c):
    """Verify if three points are colinear.

    Parameters:
        a (tuple, list, Point): Point 1.
        b (tuple, list, Point): Point 2.
        c (tuple, list, Point): Point 3.

    Returns:
        bool: True if the points are collinear, False otherwise.
    """
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1])  * (c[0] - a[0]) == 0


def is_coplanar(points, tol=0.01):
    """Verify if the points are coplanar.

    Compute the normal vector (cross product) of the vectors formed by the first
    three points. Include one more vector at a time to compute a new normal and
    compare with the original normal. If their cross product is not zero, they
    are not parallel, which means the point are not in the same plane.

    Four points are coplanar if the volume of the tetrahedron defined by them is
    0. Coplanarity is equivalent to the statement that the pair of lines
    determined by the four points are not skew, and can be equivalently stated
    in vector form as (x2 - x0).[(x1 - x0) x (x3 - x2)] = 0.

    Parameters:
        points (sequence): A sequence of locations in three-dimensional space.

    Returns:
        bool: True if the points are coplanar, False otherwise.

    """
    tol2 = tol ** 2
    if len(points) == 4:
        v01 = subtract_vectors(points[1], points[0])
        v02 = subtract_vectors(points[2], points[0])
        v23 = subtract_vectors(points[3], points[0])
        res = dot_vectors(v02, cross_vectors(v01, v23))
        return res**2 < tol2
    # len(points) > 4
    # compare length of cross product vector to tolerance
    u = subtract_vectors(points[1], points[0])
    v = subtract_vectors(points[2], points[1])
    w = cross_vectors(u, v)
    for i in range(1, len(points) - 2):
        u = v
        v = subtract_vectors(points[i + 2], points[i + 1])
        wuv = cross_vectors(w, cross_vectors(u, v))
        if wuv[0]**2 > tol2 or wuv[1]**2 > tol2 or wuv[2]**2 > tol2:
            return False
    return True


def is_polygon_convex(polygon):
    """Verify if a polygon is convex.

    Parameters:
        polygon (sequence of sequence of floats): The XYZ coordinates of the
            corners of the polygon.

    Note:
        Use this function for *spatial* polygons.
        If the polygon is in a horizontal plane, use :func:`compas.geometry.planar.is_polygon_convex`
        instead.

    See Also:
        :func:`compas.geometry.planar.is_polygon_convex`

    """
    c = center_of_mass_polygon(polygon)
    for i in range(-1, len(polygon) - 1):
        p0 = polygon[i]
        p1 = polygon[i - 1]
        p2 = polygon[i + 1]
        v0 = subtract_vectors(c, p0)
        v1 = subtract_vectors(p1, p0)
        v2 = subtract_vectors(p2, p0)
        a1 = angle_smallest_vectors(v1, v0)
        a2 = angle_smallest_vectors(v0, v2)
        if a1 + a2 > pi:
            return False
    return True


def is_point_on_plane(point, plane, tol=0.0):
    """Verify if a point lies in a plane.

    Parameters:
        point (sequence of float): XYZ coordinates.
        plane (tuple): Base point and normal defining a plane.
        tol (float): Optional. A tolerance. Default is ``0.0``.

    Returns:
        (bool): True if the point is in on the plane, False otherwise.

    """
    d = distance_point_plane(point, plane)
    return d <= tol


def is_point_on_line(point, line, tol=0.0):
    """Verify if a point lies on a line.

    Parameters:
        point (sequence of float): XYZ coordinates.
        line (tuple): Two points defining a line.
        tol (float): Optional. A tolerance. Default is ``0.0``.

    Returns:
        (bool): True if the point is in on the line, False otherwise.

    """
    d = distance_point_line(point, line)
    return d <= tol


def is_point_on_segment(point, segment, tol=0.0):
    """Verify if a point lies on a given line segment.

    Parameters:
        point (sequence of float): XYZ coordinates.
        segment (tuple): Two points defining the line segment.

    Returns:
        (bool): True if the point is on the line segment, False otherwise.

    """
    a, b = segment
    if not is_point_on_line(point, segment, tol=tol):
        return False
    d_ab = distance_point_point(a, b)
    if d_ab == 0:
        return False
    d_pa = distance_point_point(a, point)
    d_pb = distance_point_point(b, point)
    if d_pa + d_pb <= d_ab + tol:
        return True
    return False


def is_closest_point_on_segment(point, segment, tol=0.0, return_point=False):
    """Verify if the closest point on the line of a segment is on the segment.

    Parameters:
        point (sequence of float): XYZ coordinates of the point.
        segment (tuple): Two points defining the line segment.
        tol (float): Optional. A tolerance. Default is ``0.0``.
        return_point (bool): Optional. If ``True`` return the closest point.
            Default is ``False``.

    Returns:
        (bool/tuple): the point if the point is in on the line, False otherwise.
        (bool): True if the point is in on the line, False otherwise.

    """
    a, b = segment
    v = subtract_vectors(b, a)
    d_ab = distance_point_point_sqrd(a, b)
    if d_ab == 0:
        return
    u = sum((point[i] - a[i]) * v[i] for i in range(3)) / d_ab
    c = a[0] + u * v[0], a[1] + u * v[1], a[2] + u * v[2]
    d_ac = distance_point_point_sqrd(a, c)
    d_bc = distance_point_point_sqrd(b, c)
    if d_ac + d_bc <= d_ab + tol:
        if return_point:
            return c
        return True
    return False


def is_point_on_polyline(point, polyline, tol=0.0):
    """Verify if a point is on a polyline.

    Parameters:
        point (sequence of float): XYZ coordinates.
        polyline (sequence of sequence of float): XYZ coordinates of the points
            of the polyline.
        tol (float): Optional. The tolerance. Default is ``0.0``.

    Returns:
        bool: ``True`` if the point is on the polyline. ``False`` otherwise.

    """
    for i in xrange(len(polyline) - 1):
        a = polyline[i]
        b = polyline[i + 1]
        c = closest_point_on_segment(point, (a, b))
        if distance_point_point(point, c) <= tol:
            return True
    return False


def is_point_in_triangle(point, triangle):
    """Verify if a point is in the interior of a triangle.

    Parameters:
        point (sequence of float): XYZ coordinates.
        triangle (sequence of sequence of float): XYZ coordinates of the triangle corners.

    Returns:
        (bool): True if the point is in inside the triangle, False otherwise.

    Note:
        Should the point be in the same plane as the triangle?

    See Also:
        :func:`compas.geometry.planar.is_point_in_triangle`

    """
    def is_on_same_side(p1, p2, segment):
        a, b = segment
        v = vector_from_points(a, b)
        c1 = cross_vectors(v, vector_from_points(a, p1))
        c2 = cross_vectors(v, vector_from_points(a, p2))
        if dot_vectors(c1, c2) >= 0:
            return True
        return False
    a, b, c = triangle
    if is_on_same_side(point, a, (b, c)) and \
       is_on_same_side(point, b, (a, c)) and \
       is_on_same_side(point, c, (a, b)):
        return True
    return False


def is_point_in_circle(point, circle):
    center, radius, normal = circle
    if is_point_on_plane(point, (center, normal)):
        return distance_point_point(point, center) <= radius
    return False


def is_intersection_line_line(ab, cd, epsilon=1e-6):
    """Verifies if two lines intersection in one point.

    Parameters:
        ab: (tuple): A sequence of XYZ coordinates of two 3D points representing
            two points on the line.
        cd: (tuple): A sequence of XYZ coordinates of two 3D points representing
            two points on the line.

    Returns:
        True (bool): if the lines intersect in one point, False is the lines are
        skew, parallel or lie on top of each other.
    """
    a, b = ab
    c, d = cd

    line_vector_1 = normalize_vector(vector_from_points(a, b))
    line_vector_2 = normalize_vector(vector_from_points(c, d))
    # check for parallel lines
    print(abs(dot_vectors(line_vector_1, line_vector_2)))
    if abs(dot_vectors(line_vector_1, line_vector_2)) > 1.0 - epsilon:
        return False
    # check for intersection
    d_vector = cross_vectors(line_vector_1, line_vector_2)
    if dot_vectors(d_vector, subtract_vectors(c, a)) == 0:
        return True
    return False


def is_intersection_segment_plane(segment, plane, epsilon=1e-6):
    """Verify if a line segment intersects with a plane.

    Parameters:
        segment (tuple): Two points defining the line segment.
        plane (tuple): The base point and normal defining the plane.
    Returns:
        (bool): True if the line segment intersects with the plane, False otherwise.

    """
    pt1 = segment[0]
    pt2 = segment[1]
    p_cent = plane[0]
    p_norm = plane[1]

    v1 = subtract_vectors(pt2, pt1)
    dot = dot_vectors(p_norm, v1)

    if abs(dot) > epsilon:
        v2 = subtract_vectors(pt1, p_cent)
        fac = - dot_vectors(p_norm, v2) / dot
        if fac > 0. and fac < 1.:
            return True
        return False
    else:
        return False


def is_intersection_line_plane(line, plane, epsilon=1e-6):
    """Verify if a line (continuous ray) intersects with a plane.

    Parameters:
        line (tuple): Two points defining the line.
        plane (tuple): The base point and normal defining the plane.
    Returns:
        (bool): True if the line intersects with the plane, False otherwise.

    """
    pt1 = line[0]
    pt2 = line[1]
    p_norm = plane[1]

    v1 = subtract_vectors(pt2, pt1)
    dot = dot_vectors(p_norm, v1)

    if abs(dot) > epsilon:
        return True
    return False


def is_intersection_plane_plane(plane1, plane2, epsilon=1e-6):
    """Computes the intersection of two planes

    Parameters:
        plane1 (tuple): The base point and normal (normalized) defining the 1st plane.
        plane2 (tuple): The base point and normal (normalized) defining the 2nd plane.
    Returns:
        (bool): True if the planes intersect, False otherwise.

    """
    # check for parallelity of planes
    if abs(dot_vectors(plane1[1], plane2[1])) > 1 - epsilon:
        return False
    return True


def is_intersection_line_triangle(line, triangle, epsilon=1e-6):
    """Verifies if a line (ray) intersects with a triangle.

    Note:
        Based on the Moeller Trumbore intersection algorithm.

    Parameters:
        line (tuple): Two points defining the line.
        triangle (sequence of sequence of float): XYZ coordinates of the triangle corners.

    Returns:
        True if the line (ray) intersects with the triangle, False otherwise.

    Note:
        The line is treated as continues, directed ray and not as line segment with a start and end point
    """
    a, b, c = triangle
    v1 = subtract_vectors(line[1], line[0])
    p1 = line[0]
    # Find vectors for two edges sharing V1
    e1 = subtract_vectors(b, a)
    e2 = subtract_vectors(c, a)
    # Begin calculating determinant - also used to calculate u parameter
    p = cross_vectors(v1, e2)
    # if determinant is near zero, ray lies in plane of triangle
    det = dot_vectors(e1, p)
    # NOT CULLING
    if(det > - epsilon and det < epsilon):
        return False
    inv_det = 1.0 / det
    # calculate distance from V1 to ray origin
    t = subtract_vectors(p1, a)
    # Calculate u parameter and make_blocks bound
    u = dot_vectors(t, p) * inv_det
    # The intersection lies outside of the triangle
    if(u < 0.0 or u > 1.0):
        return False
    # Prepare to make_blocks v parameter
    q = cross_vectors(t, e1)
    # Calculate V parameter and make_blocks bound
    v = dot_vectors(v1, q) * inv_det
    # The intersection lies outside of the triangle
    if(v < 0.0 or u + v  > 1.0):
        return False
    t = dot_vectors(e2, q) * inv_det
    if t > epsilon:
        return True
    # No hit
    return False


def is_intersection_box_box(box_1, box_2):
    """Checks if two boxes are intersecting in 3D.

    Parameters:
        box_1 (list of tuples): list of 8 points (bottom: 0,1,2,3 top: 4,5,6,7)
        box_2 (list of tuples): list of 8 points (bottom: 0,1,2,3 top: 4,5,6,7)

    Returns:
        bool: True if the boxes intersect, False otherwise.

    Examples:

        .. code-block:: python

            x, y, z = 1, 1, 1
            box_a = [
                (0.0, 0.0, 0.0),
                (x,   0.0, 0.0),
                (x,   y,   0.0),
                (0.0, y,   0.0),
                (0.0, 0.0, z),
                (x,   0.0, z),
                (x,   y,   z),
                (0.0, y,   z)
            ]
            box_b = [
                (0.5, 0.5, 0.0),
                (1.5, 0.5, 0.0),
                (1.5, 1.5, 0.0),
                (0.5, 1.5, 0.0),
                (0.5, 0.5, 1.0),
                (1.5, 0.5, 1.0),
                (1.5, 1.5, 1.0),
                (0.5, 1.5, 1.0)
            ]
            if is_box_intersecting_box(box_a, box_b):
                print("intersection found")
            else:
                print("no intersection found")

    Warning:
        Does not check if one box is completely enclosed by the other.

    """
    # all edges of box one
    edges = [
        (box_1[0], box_1[1]),
        (box_1[1], box_1[2]),
        (box_1[2], box_1[3]),
        (box_1[3], box_1[0])
    ]
    edges += [
        (box_1[4], box_1[5]),
        (box_1[5], box_1[6]),
        (box_1[6], box_1[7]),
        (box_1[7], box_1[4])
    ]
    edges += [
        (box_1[0], box_1[4]),
        (box_1[1], box_1[5]),
        (box_1[2], box_1[6]),
        (box_1[3], box_1[7])
    ]
    # triangulation of box two
    tris = [
        (box_2[0], box_2[1], box_2[2]),
        (box_2[0], box_2[2], box_2[3])
    ]  # bottom
    tris += [
        (box_2[4], box_2[5], box_2[6]),
        (box_2[4], box_2[6], box_2[7])
    ]  # top
    tris += [
        (box_2[0], box_2[4], box_2[7]),
        (box_2[0], box_2[7], box_2[3])
    ]  # side 1
    tris += [
        (box_2[0], box_2[1], box_2[5]),
        (box_2[0], box_2[5], box_2[4])
    ]  # side 2
    tris += [
        (box_2[1], box_2[2], box_2[6]),
        (box_2[1], box_2[6], box_2[5])
    ]  # side 3
    tris += [
        (box_2[2], box_2[3], box_2[7]),
        (box_2[2], box_2[7], box_2[6])
    ]  # side 4
    # checks for edge triangle intersections
    intx = False
    for pt1, pt2 in edges:
        for tri in tris:
            for line in [(pt1, pt2), (pt2, pt1)]:
                test_pt = intersection_line_triangle(line, tri)
                if test_pt:
                    if is_point_on_segment(test_pt, line):
                        # intersection found
                        intx = True
                        break
            else:
                continue
            break
        else:
            continue
        break
    return intx


# ==============================================================================
# intersections
# ==============================================================================

def intersection_line_line(ab, cd):
    """Computes the intersection of two continuous lines. If the two lines are
    skew the points marking the shortest distance between both lines are computed.

    Parameters:
        ab: (tuple): A sequence of XYZ coordinates of two 3D points representing
            two points on the line.
        cd: (tuple): A sequence of XYZ coordinates of two 3D points representing
            two points on the line.

    Returns:
        point (tuple), point (tuple) as list:
        The two points marking the shortest distance between both lines.

        None, None (list): If the two lines are parallel.

    Note:

        To check if two lines intersect in one point:

        .. code-block:: python

            point_1, point_2 = intersection_line_line(ab, cd)
            if cmp(point_1,point_2):
                print('The two lines intersect')
            else:
                print('The two lines do not intersect')

        Alternative: is_intersection_line_line
    """
    a, b = ab
    c, d = cd

    line_vector_1 = vector_from_points(a, b)
    line_vector_2 = vector_from_points(c, d)
    d_vector = cross_vectors(line_vector_1, line_vector_2)

    normal_1 = cross_vectors(line_vector_1, d_vector)
    normal_2 = cross_vectors(line_vector_2, d_vector)
    plane_1 = (a, normal_1)
    plane_2 = (c, normal_2)

    intx_point_line_1 = intersection_line_plane(ab, plane_2)
    intx_point_line_2 = intersection_line_plane(cd, plane_1)

    return [intx_point_line_1, intx_point_line_2]


def intersection_circle_circle():
    raise NotImplementedError


def intersection_line_triangle(line, triangle, epsilon=1e-6):
    """
    Computes the intersection point of a line (ray) and a triangle
    based on the Moeller Trumbore intersection algorithm

    Parameters:
        line (tuple): Two points defining the line.
        triangle (sequence of sequence of float): XYZ coordinates of the triangle corners.

    Returns:
        point (tuple) if the line (ray) intersects with the triangle, None otherwise.

    Note:
        The line is treated as continues, directed ray and not as line segment with a start and end point
    """
    a, b, c = triangle
    v1 = subtract_vectors(line[1], line[0])
    p1 = line[0]
    # Find vectors for two edges sharing V1
    e1 = subtract_vectors(b, a)
    e2 = subtract_vectors(c, a)
    # Begin calculating determinant - also used to calculate u parameter
    p = cross_vectors(v1, e2)
    # if determinant is near zero, ray lies in plane of triangle
    det = dot_vectors(e1, p)
    # NOT CULLING
    if(det > - epsilon and det < epsilon):
        return None
    inv_det = 1.0 / det
    # calculate distance from V1 to ray origin
    t = subtract_vectors(p1, a)
    # Calculate u parameter and make_blocks bound
    u = dot_vectors(t, p) * inv_det
    # The intersection lies outside of the triangle
    if(u < 0.0 or u > 1.0):
        return None
    # Prepare to make_blocks v parameter
    q = cross_vectors(t, e1)
    # Calculate V parameter and make_blocks bound
    v = dot_vectors(v1, q) * inv_det
    # The intersection lies outside of the triangle
    if(v < 0.0 or u + v  > 1.0):
        return None
    t = dot_vectors(e2, q) * inv_det
    if t > epsilon:
        return add_vectors(p1, scale_vector(v1, t))
    # No hit
    return None


def intersection_line_plane(line, plane, epsilon=1e-6):
    """Computes the intersection point of a line (ray) and a plane

    Parameters:
        line (tuple): Two points defining the line.
        plane (tuple): The base point and normal defining the plane.

    Returns:
        point (tuple) if the line (ray) intersects with the plane, None otherwise.

    """
    pt1 = line[0]
    pt2 = line[1]
    p_cent = plane[0]
    p_norm = plane[1]

    v1 = subtract_vectors(pt2, pt1)
    dot = dot_vectors(p_norm, v1)

    if abs(dot) > epsilon:
        v2 = subtract_vectors(pt1, p_cent)
        fac = -dot_vectors(p_norm, v2) / dot
        vec = scale_vector(v1, fac)
        return add_vectors(pt1, vec)
    else:
        return None


def intersection_segment_plane(segment, plane, epsilon=1e-6):
    """Computes the intersection point of a line segment and a plane

    Parameters:
        segment (tuple): Two points defining the line segment.
        plane (tuple): The base point and normal defining the plane.

    Returns:
        point (tuple) if the line segment intersects with the plane, None otherwise.

    """
    pt1 = segment[0]
    pt2 = segment[1]
    p_cent = plane[0]
    p_norm = plane[1]

    v1 = subtract_vectors(pt2, pt1)
    dot = dot_vectors(p_norm, v1)

    if abs(dot) > epsilon:
        v2 = subtract_vectors(pt1, p_cent)
        fac = -dot_vectors(p_norm, v2) / dot
        if fac > 0. and fac < 1.:
            vec = scale_vector(v1, fac)
            return add_vectors(pt1, vec)
        return None
    else:
        return None


def intersection_plane_plane(plane1, plane2, epsilon=1e-6):
    """Computes the intersection of two planes

    Parameters:
        plane1 (tuple): The base point and normal (normalized) defining the 1st plane.
        plane2 (tuple): The base point and normal (normalized) defining the 2nd plane.

    Returns:
        line (tuple): Two points defining the intersection line. None if planes are parallel.

    """
    # check for parallelity of planes
    if abs(dot_vectors(plane1[1], plane2[1])) > 1 - epsilon:
        return None
    vec = cross_vectors(plane1[1], plane2[1])  # direction of intersection line
    p1 = plane1[0]
    vec_inplane = cross_vectors(vec, plane1[1])
    p2 = add_vectors(p1, vec_inplane)
    px1 = intersection_line_plane((p1, p2), plane2)
    px2 = add_vectors(px1, vec)
    return (px1, px2)


def intersection_plane_plane_plane(plane1, plane2, plane3, epsilon=1e-6):
    """Computes the intersection of three planes

    Parameters:
        plane1 (tuple): The base point and normal (normalized) defining the 1st plane.
        plane2 (tuple): The base point and normal (normalized) defining the 2nd plane.

    Returns:
        point (tuple): The intersection point. None if two (or all three) planes are parallel.

    Note:
        Currently this only computes the intersection point. E.g.: If two planes
        are parallel the intersection lines are not computed. see:
        http://geomalgorithms.com/Pic_3-planes.gif
    """
    line = intersection_plane_plane(plane1, plane2, epsilon)
    if not line:
        return None
    pt = intersection_line_plane(line, plane3, epsilon)
    if pt:
        return pt
    return None


def intersection_lines():
    raise NotImplementedError


def intersection_planes():
    raise NotImplementedError


# ==============================================================================
# transformations
# ==============================================================================


def translate_points(points, vector):
    return [add_vectors(point, vector) for point in points]


def translate_lines(lines, vector):
    sps, eps = zip(*lines)
    sps = translate_points(sps, vector)
    eps = translate_points(eps, vector)
    return zip(sps, eps)


def offset_line(line, distance, normal=[0., 0., 1.]):
    """Offset a line by a distance

    Parameters:
        line (tuple): Two points defining the line.
        distances (float or tuples of floats): The offset distance as float.
            A single value determines a constant offset. Alternatively, two
            offset values for the start and end point of the line can be used to
            a create variable offset.
        normal (tuple): The normal of the offset plane.

    Returns:
        offset line (tuple): Two points defining the offset line.

    Examples:

        .. code-block:: python

            line = [(0.0, 0.0, 0.0), (3.0, 3.0, 0.0)]

            distance = 0.2 # constant offset
            line_offset = offset_line(line, distance)
            print(line_offset)

            distance = [0.2, 0.1] # variable offset
            line_offset = offset_line(line, distance)
            print(line_offset)

    """
    pt1, pt2 = line[0], line[1]
    vec = subtract_vectors(pt1, pt2)
    dir_vec = normalize_vector(cross_vectors(vec, normal))

    if isinstance(distance, list):
        distances = distance
    else:
        distances = [distance, distance]

    vec_pt1 = scale_vector(dir_vec, distances[0])
    vec_pt2 = scale_vector(dir_vec, distances[1])
    pt1_new = add_vectors(pt1, vec_pt1)
    pt2_new = add_vectors(pt2, vec_pt2)
    return pt1_new, pt2_new


def offset_polygon(polygon, distance):
    """Offset a polygon (closed) by a distance.

    Parameters:
        polygon (sequence of sequence of floats): The XYZ coordinates of the
            corners of the polygon. The first and last coordinates must be identical.
        distance (float or list of tuples of floats): The offset distance as float.
            A single value determines a constant offset globally. Alternatively, pairs of local
            offset values per line segment can be used to create variable offsets.
            Distance > 0: offset to the outside, distance < 0: offset to the inside

    Returns:
        offset polygon (sequence of sequence of floats): The XYZ coordinates of the
            corners of the offset polygon. The first and last coordinates are identical.

    Note:
        The offset direction is determined by the normal of the polygon. The
        algorithm works also for spatial polygons that do not perfectly fit a plane.

    Examples:

        .. code-block:: python

            polygon = [
                (0.0, 0.0, 0.0),
                (3.0, 0.0, 1.0),
                (3.0, 3.0, 2.0),
                (1.5, 1.5, 2.0),
                (0.0, 3.0, 1.0),
                (0.0, 0.0, 0.0)
                ]

            distance = 0.5 # constant offset
            polygon_offset = offset_polygon(polygon, distance)
            print(polygon_offset)

            distance = [
                (0.1, 0.2),
                (0.2, 0.3),
                (0.3, 0.4),
                (0.4, 0.3),
                (0.3, 0.1)
                ] # variable offset
            polygon_offset = offset_polygon(polygon, distance)
            print(polygon_offset)

    """
    normal = normal_polygon(polygon)

    if isinstance(distance, list):
        distances = distance
        if len(distances) < len(polygon):
            distances = distances + [distances[-1]] * (len(polygon) - len(distances) - 1)
    else:
        distances = [[distance, distance]] * len(polygon)

    lines = [polygon[i:i + 2] for i in xrange(len(polygon[:-1]))]
    lines_offset = []
    for i, line in enumerate(lines):
        lines_offset.append(offset_line(line, distances[i], normal))

    polygon_offset = []
    for i in xrange(len(lines_offset)):
        intx_pt1, intx_pt2 = intersection_line_line(lines_offset[i - 1], lines_offset[i])
        if intx_pt1 and intx_pt2:
            polygon_offset.append(centroid_points([intx_pt1, intx_pt2]))
        else:
            polygon_offset.append(lines_offset[i][0])

    polygon_offset.append(polygon_offset[0])
    return polygon_offset


# ------------------------------------------------------------------------------
# rotate and orient
# ------------------------------------------------------------------------------


def rotate_points_degrees(points, axis, angle, origin=None):
    """Rotates points around an arbitrary axis in 3D (degrees).

    Parameters:
        points (sequence of sequence of float): XYZ coordinates of the points.
        axis (sequence of float): The rotation axis.
        angle (float): the angle of rotation in degrees.
        origin (sequence of float): Optional. The origin of the rotation axis.
            Default is ``[0.0, 0.0, 0.0]``.

    Returns:
        list: the rotated points

    References:
        https://en.wikipedia.org/wiki/Rotation_matrix

    """
    return rotate_points(points, axis, radians(angle), origin)


def rotate_points(points, axis, angle, origin=None):
    """Rotates points around an arbitrary axis in 3D (radians).

    Parameters:
        points (sequence of sequence of float): XYZ coordinates of the points.
        axis (sequence of float): The rotation axis.
        angle (float): the angle of rotation in radians.
        origin (sequence of float): Optional. The origin of the rotation axis.
            Default is ``[0.0, 0.0, 0.0]``.

    Returns:
        list: the rotated points

    References:
        https://en.wikipedia.org/wiki/Rotation_matrix

    """
    if not origin:
        origin = [0.0, 0.0, 0.0]
    # rotation matrix
    x, y, z = normalize_vector(axis)
    c = cos(angle)
    t = (1 - cos(angle))
    s = sin(angle)
    R = [
        [t * x * x + c    , t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c    , t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c]
    ]
    # translate points
    points = translate_points(points, scale_vector(origin, -1.0))
    # rotate points
    points = [multiply_matrix_vector(R, point) for point in points]
    # translate points back
    points = translate_points(points, origin)
    return points


def orient_points(points, reference_plane=None, target_plane=None):
    """Orient points from one plane to another.

    Parameters:
        points (sequence of sequence of float): XYZ coordinates of the points.
        reference_plane (tuple): Base point and normal defining a reference plane.
        target_plane (tuple): Base point and normal defining a target plane.

    Returns:
        points (sequence of sequence of float): XYZ coordinates of the oriented points.

    Note:
        This function is useful to orient a planar problem in the xy-plane to simplify
        the calculation (see example).

    Examples:

        .. code-block:: python

            from compas.geometry.spatial import orient_points
            from compas.geometry.planar import intersection_segment_segment_2d

            reference_plane = [(0.57735,0.57735,0.57735),(1.0, 1.0, 1.0)]

            line_a = [
                (0.288675,0.288675,1.1547),
                (0.866025,0.866025, 0.)
                ]

            line_b = [
                (1.07735,0.0773503,0.57735),
                (0.0773503,1.07735,0.57735)
                ]

            # orient lines to lie in the xy-plane
            line_a_xy = orient_points(line_a, reference_plane)
            line_b_xy = orient_points(line_b, reference_plane)

            # compute intersection in 2d in the xy-plane
            intx_point_xy = intersection_segment_segment_2d(line_a_xy, line_b_xy)

            # re-orient resulting intersection point to lie in the reference plane
            intx_point = orient_points([intx_point_xy], target_plane=reference_plane)[0]
            print(intx_point)

    """

    if not target_plane:
        target_plane = [(0., 0., 0.,), (0., 0., 1.)]

    if not reference_plane:
        reference_plane = [(0., 0., 0.,), (0., 0., 1.)]

    vec_rot = cross_vectors(reference_plane[1], target_plane[1])
    angle = angle_smallest_vectors(reference_plane[1], target_plane[1])
    points = rotate_points(points, vec_rot, angle, reference_plane[0])
    vec_trans = subtract_vectors(target_plane[0], reference_plane[0])
    points = translate_points(points, vec_trans)
    return points


# ------------------------------------------------------------------------------
# mirror
# ------------------------------------------------------------------------------


def mirror_point_point(point, mirror):
    """Mirror a point about a point.

    Parameters:
        point (sequence of float): XYZ coordinates of the point to mirror.
        mirror (sequence of float): XYZ coordinates of the mirror point.

    """
    return add_vectors(mirror, subtract_vectors(mirror, point))


def mirror_points_point(points, mirror):
    """Mirror multiple points about a point."""
    return [mirror_point_point(point, mirror) for point in points]


def mirror_point_line(point, line):
    pass


def mirror_points_line(points, line):
    pass


def mirror_point_plane(point, plane):
    pass


def mirror_points_plane(points, plane):
    pass


def mirror_vector_vector(v1, v2):
    """Mirrors vector about vector.

    Parameters:
        v1 (tuple, list, Vector): The vector.
        v2 (tuple, list, Vector): The normalized vector as mirror axis

    Returns:
        Tuple: mirrored vector

    Resources:
        http://math.stackexchange.com/questions/13261/how-to-get-a-reflection-vector
    """
    return subtract_vectors(v1, scale_vector(v2, 2 * dot_vectors(v1, v2)))


def reflect_line_plane(line, plane, epsilon=1e-6):
    """Reflects a line at plane.

    Parameters:
        line (tuple): Two points defining the line.
        plane (tuple): The base point and normal (normalized) defining the plane.

    Returns:
        line (tuple): The reflected line starting at the reflection point on the plane,
        None otherwise.

    Note:
        The directions of the line and plane are important! The line will only be
        reflected if it points (direction start -> end) in the direction of the plane
        and if the line intersects with the front face of the plane (normal direction
        of the plane).

    Resources:
        http://math.stackexchange.com/questions/13261/how-to-get-a-reflection-vector

    Examples:

        .. code-block:: python

            from math import pi, sin, cos, radians

            from compas.geometry.spatial import rotate_points
            from compas.geometry.spatial import intersection_line_plane
            from compas.geometry.spatial import reflect_line_plane

            # planes
            mirror_plane = [(0.0, 0.0, 0.0),(1.0, 0.0, 0.0)]
            projection_plane = [(40.0, 0.0, 0.0),(1.0, 0.0, 0.0)]

            # initial line (starting laser ray)
            line = [(30., 0.0, -10.0),(0.0, 0.0, 0.0)]

            dmax = 75 # steps (resolution)
            angle = radians(12)  # max rotation of mirror plane in degrees
            axis_z = [0.0, 0.0, 1.0] # rotation z-axis of mirror plane
            axis_y = [0.0, 1.0, 0.0] # rotation y-axis of mirror plane

            polyline_projection = []
            for i in range(dmax):
                plane_norm = rotate_points([mirror_plane[1]], axis_z, angle * sin(i / dmax * 2 * pi))[0]
                plane_norm = rotate_points([plane_norm], axis_y, angle * sin(i / dmax * 4 * pi))[0]
                reflected_line = reflect_line_plane(line, [mirror_plane[0],plane_norm])
                if not reflected_line:
                    continue
                intx_pt = intersection_line_plane(reflected_line,projection_plane)
                if intx_pt:
                    polyline_projection.append(intx_pt)

            print(polyline_projection)


    Note:
        This example visualized in Rhino:


    .. image:: /_images/reflect_line_plane.*

    """
    intx_pt = intersection_line_plane(line, plane, epsilon)
    if not intx_pt:
        return None
    vec_line = subtract_vectors(line[1], line[0])
    vec_reflect = mirror_vector_vector(vec_line, plane[1])
    if angle_smallest_vectors(plane[1], vec_reflect) > 0.5 * pi:
        return None
    return [intx_pt, add_vectors(intx_pt, vec_reflect)]


def reflect_line_triangle(line, triangle, epsilon=1e-6):
    """Reflects a line at a triangle.

    Parameters:
        line (tuple): Two points defining the line.
        triangle (sequence of sequence of float): XYZ coordinates of the triangle corners.

    Returns:
        line (tuple): The reflected line starting at the reflection point on the plane,
        None otherwise.

    Note:
        The directions of the line and triangular face are important! The line will only be
        reflected if it points (direction start -> end) in the direction of the triangular
        face and if the line intersects with the front face of the triangular face (normal
        direction of the face).

    Examples:

        .. code-block:: python

            # tetrahedron points
            pt1 = (0.0, 0.0, 0.0)
            pt2 = (6.0, 0.0, 0.0)
            pt3 = (3.0, 5.0, 0.0)
            pt4 = (3.0, 2.0, 4.0)

            # triangular tetrahedron faces
            tris = []
            tris.append([pt4,pt2,pt1])
            tris.append([pt4,pt3,pt2])
            tris.append([pt4,pt1,pt3])
            tris.append([pt1,pt2,pt3])

            # initial line (starting ray)
            line = [(1.0,1.0,0.0),(1.0,1.0,1.0)]

            # start reflection cycle inside the prism
            polyline = []
            polyline.append(line[0])
            for i in range(10):
                for tri in tris:
                    reflected_line = reflect_line_triangle(line, tri)
                    if reflected_line:
                        line = reflected_line
                        polyline.append(line[0])
                        break

            print(polyline)


    Note:
        This example visualized in Rhino:


    .. image:: /_images/reflect_line_triangle.*

    """
    intx_pt = intersection_line_triangle(line, triangle, epsilon)
    if not intx_pt:
        return None
    vec_line = subtract_vectors(line[1], line[0])
    vec_normal = normal_triangle(triangle, unitized=True)
    vec_reflect = mirror_vector_vector(vec_line, vec_normal)
    if angle_smallest_vectors(vec_normal, vec_reflect) > 0.5 * pi:
        return None
    return [intx_pt, add_vectors(intx_pt, vec_reflect)]


# ------------------------------------------------------------------------------
# project (not the same as pull) => projection direction is required
# ------------------------------------------------------------------------------


def project_point_plane(point, plane):
    """Project a point onto a plane.

    The projection is in the direction perpendicular to the plane.
    The projected point is thus the closest point on the plane to the original
    point.

    Parameters:
        point (sequence of float): XYZ coordinates of the original point.
        plane (tuple): Base poin.t and normal vector defining the plane

    Returns:
        list: XYZ coordinates of the projected point.

    Examples:

        >>> from compas.geometry.transformations import project_point_plane
        >>> point = [3.0, 3.0, 3.0]
        >>> plane = ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])  # the XY plane
        >>> project_point_plane(point, plane)
        [3.0, 3.0, 3.0]


    References:
        http://stackoverflow.com/questions/8942950/how-do-i-find-the-orthogonal-projection-of-a-point-onto-a-plane
        http://math.stackexchange.com/questions/444968/project-a-point-in-3d-on-a-given-plane

    """
    base, normal = plane
    normal = normalize_vector(normal)
    vector = subtract_vectors(point, base)
    snormal = scale_vector(normal, dot_vectors(vector, normal))
    return subtract_vectors(point, snormal)


def project_points_plane(points, plane):
    """Project multiple points onto a plane.

    Parameters:
        points (sequence of sequence of float): Cloud of XYZ coordinates.
        plane (tuple): Base point and normal vector defining the projection plane.

    Returns:
        list of list: The XYZ coordinates of the projected points.

    See Also:
        :func:`project_point_plane`

    """
    return [project_point_plane(point, plane) for point in points]


def project_point_line(point, line):
    """Project a point onto a line.

    Parameters:
        point (sequence of float): XYZ coordinates.
        line (tuple): Two points defining a line.

    Returns:
        list: XYZ coordinates of the projected point.

    References:
        https://en.wikibooks.org/wiki/Linear_Algebra/Orthogonal_Projection_Onto_a_Line

    """
    a, b = line
    ab = subtract_vectors(b, a)
    ap = subtract_vectors(point, a)
    c = vector_component(ap, ab)

    return add_vectors(a, c)


def project_points_line(points, line):
    """Project multiple points onto a line."""
    return [project_point_line(point, line) for point in points]


# ==============================================================================
# best-fit(ting)
# ==============================================================================

# ==============================================================================
# Debugging
# ==============================================================================


if __name__ == '__main__':

    import timeit

    vectors = [[float(i), float(i * 2), float(i ** 2)] for i in range(1000)]

    print(add_vectorlist(vectors))
    print(reduce(add_vectors, vectors))

    t1 = timeit.timeit('add_vectorlist(vectors)', 'from __main__ import add_vectorlist, vectors', number=10000)
    t2 = timeit.timeit('reduce(add_vectors, vectors)', 'from __main__ import add_vectors, vectors', number=10000)

    print(t1 / 10000)
    print(t2 / 10000)
