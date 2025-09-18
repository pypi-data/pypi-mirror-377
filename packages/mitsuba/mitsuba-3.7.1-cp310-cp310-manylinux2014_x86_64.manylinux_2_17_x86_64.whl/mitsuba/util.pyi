from collections.abc import Mapping

import mi




class SceneParameters(Mapping):
    """
    Dictionary-like object that references various parameters used in a Mitsuba
    scene graph. Parameters can be read and written using standard syntax
    (``parameter_map[key]``). The class exposes several non-standard functions,
    specifically :py:meth:`~mitsuba.SceneParameters.update()`, and
    :py:meth:`~mitsuba.SceneParameters.keep()`.
    """

    def __init__(self, properties=None, hierarchy=None):
        """
        Private constructor (use
        :py:func:`mitsuba.traverse()` instead)
        """

    def copy(self): ...

    def __contains__(self, key: str): ...

    def __getitem__(self, key: str): ...

    def __setitem__(self, key: str, value): ...

    def __delitem__(self, key: str) -> None: ...

    def __len__(self) -> int: ...

    def __repr__(self) -> str: ...

    def __iter__(self): ...

    def items(self): ...

    def keys(self): ...

    def flags(self, key: str):
        """Return parameter flags"""

    def set_dirty(self, key: str):
        """
        Marks a specific parameter and its parent objects as dirty. A subsequent call
        to :py:meth:`~mitsuba.SceneParameters.update()` will refresh their internal
        state.

        This method should rarely be called explicitly. The
        :py:class:`~mitsuba.SceneParameters` will detect most operations on
        its values and automatically flag them as dirty. A common exception to
        the detection mechanism is the :py:meth:`~drjit.scatter` operation which
        needs an explicit call to :py:meth:`~mitsuba.SceneParameters.set_dirty()`.
        """

    def update(self, values: Optional[Mapping] = None) -> list[tuple[Any, set]]:
        """
        This function should be called at the end of a sequence of writes
        to the dictionary. It automatically notifies all modified Mitsuba
        objects and their parent objects that they should refresh their
        internal state. For instance, the scene may rebuild the kd-tree
        when a shape was modified, etc.

        The return value of this function is a list of tuples where each tuple
        corresponds to a Mitsuba node/object that is updated. The tuple's first
        element is the node itself. The second element is the set of keys that
        the node is being updated for.

        Parameter ``values`` (``dict``):
            Optional dictionary-like object containing a set of keys and values
            to be used to overwrite scene parameters. This operation will happen
            before propagating the update further into the scene internal state.
        """

    def keep(self, keys: None | str | list[str]) -> None:
        """
        Reduce the size of the dictionary by only keeping elements,
        whose keys are defined by 'keys'.

        Parameter ``keys`` (``None``, ``str``, ``[str]``):
            Specifies which parameters should be kept. Regex are supported to define
            a subset of parameters at once. If set to ``None``, all differentiable
            scene parameters will be loaded.
        """

    __abstractmethods__: frozenset = ...

def traverse(node: mi.Object) -> SceneParameters:
    """
    Traverse a node of Mitsuba's scene graph and return a dictionary-like
    object that can be used to read and write associated scene parameters.

    See also :py:class:`mitsuba.SceneParameters`.
    """

def render(scene: mi.Scene, params: Any = None, sensor: Union[int, mi.Sensor] = 0, integrator: mi.Integrator = None, seed: mi.UInt32 = 0, seed_grad: int = 0, spp: int = 0, spp_grad: int = 0) -> mi.TensorXf:
    """
    This function provides a convenient high-level interface to differentiable
    rendering algorithms in Mi. The function returns a rendered image that can
    be used in subsequent differentiable computation steps. At any later point,
    the entire computation graph can be differentiated end-to-end in either
    forward or reverse mode (i.e., using ``dr.forward()`` and
    ``dr.backward()``).

    Under the hood, the differentiation operation will be intercepted and routed
    to ``Integrator.render_forward()`` or ``Integrator.render_backward()``,
    which evaluate the derivative using either naive AD or a more specialized
    differential simulation.

    Note the default implementation of this functionality relies on naive
    automatic differentiation (AD), which records a computation graph of the
    primal rendering step that is subsequently traversed to propagate
    derivatives. This tends to be relatively inefficient due to the need to
    track intermediate program state. In particular, it means that
    differentiation of nontrivial scenes at high sample counts will often run
    out of memory. Integrators like ``rb`` (Radiative Backpropagation) and
    ``prb`` (Path Replay Backpropagation) that are specifically designed for
    differentiation can be significantly more efficient.

    Parameter ``scene`` (``mi.Scene``):
        Reference to the scene being rendered in a differentiable manner.

    Parameter ``params``:
       An optional container of scene parameters that should receive gradients.
       This argument isn't optional when computing forward mode derivatives. It
       should be an instance of type ``mi.SceneParameters`` obtained via
       ``mi.traverse()``. Gradient tracking must be explicitly enabled on these
       parameters using ``dr.enable_grad(params['parameter_name'])`` (i.e.
       ``render()`` will not do this for you). Furthermore, ``dr.set_grad(...)``
       must be used to associate specific gradient values with parameters if
       forward mode derivatives are desired. When the scene parameters are
       derived from other variables that have gradient tracking enabled,
       gradient values should be propagated to the scene parameters by calling
       ``dr.forward_to(params, dr.ADFlag.ClearEdges)`` before calling this
       function.

    Parameter ``sensor`` (``int``, ``mi.Sensor``):
        Specify a sensor or a (sensor index) to render the scene from a
        different viewpoint. By default, the first sensor within the scene
        description (index 0) will take precedence.

    Parameter ``integrator`` (``mi.Integrator``):
        Optional parameter to override the rendering technique to be used. By
        default, the integrator specified in the original scene description will
        be used.

    Parameter ``seed`` (``mi.UInt32``)
        This parameter controls the initialization of the random number
        generator during the primal rendering step. It is crucial that you
        specify different seeds (e.g., an increasing sequence) if subsequent
        calls should produce statistically independent images (e.g. to
        de-correlate gradient-based optimization steps).

    Parameter ``seed_grad`` (``mi.UInt32``)
        This parameter is analogous to the ``seed`` parameter but targets the
        differential simulation phase. If not specified, the implementation will
        automatically compute a suitable value from the primal ``seed``.

    Parameter ``spp`` (``int``):
        Optional parameter to override the number of samples per pixel for the
        primal rendering step. The value provided within the original scene
        specification takes precedence if ``spp=0``.

    Parameter ``spp_grad`` (``int``):
        This parameter is analogous to the ``seed`` parameter but targets the
        differential simulation phase. If not specified, the implementation will
        copy the value from ``spp``.
    """

def convert_to_bitmap(data, uint8_srgb=True):
    """
    Convert the RGB image in `data` to a `Bitmap`. `uint8_srgb` defines whether
    the resulting bitmap should be translated to a uint8 sRGB bitmap.
    """

def write_bitmap(filename, data, write_async=True, quality=-1):
    """Write the RGB image in `data` to a PNG/EXR/.. file."""

def cornell_box():
    """
    Returns a dictionary containing a description of the Cornell Box scene.
    """

def variant_context(*args) -> None:
    """
    Temporarily override the active variant. Arguments are interpreted as
    they are in :func:`mitsuba.set_variant`.
    """

scoped_set_variant = variant_context
