from jambo import SchemaConverter
from jambo.exceptions import InvalidSchemaException, UnsupportedSchemaException

from pydantic import AnyUrl, BaseModel, ValidationError

from ipaddress import IPv4Address, IPv6Address
from unittest import TestCase
from uuid import UUID


def is_pydantic_model(cls):
    return isinstance(cls, type) and issubclass(cls, BaseModel)


class TestSchemaConverter(TestCase):
    def test_invalid_schema(self):
        schema = {
            "title": 1,
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }

        with self.assertRaises(InvalidSchemaException):
            SchemaConverter.build(schema)

    def test_invalid_schema_type(self):
        schema = {
            "title": 1,
            "description": "A person",
            "type": 1,
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }

        with self.assertRaises(InvalidSchemaException):
            SchemaConverter.build(schema)

    def test_build_expects_title(self):
        schema = {
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }

        with self.assertRaises(InvalidSchemaException):
            SchemaConverter.build(schema)

    def test_build_expects_object(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "string",
        }

        with self.assertRaises(UnsupportedSchemaException):
            SchemaConverter.build(schema)

    def test_is_invalid_field(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "id": {
                    "notType": "string",
                }
            },
            # 'required': ['name', 'age', 'is_active', 'friends', 'address'],
        }

        with self.assertRaises(InvalidSchemaException) as context:
            SchemaConverter.build(schema)
            self.assertTrue("Unknown type" in str(context.exception))

    def test_jsonschema_to_pydantic(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }

        model = SchemaConverter.build(schema)

        self.assertTrue(is_pydantic_model(model))

    def test_validation_string(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 4, "minLength": 1},
                "email": {
                    "type": "string",
                    "maxLength": 50,
                    "minLength": 5,
                    "pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                },
            },
            "required": ["name"],
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(model(name="John", age=30).name, "John")

        with self.assertRaises(ValidationError):
            model(name=123, age=30, email="teste@hideyoshi.com")

        with self.assertRaises(ValidationError):
            model(name="John Invalid", age=45, email="teste@hideyoshi.com")

        with self.assertRaises(ValidationError):
            model(name="", age=45, email="teste@hideyoshi.com")

        with self.assertRaises(ValidationError):
            model(name="John", age=45, email="hideyoshi.com")

    def test_validation_integer(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "age": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 120,
                },
            },
            "required": ["age"],
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(model(age=30).age, 30)

        with self.assertRaises(ValidationError):
            model(age=-1)

        with self.assertRaises(ValidationError):
            model(age=121)

    def test_validation_float(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "age": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 120,
                },
            },
            "required": ["age"],
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(model(age=30).age, 30.0)

        with self.assertRaises(ValidationError):
            model(age=-1.0)

        with self.assertRaises(ValidationError):
            model(age=121.0)

    def test_validation_boolean(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "is_active": {"type": "boolean"},
            },
            "required": ["is_active"],
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(model(is_active=True).is_active, True)

        self.assertEqual(model(is_active="true").is_active, True)

    def test_validation_list_with_valid_items(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "friends": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 2,
                    "uniqueItems": True,
                },
            },
            "required": ["friends"],
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(
            model(friends=["John", "Jane", "John"]).friends, {"John", "Jane"}
        )

        with self.assertRaises(ValidationError):
            model(friends=[])

        with self.assertRaises(ValidationError):
            model(friends=["John", "Jane", "Invalid"])

    def test_validation_list_with_missing_items(self):
        model = SchemaConverter.build(
            {
                "title": "Person",
                "description": "A person",
                "type": "object",
                "properties": {
                    "friends": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 2,
                        "default": ["John", "Jane"],
                    },
                },
            }
        )

        self.assertEqual(model().friends, ["John", "Jane"])

        model = SchemaConverter.build(
            {
                "title": "Person",
                "description": "A person",
                "type": "object",
                "properties": {
                    "friends": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 2,
                    },
                },
                "required": ["friends"],
            }
        )

        with self.assertRaises(ValidationError):
            model()

    def test_validation_object(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                    "required": ["street", "city"],
                },
            },
            "required": ["address"],
        }

        model = SchemaConverter.build(schema)

        obj = model(address={"street": "123 Main St", "city": "Springfield"})

        self.assertEqual(obj.address.street, "123 Main St")
        self.assertEqual(obj.address.city, "Springfield")

        with self.assertRaises(ValidationError):
            model()

    def test_default_for_string(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "default": "John",
                },
            },
            "required": ["name"],
        }

        model = SchemaConverter.build(schema)

        obj = model(name="John")

        self.assertEqual(obj.name, "John")

    def test_invalid_default_for_string(self):
        # Test for default with maxLength
        schema_max_length = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "default": "John",
                    "maxLength": 2,
                },
            },
            "required": ["name"],
        }

        with self.assertRaises(InvalidSchemaException):
            SchemaConverter.build(schema_max_length)

    def test_default_for_list(self):
        schema_list = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "friends": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["John", "Jane"],
                },
            },
            "required": ["friends"],
        }

        model_list = SchemaConverter.build(schema_list)

        self.assertEqual(model_list().friends, ["John", "Jane"])

        # Test for default with uniqueItems
        schema_set = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "friends": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["John", "Jane"],
                    "uniqueItems": True,
                },
            },
            "required": ["friends"],
        }

        model_set = SchemaConverter.build(schema_set)

        self.assertEqual(model_set().friends, {"John", "Jane"})

    def test_default_for_object(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                    "default": {"street": "123 Main St", "city": "Springfield"},
                },
            },
            "required": ["address"],
        }

        model = SchemaConverter.build(schema)

        obj = model(address={"street": "123 Main St", "city": "Springfield"})

        self.assertEqual(obj.address.street, "123 Main St")
        self.assertEqual(obj.address.city, "Springfield")

    def test_all_of(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "name": {
                    "allOf": [
                        {"type": "string", "maxLength": 11},
                        {"type": "string", "maxLength": 4},
                        {"type": "string", "minLength": 1},
                        {"type": "string", "minLength": 2},
                    ]
                },
            },
        }

        Model = SchemaConverter.build(schema)

        obj = Model(
            name="J",
        )

        self.assertEqual(obj.name, "J")

        with self.assertRaises(ValidationError):
            Model(name="John Invalid")

        with self.assertRaises(ValidationError):
            Model(name="")

    def test_any_of(self):
        schema = {
            "title": "Person",
            "description": "A person",
            "type": "object",
            "properties": {
                "id": {
                    "anyOf": [
                        {"type": "string", "maxLength": 11, "minLength": 1},
                        {"type": "integer", "maximum": 10},
                    ]
                },
            },
        }

        Model = SchemaConverter.build(schema)

        obj = Model(id=1)
        self.assertEqual(obj.id, 1)

        obj = Model(id="12345678901")
        self.assertEqual(obj.id, "12345678901")

        with self.assertRaises(ValidationError):
            Model(id="")

        with self.assertRaises(ValidationError):
            Model(id="12345678901234567890")

        with self.assertRaises(ValidationError):
            Model(id=11)

    def test_string_format_email(self):
        schema = {
            "title": "EmailTest",
            "type": "object",
            "properties": {"email": {"type": "string", "format": "email"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(model(email="test@example.com").email, "test@example.com")

        with self.assertRaises(ValidationError):
            model(email="invalid-email")

    def test_string_format_uri(self):
        schema = {
            "title": "UriTest",
            "type": "object",
            "properties": {"website": {"type": "string", "format": "uri"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(
            model(website="https://example.com").website, AnyUrl("https://example.com")
        )

        with self.assertRaises(ValidationError):
            model(website="invalid-uri")

    def test_string_format_ipv4(self):
        schema = {
            "title": "IPv4Test",
            "type": "object",
            "properties": {"ip": {"type": "string", "format": "ipv4"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(model(ip="192.168.1.1").ip, IPv4Address("192.168.1.1"))

        with self.assertRaises(ValidationError):
            model(ip="256.256.256.256")

    def test_string_format_ipv6(self):
        schema = {
            "title": "IPv6Test",
            "type": "object",
            "properties": {"ip": {"type": "string", "format": "ipv6"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(
            model(ip="2001:0db8:85a3:0000:0000:8a2e:0370:7334").ip,
            IPv6Address("2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
        )

        with self.assertRaises(ValidationError):
            model(ip="invalid-ipv6")

    def test_string_format_uuid(self):
        schema = {
            "title": "UUIDTest",
            "type": "object",
            "properties": {"id": {"type": "string", "format": "uuid"}},
        }

        model = SchemaConverter.build(schema)

        self.assertEqual(
            model(id="123e4567-e89b-12d3-a456-426614174000").id,
            UUID("123e4567-e89b-12d3-a456-426614174000"),
        )

        with self.assertRaises(ValidationError):
            model(id="invalid-uuid")

    def test_string_format_hostname(self):
        schema = {
            "title": "HostnameTest",
            "type": "object",
            "properties": {"hostname": {"type": "string", "format": "hostname"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(model(hostname="example.com").hostname, "example.com")

        with self.assertRaises(ValidationError):
            model(hostname="invalid..hostname")

    def test_string_format_datetime(self):
        schema = {
            "title": "DateTimeTest",
            "type": "object",
            "properties": {"timestamp": {"type": "string", "format": "date-time"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(
            model(timestamp="2024-01-01T12:00:00Z").timestamp.isoformat(),
            "2024-01-01T12:00:00+00:00",
        )

        with self.assertRaises(ValidationError):
            model(timestamp="invalid-datetime")

    def test_string_format_time(self):
        schema = {
            "title": "TimeTest",
            "type": "object",
            "properties": {"time": {"type": "string", "format": "time"}},
        }

        model = SchemaConverter.build(schema)
        self.assertEqual(
            model(time="20:20:39+00:00").time.isoformat(), "20:20:39+00:00"
        )

        with self.assertRaises(ValidationError):
            model(time="25:00:00")

    def test_string_format_unsupported(self):
        schema = {
            "title": "InvalidFormat",
            "type": "object",
            "properties": {"field": {"type": "string", "format": "unsupported"}},
        }

        with self.assertRaises(InvalidSchemaException):
            SchemaConverter.build(schema)

    def test_ref_with_root_ref(self):
        schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "emergency_contact": {
                    "$ref": "#",
                },
            },
            "required": ["name", "age"],
        }

        model = SchemaConverter.build(schema)

        obj = model(
            name="John",
            age=30,
            emergency_contact=model(
                name="Jane",
                age=28,
            ),
        )

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertIsInstance(obj.emergency_contact, model)
        self.assertEqual(obj.emergency_contact.name, "Jane")
        self.assertEqual(obj.emergency_contact.age, 28)

    def test_ref_with_def(self):
        schema = {
            "title": "person",
            "$ref": "#/$defs/person",
            "$defs": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "emergency_contact": {
                            "$ref": "#/$defs/person",
                        },
                    },
                }
            },
        }

        model = SchemaConverter.build(schema)

        obj = model(
            name="John",
            age=30,
            emergency_contact=model(
                name="Jane",
                age=28,
            ),
        )

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertIsInstance(obj.emergency_contact, model)
        self.assertEqual(obj.emergency_contact.name, "Jane")
        self.assertEqual(obj.emergency_contact.age, 28)

    def test_ref_with_def_another_model(self):
        schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {"$ref": "#/$defs/Address"},
            },
            "required": ["name"],
            "$defs": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                    "required": ["street", "city"],
                }
            },
        }

        Model = SchemaConverter.build(schema)

        obj = Model(
            name="John",
            age=30,
            address={"street": "123 Main St", "city": "Springfield"},
        )

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertEqual(obj.address.street, "123 Main St")
        self.assertEqual(obj.address.city, "Springfield")

    def test_enum_type_parser(self):
        schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"],
                }
            },
            "required": ["status"],
        }

        Model = SchemaConverter.build(schema)

        obj = Model(status="active")
        self.assertEqual(obj.status.value, "active")

    def test_enum_type_parser_with_default(self):
        schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"],
                    "default": "active",
                }
            },
            "required": ["status"],
        }

        Model = SchemaConverter.build(schema)

        obj = Model()
        self.assertEqual(obj.status.value, "active")

    def test_const_type_parser(self):
        schema = {
            "title": "Country",
            "type": "object",
            "properties": {
                "name": {
                    "const": "United States of America",
                }
            },
            "required": ["name"],
        }

        Model = SchemaConverter.build(schema)

        obj = Model()
        self.assertEqual(obj.name, "United States of America")

        with self.assertRaises(ValidationError):
            obj.name = "Canada"

        with self.assertRaises(ValidationError):
            Model(name="Canada")

    def test_const_type_parser_with_non_hashable_value(self):
        schema = {
            "title": "Country",
            "type": "object",
            "properties": {
                "name": {
                    "const": ["Brazil"],
                }
            },
            "required": ["name"],
        }

        Model = SchemaConverter.build(schema)

        obj = Model()
        self.assertEqual(obj.name, ["Brazil"])

        with self.assertRaises(ValidationError):
            obj.name = ["Argentina"]

        with self.assertRaises(ValidationError):
            Model(name=["Argentina"])

    def test_null_type_parser(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "a_thing": {"type": "null"},
            },
        }

        Model = SchemaConverter.build(schema)

        obj = Model()
        self.assertIsNone(obj.a_thing)

        obj = Model(a_thing=None)
        self.assertIsNone(obj.a_thing)

        with self.assertRaises(ValidationError):
            Model(a_thing="not none")
