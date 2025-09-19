from __future__ import annotations

import functools
import inspect
import logging
import re
import sys
import typing
from collections import ChainMap
from collections import namedtuple
from collections.abc import Callable
from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import _MISSING_TYPE
from dataclasses import Field
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from textwrap import dedent
from types import FrameType
from typing import Annotated
from typing import Any
from typing import Literal
from typing import Protocol
from typing import dataclass_transform
from typing import overload

from docnote import DocnoteConfig
from docnote import Note
from docnote import docnote

from templatey._forwardrefs import ForwardRefGeneratingNamespaceLookup
from templatey._forwardrefs import ForwardRefLookupKey
from templatey._forwardrefs import extract_frame_scope_id
from templatey._forwardrefs import resolve_forward_references
from templatey._signature import TemplateSignature
from templatey._types import Content
from templatey._types import DynamicClassSlot
from templatey._types import InterfaceAnnotationFlavor
from templatey._types import Slot
from templatey._types import Var
from templatey.interpolators import NamedInterpolator
from templatey.parser import InterpolationConfig
from templatey.parser import LiteralTemplateString
from templatey.parser import TemplateInstanceContentRef
from templatey.parser import TemplateInstanceDataRef
from templatey.parser import TemplateInstanceVariableRef

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from templatey.environments import AsyncTemplateLoader
    from templatey.environments import SyncTemplateLoader


class VariableEscaper(Protocol):

    def __call__(self, value: str) -> str:
        """Variable escaper functions accept a single positional
        argument: the value of the variable to escape. It then does any
        required escaping and returns the final string.
        """
        ...


class ContentVerifier(Protocol):

    def __call__(self, value: str) -> Literal[True]:
        """Content verifier functions accept a single positional
        argument: the value of the content to verify. It does any
        verification, and then returns True if the content was okay,
        or raises BlockedContentValue if the content was not acceptable.

        Note that we raise instead of trying to escape for two reasons:
        1.. We don't really know what to replace it with. This is also
            true with variables, but:
        2.. We expect that content is coming from -- if not trusted,
            then at least authoritative -- sources, and therefore, we
            should fail loudly, because it gives the author a chance to
            correct the problem before it becomes user-facing.
        """
        ...


class InterpolationPrerenderer[T](Protocol):

    def __call__(
            self,
            value: Annotated[
                T,
                Note(
                    '''The value of the variable or content. A value of
                    ``None`` indicates that the value is intended to be
                    omitted, but you may still provide a fallback
                    instead.
                    ''')]
            ) -> str | None:
        """Interpolation prerenderers give you a chance to modify the
        rendered result of a particular content or variable value, omit
        it entirely, or provide a fallback for missing values.

        Prerenderers are applied before formatting, escaping, and
        verification, and the result of the prerenderer is used to
        determine whether or not the value should be included in the
        result. If your prerenderer returns ``None``, the parameter will
        be completely omitted (including any prefix or suffix).
        """
        ...


@dataclass(slots=True)
class FieldConfig[T]:
    prerenderer: InterpolationPrerenderer[T] | None = None


# The following is adapted directly from typeshed. We did some formatting
# updates, and inserted our prerenderer param.
if sys.version_info >= (3, 14):
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            ) -> _T: ...
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            ) -> _T: ...
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            ) -> Any: ...

# This is technically only valid for >=3.10, but we require that anyways
else:
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            ) -> _T: ...
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            ) -> _T: ...
    @overload
    def template_field[_T](
            field_config: FieldConfig[_T] = ...,
            /, *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            ) -> Any: ...


@docnote(DocnoteConfig(include_in_docs=False))
def template_field(
        field_config: FieldConfig | None = None,
        /, *,
        prerenderer: InterpolationPrerenderer | None = None,
        metadata: Mapping[Any, Any] | None = None,
        **field_kwargs):
    if field_config is None:
        field_config = FieldConfig()

    if metadata is None:
        metadata = {'templatey.field_config': field_config}

    else:
        metadata = {
            **metadata,
            'templatey.field_config': field_config}

    return field(**field_kwargs, metadata=metadata)


# The following is adapted directly from typeshed. We did some formatting
# updates, and inserted our prerenderer param.
if sys.version_info >= (3, 14):
    @overload
    def param[_T](
            *,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> _T: ...
    @overload
    def param[_T](
            *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> _T: ...
    @overload
    def param[_T](
            *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            doc: str | None = None,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> Any: ...

# This is technically only valid for >=3.10, but we require that anyways
else:
    @overload
    def param[_T](
            *,
            default: _T,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> _T: ...
    @overload
    def param[_T](
            *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Callable[[], _T],
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> _T: ...
    @overload
    def param[_T](
            *,
            default: Literal[_MISSING_TYPE.MISSING] = ...,
            default_factory: Literal[_MISSING_TYPE.MISSING] = ...,
            init: bool = True,
            repr: bool = True,
            hash: bool | None = None,
            compare: bool = True,
            metadata: Mapping[Any, Any] | None = None,
            kw_only: bool | Literal[_MISSING_TYPE.MISSING] = ...,
            prerenderer: InterpolationPrerenderer[_T] | None = None,
            ) -> Any: ...


# DEPRECATED. Use ``template_field`` instead.
@docnote(DocnoteConfig(include_in_docs=False))
def param(
        *,
        prerenderer: InterpolationPrerenderer | None = None,
        metadata: Mapping[Any, Any] | None = None,
        **field_kwargs):
    field_config = FieldConfig(prerenderer=prerenderer)

    if metadata is None:
        metadata = {'templatey.field_config': field_config}

    else:
        metadata = {
            **metadata,
            'templatey.field_config': field_config}

    return field(**field_kwargs, metadata=metadata)


@dataclass_transform(field_specifiers=(param, field, Field))
def template[T: type](  # noqa: PLR0913
        config: TemplateConfig,
        template_resource_locator: object,
        /, *,
        init: bool = True,
        repr: bool = True,  # noqa: A002
        eq: bool = True,
        order: bool = False,
        unsafe_hash: bool = False,
        frozen: bool = False,
        match_args: bool = True,
        kw_only: bool = False,
        slots: bool = True,
        weakref_slot: bool = False,
        loader: Annotated[
                AsyncTemplateLoader | SyncTemplateLoader | None,
                Note('''Explicit template loaders can be passed to a template
                    instance to bypass the loader declared in the template
                    environment. This is primarily intended as a mechanism for
                    library developers to define redistributable templates as
                    part of their codebases, while not depending on the
                    template loader of the end user's codebase.''')
            ] = None,
        segment_modifiers: Annotated[
                Sequence[SegmentModifier] | None,
                Note('''An ordered sequence of ``SegmentModifier`` instances
                    to apply to every literal string segment of the loaded
                    template text.

                    The modifiers will be applied in the order that they are
                    declared. The first modifier to match the segment will
                    short-circuit the remaining modifiers, regardless of
                    whether or not it applies any changes.''')
            ] = None
        ) -> Callable[[T], T]:
    """This both transforms the decorated class into a stdlib dataclass
    and declares it as a templatey template.

    **Note that unlike the stdlib dataclass decorator, this defaults to
    ``slots=True``.** If you find yourself having problems with
    metaclasses and/or subclassing, you can disable this by passing
    ``slots=False``. Generally speaking, though, this provides a
    free performance benefit. **If weakref support is required, be sure
    to pass ``weakref_slot=True``.
    """
    if segment_modifiers is None:
        segment_modifiers = []

    return functools.partial(
        make_template_definition,
        dataclass_kwargs={
            'init': init,
            'repr': repr,
            'eq': eq,
            'order': order,
            'unsafe_hash': unsafe_hash,
            'frozen': frozen,
            'match_args': match_args,
            'kw_only': kw_only,
            'slots': slots,
            'weakref_slot': weakref_slot
        },
        template_resource_locator=template_resource_locator,
        template_config=config,
        segment_modifiers=segment_modifiers,
        explicit_loader=loader)


@dataclass(frozen=True)
class TemplateConfig[T: type, L: object]:
    """Template configs specify how the template and its interpolated
    content should be processed.
    """
    interpolator: Annotated[
        NamedInterpolator,
        Note('''The interpolator determines what characters are used for
            performing interpolations within the template. They can be
            escaped by repeating them, for example ``{{}}`` would be
            a literal ``{}`` with a curly braces interpolator.''')]
    variable_escaper: Annotated[
        VariableEscaper,
        Note('''Variables are always escaped. The variable escaper is
            the callable responsible for performing that escaping. If you
            don't need escaping, there are noop escapers within the prebaked
            template configs that you can use for convenience.''')]
    content_verifier: Annotated[
        ContentVerifier,
        Note('''Content isn't escaped, but it ^^is^^ verified. Content
            verification is a simple process that either succeeds or fails;
            it allows, for example, to allowlist certain HTML tags.''')]


def _extract_template_class_locals() -> dict[str, Any] | None:
    """When templates are created from inside a closure (ex, during
    testing, where this is extremely common), we need access to the
    locals from the closure to resolve type hints. This method relies
    upon ``inspect`` to extract them.

    Note that this can be very sensitive to where, exactly, you put it
    within the templatey code. Always put it as close as possible to
    the public API method, so that the first frame from another module
    coincides with the call to decorate a template class.
    """
    upmodule_frame = _get_first_frame_from_other_module()
    if upmodule_frame is not None:
        return upmodule_frame.f_locals


def _get_first_frame_from_other_module() -> FrameType | None:
    """Both of our closure workarounds require walking up the stack
    until we reach the first frame coming from ^^outside^^ the ~~house~~
    current module. This performs that lookup.

    **Note that this is pretty fragile.** Or, put a different way: it
    does exactly what the function name suggest it does: it finds the
    FIRST frame from another module. That doesn't mean we won't return
    to this module; it doesn't mean it's from the actual client library,
    etc. It just means it's the first frame that isn't from this
    module.
    """
    upstack_frame = inspect.currentframe()
    if upstack_frame is None:
        return None
    else:
        this_module = upstack_module = inspect.getmodule(
            _extract_template_class_locals)
        while upstack_module is this_module:
            if upstack_frame is None:
                return None

            upstack_frame = upstack_frame.f_back
            upstack_module = inspect.getmodule(upstack_frame)

    return upstack_frame


# Yes, this is awkward with a bazillion return statements, but in this case,
# clarity is better than elegance
def _classify_interface_field_flavor(  # noqa: PLR0911
        parent_class_type_hints: dict[str, Any],
        template_field: Field
        ) -> tuple[set[InterfaceAnnotationFlavor], type | None]:
    """For a dataclass field, determines whether it was declared as a
    var, slot, or content.

    If none of the above, returns None.
    """
    # Note that dataclasses don't include the actual type (just a string)
    # when in __future__ mode, so we need to get them from the parent class
    # by calling get_type_hints() on it
    resolved_field_type = parent_class_type_hints[template_field.name]
    anno_origin = typing.get_origin(resolved_field_type)
    if anno_origin is Var:
        nested_type, = typing.get_args(resolved_field_type)
        return {InterfaceAnnotationFlavor.VARIABLE}, nested_type
    elif anno_origin is Slot:
        nested_type, = typing.get_args(resolved_field_type)
        return {InterfaceAnnotationFlavor.SLOT}, nested_type
    elif anno_origin is Content:
        nested_type, = typing.get_args(resolved_field_type)
        return {InterfaceAnnotationFlavor.CONTENT}, nested_type
    elif anno_origin is DynamicClassSlot:
        return {
            InterfaceAnnotationFlavor.SLOT,
            InterfaceAnnotationFlavor.DYNAMIC
        }, None

    # This is all if there's a generic annotation with no parameter passed,
    # ex ``foo: Var`` or ``bar: Slot`` or (presumably) ``baz: list``
    elif anno_origin is None:
        if resolved_field_type is Var:
            return {InterfaceAnnotationFlavor.VARIABLE}, None

        elif resolved_field_type is Content:
            return {InterfaceAnnotationFlavor.CONTENT}, None

        elif resolved_field_type is DynamicClassSlot:
            return {
                InterfaceAnnotationFlavor.SLOT,
                InterfaceAnnotationFlavor.DYNAMIC
            }, None

        elif resolved_field_type is Slot:
            raise TypeError(
                '``Slot`` annotations require a concrete slot class as a '
                + 'parameter!')

        else:
            return {InterfaceAnnotationFlavor.DATA}, None

    # There was a non-generic parameter passed. Therefore, it can only be
    # one thing: template data.
    else:
        return {InterfaceAnnotationFlavor.DATA}, None


@dataclass_transform(field_specifiers=(param, field, Field))
def make_template_definition[T: type](
        cls: T,
        *,
        dataclass_kwargs: dict[str, bool],
        # Note: needs to be understandable by template loader
        template_resource_locator: object,
        template_config: TemplateConfig,
        segment_modifiers: Sequence[SegmentModifier],
        explicit_loader: AsyncTemplateLoader | SyncTemplateLoader | None
        ) -> T:
    """Programmatically creates a template definition. Converts the
    requested class into a dataclass, passing along ``dataclass_kwargs``
    to the dataclass constructor. Then performs some templatey-specific
    bookkeeping. Returns the resulting dataclass.
    """
    cls = dataclass(**dataclass_kwargs)(cls)
    cls._templatey_config = template_config
    cls._templatey_resource_locator = template_resource_locator
    cls._templatey_explicit_loader = explicit_loader

    template_module = cls.__module__
    template_scope_id = extract_frame_scope_id()
    template_forward_ref = ForwardRefLookupKey(
        module=template_module,
        name=cls.__name__,
        scope_id=template_scope_id)

    # We're prioritizing the typical case here, where the templates are defined
    # at the module toplevel, and therefore accessible within the module
    # globals. However, if the template is defined within a closure, we might
    # need to walk up the stack until we find a caller that isn't within this
    # file, and then grab its locals.
    try:
        template_type_hints = typing.get_type_hints(cls)
    except NameError as exc:
        logger.info(dedent('''\
            Failed to resolve template type hints on first pass. This could be
            indicative of a bug, or it might occur in normal situations if:
            ++  you're defining the template within a closure. Here, we'll
                attempt to infer the locals via inspect.currentframe, but not
                all platforms support that, which can lead to failures
            ++  the type hint is a forward reference.

            In both cases, we'll wrap the request into a
            ``ForwardRefLookupKey``, which will then hopefully be
            resolved as soon as the forward reference is declared.
            If it's never resolved, however, we will raise whenever
            ``render`` is called.
            '''),
            exc_info=exc)

        # If you're confused, keep reading the comments below.
        forwardref_lookup = ForwardRefGeneratingNamespaceLookup(
            template_module=template_module,
            template_scope_id=template_scope_id)
        # This is the same as the current implementation of get_type_hints
        # in cpython for classes:
        # https://github.com/python/cpython/blob/0045100ccbc3919e8990fa59bc413fe38d21b075/Lib/typing.py#L2325
        template_globals = getattr(
            sys.modules.get(template_module, None), '__dict__', {})

        # Okay, so... this is non-intuitive, to be sure. And if you fail to
        # do this, you'll have really perfidious bugs, because anything that
        # was a valid reference within the temporary namespace created inside
        # the class creation -- **including the class itself** -- will be
        # converted to a forward reference proxy. This would of course cause
        # problems with inter-class references, but it also means that the
        # class itself gets treated as a forward ref instead a concrete slot,
        # and therefore added into the pending forward refs registration. This
        # then gets immediately fixed, except, because the registration is a
        # set, and the iteration order of sets is non-deterministic, the
        # exact, arbitrary order of pending ref resolution can cause a
        # correctly-resolved forward ref for the current class being processed,
        # to then be overwritten by a pending reference, which is then never
        # resolved. Believe me, it's a mess.
        # So to solve this, we need to do two things. First, add the class'
        # __dict__ into the namespace lookups, because that solves any
        # inter-class references. But second, we need to also add the class
        # itself, under its __name__, because this name, though valid and
        # accessible in the temporary class creation namespace, is nonetheless
        # removed from the __dict__ during final class creation.
        # But, ONE FINAL THING: chainmaps need **mutable** mappings. So we
        # have to create a copy of the cls.__dict__ anyways.
        resurrected_clsdef_namespace = {**cls.__dict__, cls.__name__: cls}

        # Note: the whole point of this is to support forward refs, and there's
        # a method to the madness here. We need a way of getting an actual
        # forward ref object. Prior to 3.14 (via PEP 649), we don't have a way
        # to specify to ``get_type_hints`` that we want to have a forward ref
        # object, and it just raises a nameerror that we can't recover from.
        # Our workaround is to inject an object that will lazily create proxy
        # objects for all forward references, but we have to supply this to
        # get_type_hints somehow, which is non-trivial:
        # globalns needs to be strictly a dict, because it gets delegated into
        # ``eval``, which requires one. Which means we can only use the localns
        # to intercept missing forward references. But that, then, means that
        # we need to recover the existing check for the actual globals, since
        # otherwise **all** global names would be overwritten by the forward
        # reference.
        maybe_locals = _extract_template_class_locals()
        if maybe_locals is None:
            prioritized_lookups = (
                # See note above about this
                resurrected_clsdef_namespace,
                template_globals,
                # Fun fact: these aren't included in the other globals!
                __builtins__,
                forwardref_lookup)

        else:
            prioritized_lookups = (
                # See note above about this
                resurrected_clsdef_namespace,
                maybe_locals,
                template_globals,
                # Fun fact: these aren't included in the other globals!
                __builtins__,
                forwardref_lookup)

        # Because of our forward lookup, this will always succeed
        template_type_hints = typing.get_type_hints(
            cls, localns=ChainMap(*prioritized_lookups))

    slots = {}
    dynamic_slots = {}
    vars_ = {}
    content = {}
    data = {}
    prerenderers = {}
    # Note that this ignores initvars, which is what we want
    for template_field in fields(cls):
        field_classification = _classify_interface_field_flavor(
            template_type_hints, template_field)

        # Note: it's not entirely clear to me that this restriction makes
        # sense; I could potentially see MAYBE there being some kind of
        # environment function that could access other attributes from the
        # dataclass? But also, maybe those should be vars? Again, unclear.
        if field_classification is None:
            raise TypeError(
                'Template parameter definitions may only contain variables, '
                + 'slots, and content!')

        else:
            field_flavors, wrapped_type = field_classification

            # A little awkward to effectively just repeat the comparison we did
            # when classifying, but that makes testing easier and control flow
            # clearer
            if InterfaceAnnotationFlavor.VARIABLE in field_flavors:
                dest_lookup = vars_
            elif InterfaceAnnotationFlavor.SLOT in field_flavors:
                if InterfaceAnnotationFlavor.DYNAMIC in field_flavors:
                    dest_lookup = dynamic_slots
                else:
                    dest_lookup = slots
            elif InterfaceAnnotationFlavor.CONTENT in field_flavors:
                dest_lookup = content
            else:
                dest_lookup = data

            dest_lookup[template_field.name] = wrapped_type
            # The .get() might seem redundant here, but not everything is going
            # to be assigned via ``template_field``, so everything else will
            # be missing it.
            prerenderers[template_field.name] = template_field.metadata.get(
                'templatey.field_config', FieldConfig()).prerenderer

    cls._templatey_signature = TemplateSignature.new(
        template_cls=cls,
        data=data,
        slots=slots,
        dynamic_class_slot_names=set(dynamic_slots),
        vars_=vars_,
        content=content,
        forward_ref_lookup_key=template_forward_ref)
    converter_cls = namedtuple('TemplateyConverters', tuple(prerenderers))
    cls._templatey_prerenderers = converter_cls(**prerenderers)
    cls._templatey_segment_modifiers = tuple(segment_modifiers)

    # Note: this needs to be the absolute last thing, because we need to fully
    # satisfy the intersectable interface before we can call it.
    resolve_forward_references(cls)
    return cls


@dataclass(frozen=True, slots=True)
class InjectedValue:
    """This is used by environment functions and complex content to
    indicate that a value is being injected into the template. Use it
    instead of a bare string to preserve an existing interpolation
    config, or to indicate whether verification and/or escaping should
    be applied to the value after conversion to a string.

    Note that, if both are defined, the variable escaper will be called
    first, before the content verifier.
    """
    value: object

    config: InterpolationConfig = field(default_factory=InterpolationConfig)
    use_content_verifier: bool = False
    use_variable_escaper: bool = True

    def __post_init__(self):
        if self.config.prefix is not None or self.config.suffix is not None:
            raise ValueError(
                'Injected values cannot have prefixes nor suffixes. If you '
                + 'need similar behavior, simply add the affix(es) to the '
                + 'iterable returned by the complex content or env function.')


class _ComplexContentBase(Protocol):

    def flatten(
            self,
            dependencies: Annotated[
                Mapping[str, object],
                Note(
                    '''The values of the variables declared as dependencies
                    in the constructor are passed to the call to ``flatten``
                    during rendering.
                    ''')],
            config: Annotated[
                InterpolationConfig,
                Note(
                    '''The interpolation configuration of the content
                    interpolation that the complex content is a member
                    of. Note that neither prefix nor suffix can be passed
                    on to an ``InjectedValue``; they must be manually included
                    in the return value if desired.
                    ''')],
            prerenderers: Annotated[
                Mapping[str, InterpolationPrerenderer | None],
                Note(
                    '''If a prerenderer is defined on a dependency variable,
                    it will be included here; otherwise, the value will be
                    set to ``None``.
                    ''')],
            ) -> Iterable[object | InjectedValue]:
        """Implement this for any instance of complex content.

        First, do whatever content modification you need to, based on
        the dependency variables declared in the constructor. Then,
        if needed, merge in the variable itself using an
        ``InjectedValue``, configuring it as appropriate.

        **Note that the parent interpolation config will be ignored by
        all strings returned by flattening individually.** So if, for
        example, you included a prefix in the content interpolation
        within the template itself, and then passed a ``ComplexContent``
        instance to the template instance, the prefix would be ignored
        completely (unless you do something with it in ``flatten``).

        **Also note that you are responsible for calling the dependency
        variable's ``InterpolationPrerenderer``. directly,** within your
        implementation of ``flatten``. This affords you the option to
        skip it if desired.

        > Example: noun quantity
        __embed__: 'code/python'
            class NaivePluralContent(ComplexContent):

                def flatten(
                        self,
                        dependencies: Mapping[str, object],
                        config: InterpolationConfig,
                        prerenderers:
                            Mapping[str, InterpolationPrerenderer | None],
                        ) -> Iterable[str | InjectedValue]:
                    \"""Pluralizes the name of the provided dependency.
                    For example, ``{'widget': 1}`` will be rendered as
                    "1 widget", but ``{'widget': 2}`` will be rendered as
                    "2 widgets".
                    \"""

                    # Assume only 1 dependency
                    name, value = next(iter(dependencies.items()))

                    if 0 <= value <= 1:
                        return (
                            InjectedValue(
                                value,
                                # This assumes no prefix/suffix
                                config=config,
                                use_content_verifier=False,
                                use_variable_escaper=True),
                            ' ',
                            name)

                    else:
                        return (
                            InjectedValue(
                                value,
                                # This assumes no prefix/suffix
                                config=config,
                                use_content_verifier=False,
                                use_variable_escaper=True),
                            ' ',
                            name,
                            's')
        """
        ...


@dataclass(slots=True, kw_only=True)
class ComplexContent(_ComplexContentBase):
    """Sometimes content isn't as simple as a ``string``. For example,
    content might include variable interpolations. Or you might need
    to modify the content slightly based on the variables -- for
    example, to get subject/verb alignment based on a number, gender
    alignment based on a pronoun, or whatever. ComplexContent gives
    you an escape hatch to do this: simply pass a ComplexContent
    instance as a value instead of a string.
    """

    dependencies: Annotated[
        Collection[str],
        Note(
            '''Complex content dependencies are the **variable** names
            that a piece of complex content depends on. These will be
            passed to the implemented ``flatten`` function during
            rendering.
            ''')]


@dataclass(slots=True, frozen=True)
class SegmentModifier:
    """Segment modifiers are a particularly powerful tool for reducing
    the verbosity of the actual template text. They allow you to modify
    literal string segments that match a particular pattern, replacing
    that pattern with a different segment sequence.

    For example, you could have a modifier that replaces every newline
    in the segment with a call to an ``add_indentation`` environment
    function:

    Note that if you want access to any part of the matched pattern,
    you must include it in a capture group:
    """
    pattern: re.Pattern
    modifier: Callable[
        [SegmentModifierMatch],
        Sequence[
            EnvFuncInvocationRef
            | TemplateInstanceContentRef
            | TemplateInstanceVariableRef
            | str]]

    def apply_and_flatten(
            self,
            literal_template_string: LiteralTemplateString
            ) -> tuple[
                bool,
                list[
                    str
                    | EnvFuncInvocationRef
                    | TemplateInstanceContentRef
                    | TemplateInstanceVariableRef]]:
        """This takes a literal template string segment and applies all
        modifiers. This gets it ready to be converted into the actual
        ParsedTemplateResource parts we need, but doesn't yet perform
        the final conversion.

        Returns a tuple of [had_matches, segments_after_modification]
        """
        after_modification: list[
            str
            | EnvFuncInvocationRef
            | TemplateInstanceContentRef
            | TemplateInstanceVariableRef] = []
        had_matches = False
        splits = self.pattern.split(literal_template_string)
        for split_segment_or_modification in SegmentModifierMatch.from_splits(
            self.pattern,
            splits
        ):
            if isinstance(split_segment_or_modification, str):
                # Here's where we filter out any empty strings. This also helps
                # us re-normalize the output from re.split, so that we recover
                # from the land of "let's use an empty string as a placeholder
                # for anything we did implicitly"
                if split_segment_or_modification:
                    after_modification.append(split_segment_or_modification)
            else:
                had_matches = True
                after_modification.extend(
                    self.modifier(split_segment_or_modification))

        return had_matches, after_modification


@dataclass(slots=True, kw_only=True)
class SegmentModifierMatch:
    """
    """
    captures: Annotated[
        list[str],
        Note(
            '''The captures in a segment modifier match correspond to
            the capture groups in the ``SegmentModifier`` pattern that
            resulted in the match. If the pattern had zero match groups,
            it will be an empty list. If it had one match group, it will
            be a single-item list. Etc.

            The ordering will be the same as the ordering of the groups
            in the original pattern. Named groups are not supported.
            ''')]

    @classmethod
    def from_splits(
            cls,
            src_pattern: re.Pattern,
            splits: list[str]
            ) -> Iterable[SegmentModifierMatch | str]:
        # Note: the +1 is because we need to account for the literal strings
        # in the pattern; otherwise the mod math doesn't work out! This also
        # has the added benefit of meaning we don't need to change behavior
        # between both cases.
        split_type_count = src_pattern.groups + 1

        current_captures = []
        for index, post_split_segment in enumerate(splits):
            # This is always literal text, even if it's an empty string.
            if not index % split_type_count:
                # Note that the zeroth and last index are always literal text,
                # and are never preceeded or followed by a capture. However,
                # we still need to yield the preceeding match when we reach
                # the end.
                if 0 < index:
                    yield cls(captures=current_captures)
                    current_captures = []

                # Note: we're saving the "cull empty strings" bit for later;
                # it makes the logic much cleaner to do one at a time
                yield post_split_segment

            else:
                current_captures.append(post_split_segment)


@dataclass(slots=True, init=False)
class EnvFuncInvocationRef:
    """Used to indicate that a segment modification needs to invoke an
    environment function. Instantiate these like partials:

    > Invocation example
        def my_env_func(foo: str, *, bar: int) -> list[str]:
            ...

        EnvFuncInvocationRef('my_env_func', 'foo', bar=3)
        EnvFuncInvocationRef(
            'my_env_func',
            # TemplateInstanceContentRef, TemplateInstanceDataRef, and
            # TemplateInstanceVariableRef are all supported, including nested
            # within containers
            TemplateInstanceVariableRef('foo'),
            bar=TemplateInstanceDataRef('bar'))

    Note that unfortunately, until/unless higher-kinded type support is
    added to python, these won't be able to type-check correctly.
    """
    name: str
    call_args: tuple[
        object
        | TemplateInstanceContentRef
        | TemplateInstanceDataRef
        | TemplateInstanceVariableRef, ...]
    call_kwargs: dict[
        str,
        object
        | TemplateInstanceContentRef
        | TemplateInstanceDataRef
        | TemplateInstanceVariableRef]

    def __init__(
            self,
            name: str,
            /,
            *call_args:
                object
                | TemplateInstanceContentRef
                | TemplateInstanceDataRef
                | TemplateInstanceVariableRef,
            **call_kwargs:
                object
                | TemplateInstanceContentRef
                | TemplateInstanceDataRef
                | TemplateInstanceVariableRef):
        self.name = name
        self.call_args = call_args
        self.call_kwargs = call_kwargs
