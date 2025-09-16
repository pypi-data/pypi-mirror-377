from jambo.exceptions import InvalidSchemaException, UnsupportedSchemaException
from jambo.parser import ObjectTypeParser, RefTypeParser
from jambo.types import JSONSchema

from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for
from pydantic import BaseModel


class SchemaConverter:
    """
    Converts JSON Schema to Pydantic models.

    This class is responsible for converting JSON Schema definitions into Pydantic models.
    It validates the schema and generates the corresponding Pydantic model with appropriate
    fields and types. The generated model can be used for data validation and serialization.
    """

    @staticmethod
    def build(schema: JSONSchema) -> type[BaseModel]:
        """
        Converts a JSON Schema to a Pydantic model.
        :param schema: The JSON Schema to convert.
        :return: A Pydantic model class.
        """

        try:
            validator = validator_for(schema)
            validator.check_schema(schema)  # type: ignore
        except SchemaError as err:
            raise InvalidSchemaException(
                "Validation of JSON Schema failed.", cause=err
            ) from err

        if "title" not in schema:
            raise InvalidSchemaException(
                "Schema must have a title.", invalid_field="title"
            )

        schema_type = SchemaConverter._get_schema_type(schema)

        match schema_type:
            case "object":
                return ObjectTypeParser.to_model(
                    schema["title"],
                    schema.get("properties", {}),
                    schema.get("required", []),
                    context=schema,
                    ref_cache=dict(),
                    required=True,
                )

            case "$ref":
                parsed_model, _ = RefTypeParser().from_properties(
                    schema["title"],
                    schema,
                    context=schema,
                    ref_cache=dict(),
                    required=True,
                )
                return parsed_model
            case _:
                unsupported_type = (
                    f"type:{schema_type}" if schema_type else "missing type"
                )
                raise UnsupportedSchemaException(
                    "Only object and $ref schema types are supported.",
                    unsupported_field=unsupported_type,
                )

    @staticmethod
    def _get_schema_type(schema: JSONSchema) -> str | None:
        """
        Returns the type of the schema.
        :param schema: The JSON Schema to check.
        :return: The type of the schema.
        """
        if "$ref" in schema:
            return "$ref"

        return schema.get("type")
