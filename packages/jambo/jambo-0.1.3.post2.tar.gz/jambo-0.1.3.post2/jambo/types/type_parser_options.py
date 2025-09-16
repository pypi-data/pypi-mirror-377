from jambo.types.json_schema_type import JSONSchema

from typing_extensions import ForwardRef, TypedDict


class TypeParserOptions(TypedDict):
    required: bool
    context: JSONSchema
    ref_cache: dict[str, ForwardRef | type | None]
