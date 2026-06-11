"""Unit tests for extract_json utility hardening."""

import unittest
from ctree.utils import extract_json


class ExtractJsonTests(unittest.TestCase):

    def test_standard_json_object(self):
        result = extract_json('{"key": "value"}')
        self.assertEqual(result, {"key": "value"})

    def test_preserves_string_containing_none(self):
        result = extract_json('{"key": "None is the value"}')
        self.assertEqual(result, {"key": "None is the value"})

    def test_preserves_string_containing_none_keyword(self):
        result = extract_json('{"key": "None"}')
        self.assertEqual(result, {"key": "None"})

    def test_preserves_string_containing_true_word(self):
        result = extract_json('{"key": "True story"}')
        self.assertEqual(result, {"key": "True story"})

    def test_preserves_string_containing_false_word(self):
        result = extract_json('{"key": "False alarm"}')
        self.assertEqual(result, {"key": "False alarm"})

    def test_parses_python_none_as_null(self):
        result = extract_json('{"key": None}')
        self.assertIsNone(result["key"])

    def test_parses_python_true(self):
        result = extract_json('{"key": True}')
        self.assertIs(result["key"], True)

    def test_parses_python_false(self):
        result = extract_json('{"key": False}')
        self.assertIs(result["key"], False)

    def test_parses_python_literals_with_string_containing_none(self):
        result = extract_json('{"value": "None", "flag": None}')
        self.assertEqual(result["value"], "None")
        self.assertIsNone(result["flag"])

    def test_parses_python_literals_with_mixed_types(self):
        content = '{"name": "test", "count": 42, "active": True, "alt": None, "disabled": False}'
        result = extract_json(content)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["count"], 42)
        self.assertIs(result["active"], True)
        self.assertIsNone(result["alt"])
        self.assertIs(result["disabled"], False)

    def test_fenced_json_block(self):
        content = 'Some preamble\n```json\n{"key": "value"}\n```\nSome epilogue'
        result = extract_json(content)
        self.assertEqual(result, {"key": "value"})

    def test_fenced_python_literal_block(self):
        content = '```json\n{"key": None, "flag": True}\n```'
        result = extract_json(content)
        self.assertIsNone(result["key"])
        self.assertIs(result["flag"], True)

    def test_fenced_with_string_containing_none(self):
        content = '```json\n{"key": "None", "val": None}\n```'
        result = extract_json(content)
        self.assertEqual(result["key"], "None")
        self.assertIsNone(result["val"])

    def test_malformed_content_returns_empty_dict(self):
        result = extract_json("not json at all")
        self.assertEqual(result, {})

    def test_empty_string_returns_empty_dict(self):
        result = extract_json("")
        self.assertEqual(result, {})

    def test_standard_json_null(self):
        result = extract_json('{"key": null}')
        self.assertIsNone(result["key"])

    def test_standard_json_bool(self):
        result = extract_json('{"flag": true, "off": false}')
        self.assertIs(result["flag"], True)
        self.assertIs(result["off"], False)

    def test_nested_structures(self):
        content = '{"items": [1, 2, 3], "meta": {"active": True, "label": None}}'
        result = extract_json(content)
        self.assertEqual(result["items"], [1, 2, 3])
        self.assertIs(result["meta"]["active"], True)
        self.assertIsNone(result["meta"]["label"])

    def test_array_at_top_level(self):
        result = extract_json("[1, 2, 3]")
        self.assertEqual(result, [1, 2, 3])

    def test_array_with_python_literals(self):
        result = extract_json("[None, True, False, 42, 'hello']")
        self.assertEqual(result, [None, True, False, 42, "hello"])

    def test_none_inside_nested_strings(self):
        content = '{"a": "none", "b": "None", "c": "NONE", "d": None}'
        result = extract_json(content)
        self.assertEqual(result["a"], "none")
        self.assertEqual(result["b"], "None")
        self.assertEqual(result["c"], "NONE")
        self.assertIsNone(result["d"])


if __name__ == "__main__":
    unittest.main()
