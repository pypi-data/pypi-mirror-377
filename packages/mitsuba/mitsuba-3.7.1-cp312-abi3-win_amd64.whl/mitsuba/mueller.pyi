from typing import overload

import drjit.auto.ad

import mitsuba


@overload
def depolarizer(value: drjit.auto.ad.Float = 1.0) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of an ideal depolarizer

    Parameter ``value``:
        The value of the (0, 0) element
    """

@overload
def depolarizer(value: mitsuba.Spectrum = 1.0) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def absorber(value: drjit.auto.ad.Float) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of an ideal absorber

    Parameter ``value``:
        The amount of absorption.
    """

@overload
def absorber(value: mitsuba.Spectrum) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def linear_polarizer(value: drjit.auto.ad.Float = 1.0) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of a linear polarizer which transmits
    linear polarization at 0 degrees.

    "Polarized Light" by Edward Collett, Ch. 5 eq. (13)

    Parameter ``value``:
        The amount of attenuation of the transmitted component (1
        corresponds to an ideal polarizer).
    """

@overload
def linear_polarizer(value: mitsuba.Spectrum = 1.0) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def linear_retarder(phase: drjit.auto.ad.Float) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of a linear retarder which has its fast
    axis aligned horizontally.

    This implements the general case with arbitrary phase shift and can be
    used to construct the common special cases of quarter-wave and half-
    wave plates.

    "Polarized Light, Third Edition" by Dennis H. Goldstein, Ch. 6 eq.
    (6.43) (Note that the fast and slow axis were flipped in the first
    edition by Edward Collett.)

    Parameter ``phase``:
        The phase difference between the fast and slow axis
    """

@overload
def linear_retarder(phase: mitsuba.Spectrum) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def right_circular_polarizer() -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of a (right) circular polarizer.

    "Polarized Light and Optical Systems" by Chipman et al. Table 6.2
    """

@overload
def right_circular_polarizer() -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def left_circular_polarizer() -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of a (left) circular polarizer.

    "Polarized Light and Optical Systems" by Chipman et al. Table 6.2
    """

@overload
def left_circular_polarizer() -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def diattenuator(x: drjit.auto.ad.Float, y: drjit.auto.ad.Float) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of a linear diattenuator, which
    attenuates the electric field components at 0 and 90 degrees by 'x'
    and 'y', * respectively.
    """

@overload
def diattenuator(x: mitsuba.Spectrum, y: mitsuba.Spectrum) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def rotator(theta: drjit.auto.ad.Float) -> drjit.auto.ad.Matrix4f:
    """
    Constructs the Mueller matrix of an ideal rotator, which performs a
    counter-clockwise rotation of the electric field by 'theta' radians
    (when facing the light beam from the sensor side).

    To be more precise, it rotates the reference frame of the current
    Stokes vector. For example: horizontally linear polarized light s1 =
    [1,1,0,0] will look like -45˚ linear polarized light s2 = R(45˚) * s1
    = [1,0,-1,0] after applying a rotator of +45˚ to it.

    "Polarized Light" by Edward Collett, Ch. 5 eq. (43)
    """

@overload
def rotator(theta: mitsuba.Spectrum) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def rotated_element(theta: drjit.auto.ad.Float, M: drjit.auto.ad.Matrix4f) -> drjit.auto.ad.Matrix4f:
    """
    Applies a counter-clockwise rotation to the mueller matrix of a given
    element.
    """

@overload
def rotated_element(theta: mitsuba.Spectrum, M: "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>") -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def specular_reflection(cos_theta_i: drjit.auto.ad.Float, eta: drjit.auto.ad.Complex2f) -> drjit.auto.ad.Matrix4f:
    """
    Calculates the Mueller matrix of a specular reflection at an interface
    between two dielectrics or conductors.

    Parameter ``cos_theta_i``:
        Cosine of the angle between the surface normal and the incident
        ray

    Parameter ``eta``:
        Complex-valued relative refractive index of the interface. In the
        real case, a value greater than 1.0 case means that the surface
        normal points into the region of lower density.
    """

@overload
def specular_reflection(cos_theta_i: mitsuba.Spectrum, eta: "drjit::Complex<mitsuba::Spectrum<drjit::DiffArray<2,float>,4> >") -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def specular_transmission(cos_theta_i: drjit.auto.ad.Float, eta: drjit.auto.ad.Float) -> drjit.auto.ad.Matrix4f:
    """
    Calculates the Mueller matrix of a specular transmission at an
    interface between two dielectrics or conductors.

    Parameter ``cos_theta_i``:
        Cosine of the angle between the surface normal and the incident
        ray

    Parameter ``eta``:
        Complex-valued relative refractive index of the interface. A value
        greater than 1.0 in the real case means that the surface normal is
        pointing into the region of lower density.
    """

@overload
def specular_transmission(cos_theta_i: mitsuba.Spectrum, eta: mitsuba.Spectrum) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

def stokes_basis(w: mitsuba.Vector3f) -> mitsuba.Vector3f:
    """
    Gives the reference frame basis for a Stokes vector.

    For light transport involving polarized quantities it is essential to
    keep track of reference frames. A Stokes vector is only meaningful if
    we also know w.r.t. which basis this state of light is observed. In
    Mitsuba, these reference frames are never explicitly stored but
    instead can be computed on the fly using this function.

    Parameter ``forward``:
        Direction of travel for Stokes vector (normalized)

    Returns:
        The (implicitly defined) reference coordinate system basis for the
        Stokes vector traveling along forward.
    """

def rotate_stokes_basis(wi: mitsuba.Vector3f, basis_current: mitsuba.Vector3f, basis_target: mitsuba.Vector3f) -> drjit.auto.ad.Matrix4f:
    """
    Gives the Mueller matrix that aligns the reference frames (defined by
    their respective basis vectors) of two collinear stokes vectors.

    If we have a stokes vector s_current expressed in 'basis_current', we
    can re-interpret it as a stokes vector rotate_stokes_basis(..) * s1
    that is expressed in 'basis_target' instead. For example: Horizontally
    polarized light [1,1,0,0] in a basis [1,0,0] can be interpreted as
    +45˚ linear polarized light [1,0,1,0] by switching to a target basis
    [0.707, -0.707, 0].

    Parameter ``forward``:
        Direction of travel for Stokes vector (normalized)

    Parameter ``basis_current``:
        Current (normalized) Stokes basis. Must be orthogonal to
        ``forward``.

    Parameter ``basis_target``:
        Target (normalized) Stokes basis. Must be orthogonal to
        ``forward``.

    Returns:
        Mueller matrix that performs the desired change of reference
        frames.
    """

def rotate_stokes_basis_m(wi: mitsuba.Vector3f, basis_current: mitsuba.Vector3f, basis_target: mitsuba.Vector3f) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>":
    """
    Gives the Mueller matrix that aligns the reference frames (defined by
    their respective basis vectors) of two collinear stokes vectors.

    If we have a stokes vector s_current expressed in 'basis_current', we
    can re-interpret it as a stokes vector rotate_stokes_basis(..) * s1
    that is expressed in 'basis_target' instead. For example: Horizontally
    polarized light [1,1,0,0] in a basis [1,0,0] can be interpreted as
    +45˚ linear polarized light [1,0,1,0] by switching to a target basis
    [0.707, -0.707, 0].

    Parameter ``forward``:
        Direction of travel for Stokes vector (normalized)

    Parameter ``basis_current``:
        Current (normalized) Stokes basis. Must be orthogonal to
        ``forward``.

    Parameter ``basis_target``:
        Target (normalized) Stokes basis. Must be orthogonal to
        ``forward``.

    Returns:
        Mueller matrix that performs the desired change of reference
        frames.
    """

@overload
def rotate_mueller_basis(M: drjit.auto.ad.Matrix4f, in_forward: mitsuba.Vector3f, in_basis_current: mitsuba.Vector3f, in_basis_target: mitsuba.Vector3f, out_forward: mitsuba.Vector3f, out_basis_current: mitsuba.Vector3f, out_basis_target: mitsuba.Vector3f) -> drjit.auto.ad.Matrix4f:
    """
    Return the Mueller matrix for some new reference frames. This version
    rotates the input/output frames independently.

    This operation is often used in polarized light transport when we have
    a known Mueller matrix 'M' that operates from 'in_basis_current' to
    'out_basis_current' but instead want to re-express it as a Mueller
    matrix that operates from 'in_basis_target' to 'out_basis_target'.

    Parameter ``M``:
        The current Mueller matrix that operates from ``in_basis_current``
        to ``out_basis_current``.

    Parameter ``in_forward``:
        Direction of travel for input Stokes vector (normalized)

    Parameter ``in_basis_current``:
        Current (normalized) input Stokes basis. Must be orthogonal to
        ``in_forward``.

    Parameter ``in_basis_target``:
        Target (normalized) input Stokes basis. Must be orthogonal to
        ``in_forward``.

    Parameter ``out_forward``:
        Direction of travel for input Stokes vector (normalized)

    Parameter ``out_basis_current``:
        Current (normalized) output Stokes basis. Must be orthogonal to
        ``out_forward``.

    Parameter ``out_basis_target``:
        Target (normalized) output Stokes basis. Must be orthogonal to
        ``out_forward``.

    Returns:
        New Mueller matrix that operates from ``in_basis_target`` to
        ``out_basis_target``.
    """

@overload
def rotate_mueller_basis(M: "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>", in_forward: mitsuba.Vector3f, in_basis_current: mitsuba.Vector3f, in_basis_target: mitsuba.Vector3f, out_forward: mitsuba.Vector3f, out_basis_current: mitsuba.Vector3f, out_basis_target: mitsuba.Vector3f) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

@overload
def rotate_mueller_basis_collinear(M: drjit.auto.ad.Matrix4f, forward: mitsuba.Vector3f, basis_current: mitsuba.Vector3f, basis_target: mitsuba.Vector3f) -> drjit.auto.ad.Matrix4f:
    """
    Return the Mueller matrix for some new reference frames. This version
    applies the same rotation to the input/output frames.

    This operation is often used in polarized light transport when we have
    a known Mueller matrix 'M' that operates from 'basis_current' to
    'basis_current' but instead want to re-express it as a Mueller matrix
    that operates from 'basis_target' to 'basis_target'.

    Parameter ``M``:
        The current Mueller matrix that operates from ``basis_current`` to
        ``basis_current``.

    Parameter ``forward``:
        Direction of travel for input Stokes vector (normalized)

    Parameter ``basis_current``:
        Current (normalized) input Stokes basis. Must be orthogonal to
        ``forward``.

    Parameter ``basis_target``:
        Target (normalized) input Stokes basis. Must be orthogonal to
        ``forward``.

    Returns:
        New Mueller matrix that operates from ``basis_target`` to
        ``basis_target``.
    """

@overload
def rotate_mueller_basis_collinear(M: "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>", forward: mitsuba.Vector3f, basis_current: mitsuba.Vector3f, basis_target: mitsuba.Vector3f) -> "drjit::Matrix<mitsuba::Spectrum<drjit::DiffArray<2,float>,4>,4>": ...

def unit_angle(a: mitsuba.Vector3f, b: mitsuba.Vector3f) -> drjit.auto.ad.Float: ...
