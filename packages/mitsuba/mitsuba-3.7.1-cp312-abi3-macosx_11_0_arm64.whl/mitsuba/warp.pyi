import drjit.auto.ad

import mitsuba


def square_to_uniform_disk(sample: mitsuba.Point2f) -> mitsuba.Point2f:
    """Uniformly sample a vector on a 2D disk"""

def uniform_disk_to_square(p: mitsuba.Point2f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_disk"""

def square_to_uniform_disk_pdf(p: mitsuba.Point2f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_disk per unit area"""

def uniform_disk_to_square_concentric(p: mitsuba.Point2f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_disk_concentric"""

def square_to_uniform_disk_concentric(sample: mitsuba.Point2f) -> mitsuba.Point2f:
    """Low-distortion concentric square to disk mapping by Peter Shirley"""

def square_to_uniform_square_concentric(sample: mitsuba.Point2f) -> mitsuba.Point2f:
    """
    Low-distortion concentric square to square mapping (meant to be used
    in conjunction with another warping method that maps to the sphere)
    """

def square_to_uniform_disk_concentric_pdf(p: mitsuba.Point2f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_disk per unit area"""

def square_to_uniform_triangle(sample: mitsuba.Point2f) -> mitsuba.Point2f:
    """
    Convert an uniformly distributed square sample into barycentric
    coordinates
    """

def uniform_triangle_to_square(p: mitsuba.Point2f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_triangle"""

def interval_to_tent(sample: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Warp a uniformly distributed sample on [0, 1] to a tent distribution"""

def tent_to_interval(value: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Warp a tent distribution to a uniformly distributed sample on [0, 1]"""

def interval_to_nonuniform_tent(a: drjit.auto.ad.Float, b: drjit.auto.ad.Float, c: drjit.auto.ad.Float, d: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """
    Warp a uniformly distributed sample on [0, 1] to a nonuniform tent
    distribution with nodes ``{a, b, c}``
    """

def square_to_tent(sample: mitsuba.Point2f) -> mitsuba.Point2f:
    """Warp a uniformly distributed square sample to a 2D tent distribution"""

def tent_to_square(value: mitsuba.Point2f) -> mitsuba.Point2f:
    """Warp a uniformly distributed square sample to a 2D tent distribution"""

def square_to_tent_pdf(v: mitsuba.Point2f) -> drjit.auto.ad.Float:
    """Density of square_to_tent per unit area."""

def square_to_uniform_triangle_pdf(p: mitsuba.Point2f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_triangle per unit area."""

def square_to_uniform_sphere(sample: mitsuba.Point2f) -> mitsuba.Vector3f:
    """
    Uniformly sample a vector on the unit sphere with respect to solid
    angles
    """

def uniform_sphere_to_square(sample: mitsuba.Vector3f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_sphere"""

def square_to_uniform_sphere_pdf(v: mitsuba.Vector3f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_sphere() with respect to solid angles"""

def square_to_uniform_spherical_lune(sample: mitsuba.Point2f, n1: mitsuba.Normal3f, n2: mitsuba.Normal3f) -> mitsuba.Vector3f:
    """
    Uniformly sample a direction in the two spherical lunes defined by the
    valid boundary directions of two touching faces defined by their
    normals ``n1`` and ``n2``.
    """

def uniform_spherical_lune_to_square(d: mitsuba.Vector3f, n1: mitsuba.Normal3f, n2: mitsuba.Normal3f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_spherical_lune"""

def square_to_uniform_spherical_lune_pdf(d: mitsuba.Vector3f, n1: mitsuba.Normal3f, n2: mitsuba.Normal3f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_spherical_lune() w.r.t. solid angles"""

def square_to_uniform_hemisphere(sample: mitsuba.Point2f) -> mitsuba.Vector3f:
    """
    Uniformly sample a vector on the unit hemisphere with respect to solid
    angles
    """

def uniform_hemisphere_to_square(v: mitsuba.Vector3f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_hemisphere"""

def square_to_uniform_hemisphere_pdf(v: mitsuba.Vector3f) -> drjit.auto.ad.Float:
    """Density of square_to_uniform_hemisphere() with respect to solid angles"""

def square_to_cosine_hemisphere(sample: mitsuba.Point2f) -> mitsuba.Vector3f:
    """
    Sample a cosine-weighted vector on the unit hemisphere with respect to
    solid angles
    """

def cosine_hemisphere_to_square(v: mitsuba.Vector3f) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_cosine_hemisphere"""

def square_to_cosine_hemisphere_pdf(v: mitsuba.Vector3f) -> drjit.auto.ad.Float:
    """Density of square_to_cosine_hemisphere() with respect to solid angles"""

def square_to_uniform_cone(v: mitsuba.Point2f, cos_cutoff: drjit.auto.ad.Float) -> mitsuba.Vector3f:
    """
    Uniformly sample a vector that lies within a given cone of angles
    around the Z axis

    Parameter ``cos_cutoff``:
        Cosine of the cutoff angle

    Parameter ``sample``:
        A uniformly distributed sample on :math:`[0,1]^2`
    """

def uniform_cone_to_square(v: mitsuba.Vector3f, cos_cutoff: drjit.auto.ad.Float) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_cone"""

def square_to_uniform_cone_pdf(v: mitsuba.Vector3f, cos_cutoff: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """
    Density of square_to_uniform_cone per unit area.

    Parameter ``cos_cutoff``:
        Cosine of the cutoff angle
    """

def square_to_beckmann(sample: mitsuba.Point2f, alpha: drjit.auto.ad.Float) -> mitsuba.Vector3f:
    """Warp a uniformly distributed square sample to a Beckmann distribution"""

def beckmann_to_square(v: mitsuba.Vector3f, alpha: drjit.auto.ad.Float) -> mitsuba.Point2f:
    """Inverse of the mapping square_to_uniform_cone"""

def square_to_beckmann_pdf(v: mitsuba.Vector3f, alpha: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Probability density of square_to_beckmann()"""

def square_to_von_mises_fisher(sample: mitsuba.Point2f, kappa: drjit.auto.ad.Float) -> mitsuba.Vector3f:
    """
    Warp a uniformly distributed square sample to a von Mises Fisher
    distribution
    """

def von_mises_fisher_to_square(v: mitsuba.Vector3f, kappa: drjit.auto.ad.Float) -> mitsuba.Point2f:
    """Inverse of the mapping von_mises_fisher_to_square"""

def square_to_von_mises_fisher_pdf(v: mitsuba.Vector3f, kappa: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Probability density of square_to_von_mises_fisher()"""

def square_to_rough_fiber(sample: mitsuba.Point3f, wi: mitsuba.Vector3f, tangent: mitsuba.Vector3f, kappa: drjit.auto.ad.Float) -> mitsuba.Vector3f:
    """
    Warp a uniformly distributed square sample to a rough fiber
    distribution
    """

def square_to_rough_fiber_pdf(v: mitsuba.Vector3f, wi: mitsuba.Vector3f, tangent: mitsuba.Vector3f, kappa: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Probability density of square_to_rough_fiber()"""

def square_to_std_normal(v: mitsuba.Point2f) -> mitsuba.Point2f:
    """
    Sample a point on a 2D standard normal distribution. Internally uses
    the Box-Muller transformation
    """

def square_to_std_normal_pdf(v: mitsuba.Point2f) -> drjit.auto.ad.Float: ...

def interval_to_linear(v0: drjit.auto.ad.Float, v1: drjit.auto.ad.Float, sample: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """
    Importance sample a linear interpolant

    Given a linear interpolant on the unit interval with boundary values
    ``v0``, ``v1`` (where ``v1`` is the value at ``x=1``), warp a
    uniformly distributed input sample ``sample`` so that the resulting
    probability distribution matches the linear interpolant.
    """

def linear_to_interval(v0: drjit.auto.ad.Float, v1: drjit.auto.ad.Float, sample: drjit.auto.ad.Float) -> drjit.auto.ad.Float:
    """Inverse of interval_to_linear"""

def square_to_bilinear(v00: drjit.auto.ad.Float, v10: drjit.auto.ad.Float, v01: drjit.auto.ad.Float, v11: drjit.auto.ad.Float, sample: mitsuba.Point2f) -> tuple[mitsuba.Point2f, drjit.auto.ad.Float]:
    """
    Importance sample a bilinear interpolant

    Given a bilinear interpolant on the unit square with corner values
    ``v00``, ``v10``, ``v01``, ``v11`` (where ``v10`` is the value at
    (x,y) == (0, 0)), warp a uniformly distributed input sample ``sample``
    so that the resulting probability distribution matches the linear
    interpolant.

    The implementation first samples the marginal distribution to obtain
    ``y``, followed by sampling the conditional distribution to obtain
    ``x``.

    Returns the sampled point and PDF for convenience.
    """

def square_to_bilinear_pdf(v00: drjit.auto.ad.Float, v10: drjit.auto.ad.Float, v01: drjit.auto.ad.Float, v11: drjit.auto.ad.Float, sample: mitsuba.Point2f) -> drjit.auto.ad.Float: ...

def bilinear_to_square(v00: drjit.auto.ad.Float, v10: drjit.auto.ad.Float, v01: drjit.auto.ad.Float, v11: drjit.auto.ad.Float, sample: mitsuba.Point2f) -> tuple[mitsuba.Point2f, drjit.auto.ad.Float]:
    """Inverse of square_to_bilinear"""

def interval_to_tangent_direction(n: mitsuba.Normal3f, sample: drjit.auto.ad.Float) -> mitsuba.Vector3f:
    """
    Warp a uniformly distributed sample on [0, 1] to a direction in the
    tangent plane
    """

def tangent_direction_to_interval(n: mitsuba.Normal3f, dir: mitsuba.Vector3f) -> drjit.auto.ad.Float:
    """Inverse of uniform_to_tangent_direction"""
