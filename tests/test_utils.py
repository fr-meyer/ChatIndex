import unittest

from ctree.utils import extract_json


class ExtractJsonTests(unittest.TestCase):
    def test_extracts_fenced_json(self):
        content = """
        Here is the result:

        ```json
        {
          "topic_name": "Planning",
          "belongs_to_current": true
        }
        ```
        """

        parsed = extract_json(content)

        self.assertEqual(parsed["topic_name"], "Planning")
        self.assertTrue(parsed["belongs_to_current"])

    def test_extracts_python_literal_values_from_model_output(self):
        content = "{'topic_name': None, 'belongs_to_current': True, 'children': []}"

        parsed = extract_json(content)

        self.assertIsNone(parsed["topic_name"])
        self.assertTrue(parsed["belongs_to_current"])
        self.assertEqual(parsed["children"], [])

    def test_preserves_none_inside_string_values(self):
        content = '{"summary": "None of this should become null"}'

        parsed = extract_json(content)

        self.assertEqual(parsed["summary"], "None of this should become null")

    def test_removes_trailing_commas_before_json_parse(self):
        content = '{"topic_name": "Planning", "children": [],}'

        parsed = extract_json(content)

        self.assertEqual(parsed["topic_name"], "Planning")
        self.assertEqual(parsed["children"], [])

    def test_returns_empty_dict_for_unparseable_content(self):
        self.assertEqual(extract_json("not json at all"), {})


if __name__ == "__main__":
    unittest.main()
