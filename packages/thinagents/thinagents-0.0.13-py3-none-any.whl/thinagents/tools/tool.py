import contextlib
import functools
import hashlib
import re
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Union,
    get_args,
    get_origin,
    Annotated,
    Protocol,
    Literal,
    Final,
    ClassVar,
    TypeVar,
    List,
    Tuple,
    Set,
    FrozenSet,
    ParamSpec,
    runtime_checkable,
)
import logging

try:
    from typing import get_type_hints
except ImportError:
    from typing_extensions import get_type_hints  # type: ignore

import inspect
from collections.abc import Sequence, Mapping
import enum
from dataclasses import is_dataclass, fields

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class FunctionNameSanitizationError(Exception):
    """Raised when function name sanitization fails."""
    pass


def sanitize_function_name(name: str) -> str:
    """
    Sanitize function name to meet LLM provider requirements.
    
    This function ensures compatibility across different LLM providers by applying
    common function naming conventions:
    - Must start with a letter or underscore
    - Must be alphanumeric (a-z, A-Z, 0-9) or underscores (_) only
    - Maximum length of 64 characters (strictest common requirement)
    - No special characters or spaces
    
    Args:
        name: Original function name
        
    Returns:
        Sanitized function name that works across all LLM providers
        
    Raises:
        FunctionNameSanitizationError: If the name cannot be sanitized to a valid function name
    """
    if not name or not isinstance(name, str):
        raise FunctionNameSanitizationError(
            f"Function name must be a non-empty string, got: {type(name).__name__} = {repr(name)}"
        )
    
    original_name = name
    
    # Replace invalid characters with underscores (be more conservative)
    # Only allow alphanumeric and underscores for maximum compatibility
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Ensure it starts with a letter or underscore
    if not re.match(r'^[a-zA-Z_]', sanitized):
        sanitized = f"tool_{sanitized}"
    
    # Truncate to 64 characters (common limit across providers)
    if len(sanitized) > 64:
        sanitized = sanitized[:64]
    
    # Remove trailing underscores and ensure it's not empty
    sanitized = sanitized.rstrip('_')
    
    # Fallback if empty after sanitization
    if not sanitized:
        sanitized = "tool_function"
    
    # Ensure it doesn't conflict with reserved keywords
    if sanitized.lower() in ('function', 'tool', 'call', 'run', 'execute'):
        sanitized = f"{sanitized}_fn"
        # Re-check length after adding suffix
        if len(sanitized) > 64:
            sanitized = sanitized[:64].rstrip('_')
    
    # Final validation - ensure the result is valid
    if not sanitized:
        raise FunctionNameSanitizationError(
            f"Failed to sanitize function name '{original_name}' - resulted in empty string"
        )
    
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', sanitized):
        raise FunctionNameSanitizationError(
            f"Failed to sanitize function name '{original_name}' - result '{sanitized}' is not a valid function name"
        )
    
    if len(sanitized) > 64:
        raise FunctionNameSanitizationError(
            f"Failed to sanitize function name '{original_name}' - result '{sanitized}' exceeds 64 character limit"
        )
    
    return sanitized

JSONSchemaType = Dict[str, Any]

_PYDANTIC_V1 = False
_PYDANTIC_V2 = False
_BaseModel = object
IS_PYDANTIC_AVAILABLE = False

with contextlib.suppress(ImportError):
    from pydantic import BaseModel as PydanticBaseModel
    from pydantic import __version__ as pydantic_version

    _BaseModel = PydanticBaseModel  # type: ignore
    if pydantic_version.startswith("1."):
        _PYDANTIC_V1 = True
    elif pydantic_version.startswith("2."):
        _PYDANTIC_V2 = True

    if _PYDANTIC_V1 or _PYDANTIC_V2:
        IS_PYDANTIC_AVAILABLE = True

# Schema caching for better performance
_SCHEMA_CACHE: Dict[str, JSONSchemaType] = {}
_SCHEMA_CACHE_ENABLED = True


def enable_schema_cache(enabled: bool = True) -> None:
    """Enable or disable schema caching globally."""
    global _SCHEMA_CACHE_ENABLED
    _SCHEMA_CACHE_ENABLED = enabled
    if not enabled:
        clear_schema_cache()


def clear_schema_cache() -> None:
    """Clear the schema cache."""
    global _SCHEMA_CACHE
    _SCHEMA_CACHE.clear()
    logger.debug("Schema cache cleared")


def _get_cache_key(py_type: Any, schema_source: str = "") -> str:
    """Generate a cache key for a Python type and schema source."""
    type_str = str(py_type)
    if hasattr(py_type, "__module__"):
        type_str = f"{py_type.__module__}.{type_str}"
    
    cache_key = f"{type_str}_{schema_source}"
    return hashlib.md5(cache_key.encode()).hexdigest()


@runtime_checkable
class ThinAgentsTool(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    async def __acall__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def tool_schema(self) -> Dict[str, Any]: ...

    __name__: str


_PRIMITIVE_TYPE_MAP = {
    type(None): {"type": "null"},
    str: {"type": "string"},
    int: {"type": "integer"},
    float: {"type": "number"},
    bool: {"type": "boolean"},
}


def _handle_enum(py_type: Any) -> JSONSchemaType:
    """
    Convert a Python Enum type to a JSON schema representation.
    Handles string, integer, and number enums.
    """
    # Check cache first
    cache_key = _get_cache_key(py_type, "enum")
    if _SCHEMA_CACHE_ENABLED and cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]
    
    values = [e.value for e in py_type]
    if all(isinstance(v, str) for v in values):
        schema = {"type": "string", "enum": values}
    elif all(isinstance(v, int) for v in values):
        schema = {"type": "integer", "enum": values}
    elif all(isinstance(v, (int, float)) for v in values):
        schema = {"type": "number", "enum": values}
    else:
        schema = {"enum": values}
    
    if _SCHEMA_CACHE_ENABLED:
        _SCHEMA_CACHE[cache_key] = schema
    
    return schema

def _handle_sequence(py_type: Any, args: tuple) -> JSONSchemaType:
    """
    Convert a sequence type (e.g., List, Sequence) to a JSON schema array type.
    """
    item_type = args[0] if args else Any
    return {"type": "array", "items": map_type_to_schema(item_type)}

def _handle_tuple(args: tuple) -> JSONSchemaType:
    """
    Convert a tuple type to a JSON schema representation.
    Handles both fixed-length and variable-length tuples.
    """
    if not args:
        return {"type": "array"}
    if len(args) == 2 and args[1] is Ellipsis:
        return {"type": "array", "items": map_type_to_schema(args[0])}
    return {
        "type": "array",
        "prefixItems": [map_type_to_schema(arg) for arg in args],
        "minItems": len(args),
        "maxItems": len(args),
    }

def _handle_dataclass(py_type: Any) -> JSONSchemaType:
    """
    Convert a dataclass type to a JSON schema object, including required fields and property types.
    """
    props = {}
    required = []
    dc_fields = fields(py_type)
    type_hints_for_dc = get_type_hints(py_type, include_extras=True)

    for field in dc_fields:
        field_type = type_hints_for_dc.get(field.name, field.type)
        props[field.name] = map_type_to_schema(field_type)
        if _is_required_field(field, field_type):
            required.append(field.name)

    return {
        "type": "object",
        "properties": props,
        "required": sorted(list(set(required))),
        "additionalProperties": False,
    }

def _is_required_field(field: Any, field_type: Any) -> bool:
    """
    Determine if a dataclass field is required based on its default value and type annotation.
    """
    if field.default is not inspect.Parameter.empty:
        return False
    origin = get_origin(field_type)
    args = get_args(field_type)
    return (origin is not Union or type(None) not in args) and (
        origin is Union or origin is not Optional
    )

def _handle_union(args: tuple) -> JSONSchemaType:
    """
    Convert a Union type (including Optional) to a JSON schema using anyOf.
    """
    non_none_args = [a for a in args if a is not type(None)]
    if not non_none_args:
        return {"type": "null"}
    
    schemas = [map_type_to_schema(a) for a in non_none_args]
    if type(None) in args:
        schemas.append({"type": "null"})
    return {"anyOf": schemas}

@runtime_checkable
class TypeHandler(Protocol):
    """
    Protocol for custom type handlers that convert Python types to JSON schema.
    """
    def can_handle(self, py_type: Any) -> bool: ...
    def handle(self, py_type: Any, schema_mapper: Callable[[Any], JSONSchemaType]) -> JSONSchemaType: ...

class BaseTypeHandler:
    def can_handle(self, py_type: Any) -> bool:
        return False

    def handle(self, py_type: Any, schema_mapper: Callable[[Any], JSONSchemaType]) -> JSONSchemaType:
        return {"type": "object"}

class PrimitiveHandler(BaseTypeHandler):
    """
    Handles primitive Python types (str, int, float, bool, None) for JSON schema conversion.
    """
    def can_handle(self, py_type: Any) -> bool:
        return py_type in _PRIMITIVE_TYPE_MAP

    def handle(self, py_type: Any, _: Callable[[Any], JSONSchemaType]) -> JSONSchemaType:
        return _PRIMITIVE_TYPE_MAP[py_type]

class EnumHandler(BaseTypeHandler):
    """
    Handles Python Enum types for JSON schema conversion.
    """
    def can_handle(self, py_type: Any) -> bool:
        return isinstance(py_type, type) and issubclass(py_type, enum.Enum)

    def handle(self, py_type: Any, _: Callable[[Any], JSONSchemaType]) -> JSONSchemaType:
        return _handle_enum(py_type)

class PydanticHandler(BaseTypeHandler):
    """
    Handles Pydantic BaseModel types for JSON schema conversion, supporting both v1 and v2.
    """
    def can_handle(self, py_type: Any) -> bool:
        return (IS_PYDANTIC_AVAILABLE and isinstance(py_type, type) 
                and issubclass(py_type, _BaseModel))

    def handle(self, py_type: Any, _: Callable[[Any], JSONSchemaType]) -> JSONSchemaType:
        schema: Optional[JSONSchemaType] = None
        try:
            if _PYDANTIC_V2 and hasattr(py_type, "model_json_schema"):
                schema = py_type.model_json_schema()  # type: ignore
            elif _PYDANTIC_V1 and hasattr(py_type, "schema"):
                schema = py_type.schema()  # type: ignore
        except Exception as e:
            logger.error(f"Error generating Pydantic schema for {py_type}: {e}", exc_info=True)
            return {"type": "object", "description": f"Error generating Pydantic schema: {e}"}
        return schema if schema is not None else {"type": "object"}

class SequenceHandler(BaseTypeHandler):
    """
    Handles sequence types (lists, sequences) for JSON schema conversion.
    """
    def can_handle(self, py_type: Any) -> bool:
        origin = get_origin(py_type)
        return (origin in (list, List) or 
                (isinstance(py_type, type) and issubclass(py_type, Sequence) 
                 and not issubclass(py_type, (str, bytes, bytearray))))

    def handle(self, py_type: Any, schema_mapper: Callable[[Any], JSONSchemaType]) -> JSONSchemaType:
        return _handle_sequence(py_type, get_args(py_type))

_type_handlers = [
    PrimitiveHandler(),
    EnumHandler(),
    PydanticHandler(),
    SequenceHandler(),
]

def map_type_to_schema(py_type: Any) -> JSONSchemaType:
    """
    Main entry point for mapping a Python type annotation to a JSON schema type.
    Delegates to registered type handlers and handles common generic types.
    Uses caching for improved performance.
    """
    # Check cache first
    cache_key = _get_cache_key(py_type, "main")
    if _SCHEMA_CACHE_ENABLED and cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]
    
    origin = get_origin(py_type)
    args = get_args(py_type)

    schema = None
    
    for handler in _type_handlers:
        if handler.can_handle(py_type):
            schema = handler.handle(py_type, map_type_to_schema)
            break

    if schema is None:
        if origin is Literal:
            schema = _handle_enum(lambda: args)
        elif origin in (tuple, Tuple):
            schema = _handle_tuple(args)
        elif origin in (set, Set, frozenset, FrozenSet):
            schema = {**_handle_sequence(py_type, args), "uniqueItems": True}
        elif is_dataclass(py_type):
            schema = _handle_dataclass(py_type)
        elif origin in (dict, Dict) or (isinstance(py_type, type) and issubclass(py_type, Mapping)):
            if not args or len(args) != 2:
                schema = {"type": "object", "additionalProperties": map_type_to_schema(Any)}
            else:
                key_type, value_type = args
                schema = {"type": "object", "additionalProperties": map_type_to_schema(value_type)}
                if key_type is not str:
                    schema["x-key-type"] = str(key_type)
        elif origin is Union:
            schema = _handle_union(args)
        elif origin is Optional:
            schema = _handle_union((args[0], type(None))) if args else {"type": "null"}
        elif origin in (Final, ClassVar):
            schema = map_type_to_schema(args[0]) if args else {}
        elif py_type is Any:
            logger.debug("Mapping 'Any' type to empty schema.")
            schema = {}
        elif isinstance(py_type, TypeVar):
            if constraints := getattr(py_type, "__constraints__", None):
                logger.debug(f"Mapping TypeVar {py_type} with constraints {constraints} to anyOf schema.")
                schema = {"anyOf": [map_type_to_schema(c) for c in constraints]}
            else:
                bound = getattr(py_type, "__bound__", None)
                if bound and bound is not object and bound is not py_type:
                    logger.debug(f"Mapping TypeVar {py_type} with bound {bound} to schema of bound type.")
                    schema = map_type_to_schema(bound)
                else:
                    logger.debug(f"Mapping TypeVar {py_type} (unconstrained or self-bound) to empty schema.")
                    schema = {}
        else:
            logger.warning(f"No specific schema handler for type {py_type}. Defaulting to 'object'.")
            schema = {"type": "object"}
    
    # Cache the result
    if _SCHEMA_CACHE_ENABLED and schema is not None:
        _SCHEMA_CACHE[cache_key] = schema
    
    return schema or {"type": "object"}


@functools.lru_cache(maxsize=256)
def generate_param_schema(param_name: str, param: inspect.Parameter, annotation: Any) -> JSONSchemaType:
    """
    Generate JSON schema for a function parameter with caching.
    
    Args:
        param_name: Name of the parameter
        param: Parameter object from inspect
        annotation: Type annotation of the parameter
        
    Returns:
        JSON schema for the parameter
    """
    schema = map_type_to_schema(annotation)
    
    # Add default value if present
    if param.default is not inspect.Parameter.empty and param.default is not None:
        schema["default"] = param.default
    
    # Add parameter description if available from docstring
    if hasattr(param, "__doc__") and param.__doc__:
        schema["description"] = param.__doc__
    
    return schema


def is_required_parameter(param: inspect.Parameter, annotation: Any) -> bool:
    """
    Determine if a function parameter is required based on its default value and type annotation.
    """
    if param.default is not inspect.Parameter.empty:
        return False
    current_type_to_check = annotation
    if get_origin(current_type_to_check) is Annotated:
        args = get_args(current_type_to_check)
        if args:
            current_type_to_check = args[0]

    origin = get_origin(current_type_to_check)
    args = get_args(current_type_to_check)

    return (origin is not Union or type(None) not in args) and (
        origin is Union or origin is not Optional
    )


def tool(
    fn_for_tool: Optional[Callable[P, R]] = None,
    *,
    return_type: Literal["content", "content_and_artifact"] = "content",
    pydantic_schema: Optional[Any] = None,
    name: Optional[str] = None,
) -> ThinAgentsTool[P, R]:  # type: ignore
    """
    Decorator to register a function as a ThinAgentsTool, optionally specifying the return type and/or a pydantic schema.
    Enforces return type compatibility and attaches a tool_schema method for OpenAPI/JSON schema generation.

    Args:
        fn_for_tool: The function to register as a tool.
        return_type: The return type of the tool.
            - "content": The tool returns only content. This is the default.  
            - "content_and_artifact": The tool returns both content and an artifact, where the artifact is something that can be sent downstream.
        pydantic_schema: If provided, should be a Pydantic BaseModel class. The schema will be extracted internally and validated against the function signature.
        name: If provided, use this as the tool's name in the schema and for the wrapper. Otherwise, use the function's name.

    Returns:
        A ThinAgentsTool object that can be used to execute the tool.
    """
    if fn_for_tool is None:
        return lambda fn: tool(fn, return_type=return_type, pydantic_schema=pydantic_schema, name=name)  # type: ignore
    annotated_desc = ""
    actual_func = fn_for_tool
    if get_origin(fn_for_tool) is Annotated:
        unwrapped_func, *meta = get_args(fn_for_tool)
        actual_func = unwrapped_func
        annotated_desc = next((m for m in meta if isinstance(m, str)), "")

    raw_name = name if name is not None else actual_func.__name__
    try:
        tool_name = sanitize_function_name(raw_name)
    except FunctionNameSanitizationError as e:
        raise ValueError(f"Cannot create tool from function '{actual_func.__name__}': {e}") from e
    
    is_async_tool = inspect.iscoroutinefunction(actual_func)

    if return_type == "content_and_artifact":
        sig = inspect.signature(actual_func)
        ret_ann = sig.return_annotation
        # no annotation provided
        if ret_ann is inspect.Signature.empty:
            raise ValueError(
                f"Tool '{tool_name}' declared return_type='content_and_artifact' but no return annotation found"
            )
        origin = get_origin(ret_ann)
        args = get_args(ret_ann)
        if origin not in (tuple, Tuple) or len(args) != 2:
            raise ValueError(
                f"Tool '{tool_name}' declared return_type='content_and_artifact' but return annotation is {ret_ann!r}, expected Tuple[content_type, artifact_type]"
            )

    schema_dict = None
    if pydantic_schema is not None:
        if not IS_PYDANTIC_AVAILABLE:
            raise ImportError("Pydantic is not available. Please install pydantic to use pydantic_schema.")
        if not (isinstance(pydantic_schema, type) and issubclass(pydantic_schema, _BaseModel)):
            raise ValueError("pydantic_schema must be a Pydantic BaseModel class")
        if hasattr(pydantic_schema, "model_json_schema"):
            schema_dict = pydantic_schema.model_json_schema()  # type: ignore
        elif hasattr(pydantic_schema, "schema"):
            schema_dict = pydantic_schema.schema()  # type: ignore
        else:
            raise ValueError("Provided pydantic_schema does not have a model_json_schema or schema method.")
        if "title" in schema_dict:
            schema_dict = dict(schema_dict)
            schema_dict.pop("title")
        sig = inspect.signature(actual_func)
        func_param_names = list(sig.parameters.keys())
        func_required = [
            name for name, param in sig.parameters.items()
            if is_required_parameter(param, param.annotation if param.annotation is not inspect.Parameter.empty else Any)
        ]
        schema_properties = list(schema_dict.get("properties", {}).keys())
        schema_required = list(schema_dict.get("required", []))
        # Check that all function parameters are in schema properties and vice versa
        if set(func_param_names) != set(schema_properties):
            raise ValueError(
                f"pydantic_schema properties {schema_properties} do not match function parameters {func_param_names} for tool '{tool_name}'"
            )
        # Check that required match
        if set(func_required) != set(schema_required):
            raise ValueError(
                f"pydantic_schema required {schema_required} do not match function required parameters {func_required} for tool '{tool_name}'"
            )

    @functools.wraps(actual_func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        # call the actual tool function
        result = actual_func(*args, **kwargs)
        # if the tool declares content_and_artifact, enforce a 2-tuple return
        if return_type == "content_and_artifact" and not (isinstance(result, tuple) and len(result) == 2):
            raise ValueError(
                f"Tool '{tool_name}' declared return_type='content_and_artifact' but returned {result!r}"
            )
        return result

    # store desired return_type on the wrapper
    wrapper.return_type = return_type  # type: ignore
    wrapper.is_async_tool = is_async_tool # type: ignore

    def tool_schema() -> Dict[str, Any]:
        sig = inspect.signature(actual_func)
        func_doc = inspect.getdoc(actual_func)
        description = annotated_desc or func_doc or ""
        if schema_dict is not None:
            params_schema = schema_dict.copy()
            param_desc = params_schema.pop("description", None)
            if param_desc and not description:
                description = param_desc
        else:
            type_hints = get_type_hints(actual_func, include_extras=True)
            generated_params_schema: Dict[str, Any] = {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            }
            for name, param in sig.parameters.items():
                annotation = type_hints.get(name, param.annotation)
                if annotation is inspect.Parameter.empty:
                    annotation = Any
                param_def = generate_param_schema(name, param, annotation)
                generated_params_schema["properties"][name] = param_def  # type: ignore
                if is_required_parameter(param, annotation):
                    generated_params_schema["required"].append(name)
            generated_params_schema["required"] = sorted(list(set(generated_params_schema["required"])))
            params_schema = generated_params_schema
        # wrap schema with return_type metadata
        original_schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": params_schema,
            },
        }
        return {"tool_schema": original_schema, "return_type": return_type}

    setattr(wrapper, "tool_schema", tool_schema)
    wrapper.__name__ = tool_name

    return wrapper  # type: ignore
