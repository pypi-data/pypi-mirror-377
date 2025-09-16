from jambo.exceptions import InvalidSchemaException
from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Iterable, TypeVar, Unpack

import copy


V = TypeVar("V")


class ArrayTypeParser(GenericTypeParser):
    mapped_type = list

    json_schema_type = "type:array"

    default_mappings = {"description": "description"}

    type_mappings = {
        "maxItems": "max_length",
        "minItems": "min_length",
    }

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        item_properties = kwargs.copy()
        item_properties["required"] = True

        if (items := properties.get("items")) is None:
            raise InvalidSchemaException(
                f"Array type {name} must have 'items' property defined.",
                invalid_field="items",
            )

        _item_type, _item_args = GenericTypeParser.type_from_properties(
            name, items, **item_properties
        )

        wrapper_type = set if properties.get("uniqueItems", False) else list
        field_type = wrapper_type[_item_type]

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        if "default" in properties or not kwargs.get("required", False):
            mapped_properties["default_factory"] = self._build_default_factory(
                properties.get("default"), wrapper_type
            )

        return field_type, mapped_properties

    def _build_default_factory(self, default_list, wrapper_type):
        if default_list is None:
            return lambda: None

        if not isinstance(default_list, Iterable):
            raise InvalidSchemaException(
                f"Default value for array must be an iterable, got {type(default_list)}",
                invalid_field="default",
            )

        return lambda: copy.deepcopy(wrapper_type(default_list))
