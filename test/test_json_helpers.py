import io
import json
import unittest
from enum import auto

import jsonlines

from pytils.json_helpers import DefaultJSONDecoder, default_json_dumps, DefaultJSONEncoder, default_json_loads, \
    JSONEnum, JSONSerializable


class ExampleEnum(JSONEnum):
    ONE = auto()
    TWO = auto()


class ExampleWithEnumExampleJSONSerializable(JSONSerializable):
    def __init__(self, string: str = "bar"):
        super().__init__(string=string)
        self.enum = ExampleEnum.TWO


class ExampleJSONSerializable(JSONSerializable):
    def __init__(self, string: str = "bar"):
        super().__init__()
        self.string = string
        self.list = ["hello", "world"]
        self.dict = {"fruit": "banana"}


class ExampleSubclassJSONSerializable(ExampleJSONSerializable):
    def __init__(self):
        super().__init__()
        self.child = "child"


class ExampleMemberObjectJSONSerializable(JSONSerializable):
    def __init__(self):
        super().__init__()
        self.left = ExampleJSONSerializable("foo")
        self.right = ExampleJSONSerializable("bar")


class TestJSONHelpers(unittest.TestCase):
    def test_simple(self):
        data = ExampleJSONSerializable()
        encoded = json.dumps(data, cls=DefaultJSONEncoder)
        decoded = json.loads(encoded, cls=DefaultJSONDecoder)
        self.assertDictEqual(data.__dict__, decoded.__dict__)

    def test_subclass(self):
        data = ExampleSubclassJSONSerializable()
        encoded = json.dumps(data, cls=DefaultJSONEncoder)
        decoded = json.loads(encoded, cls=DefaultJSONDecoder)
        self.assertDictEqual(data.__dict__, decoded.__dict__)

    def test_member_objects_subclass(self):
        data = ExampleMemberObjectJSONSerializable()
        encoded = json.dumps(data, cls=DefaultJSONEncoder)
        decoded = json.loads(encoded, cls=DefaultJSONDecoder)
        self.assertDictEqual(data.left.__dict__, decoded.left.__dict__)
        self.assertDictEqual(data.right.__dict__, decoded.right.__dict__)

    def test_enum(self):
        data = ExampleWithEnumExampleJSONSerializable()
        encoded = json.dumps(data, cls=DefaultJSONEncoder)
        decoded = json.loads(encoded, cls=DefaultJSONDecoder)
        self.assertDictEqual(data.__dict__, decoded.__dict__)


class TestJSONLinesHelpers(unittest.TestCase):
    def test_simple(self):
        buffer = io.StringIO()
        data_1 = ExampleJSONSerializable("Hello")
        data_2 = ExampleJSONSerializable("World")
        data_3 = ExampleJSONSerializable("Test")
        with jsonlines.Writer(buffer, dumps=default_json_dumps) as writer:
            writer.write(data_1)
            writer.write(data_2)
            writer.write(data_3)

        output_string = buffer.getvalue()
        buffer.close()

        buffer = io.StringIO(output_string)
        with jsonlines.Reader(buffer, loads=default_json_loads) as reader:
            results = [x for x in reader]

        self.assertDictEqual(results[0].__dict__, data_1.__dict__)
        self.assertDictEqual(results[1].__dict__, data_2.__dict__)
        self.assertDictEqual(results[2].__dict__, data_3.__dict__)
