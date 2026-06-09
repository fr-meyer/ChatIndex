import os
import tempfile
import unittest

from ctree.ctree import CTree
from retrieval.llm_tools import ChatIndexTools


class EndToEndSmokeTests(unittest.TestCase):
    """Composed no-key smoke test for build/save/load/append/vector retrieval."""

    DISTINCTIVE_USER = "zephyr quartz closure marker question"
    DISTINCTIVE_ASSISTANT = "zephyr quartz closure marker assistant reply"

    def make_tree(self):
        return CTree(api_key="test-openai-key")

    def exchange(self, user_content, assistant_content):
        return [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ]

    def stub_llm_for_add(self, tree, *, belongs_to_current=True, topic_name="Smoke Topic"):
        tree._llm_generate_topic_from_message = lambda *args, **kwargs: topic_name
        tree._llm_summarize = lambda messages, topic_name: f"summary for {topic_name}"
        tree._llm_classify_message_exchange = lambda *args, **kwargs: {
            "belongs_to_current": belongs_to_current,
            "new_topic_name": topic_name,
            "new_topic_parent_index": 0,
        }
        tree._llm_split_subtopics = lambda messages, node: [
            {
                "topic_name": f"{node.topic_name} - Part 1",
                "summary": "first part",
                "start_offset": 0,
                "end_offset": len(messages) // 2,
            },
            {
                "topic_name": f"{node.topic_name} - Part 2",
                "summary": "second part",
                "start_offset": len(messages) // 2,
                "end_offset": len(messages),
            },
        ]

    def test_build_save_load_append_vector_search_and_message_retrieval(self):
        tree = self.make_tree()
        self.stub_llm_for_add(tree)
        tree.add(self.exchange("baseline planning question", "baseline planning answer"))
        tree.add(self.exchange("deployment strategy question", "deployment strategy answer"))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True)
            loaded = CTree.load(path, api_key="test-openai-key")

            self.assertEqual(len(loaded.conversation), 4)

            self.stub_llm_for_add(loaded, belongs_to_current=True)
            loaded.add(self.exchange(self.DISTINCTIVE_USER, self.DISTINCTIVE_ASSISTANT))

            self.assertEqual(len(loaded.conversation), 6)
            self.assertEqual(loaded.conversation[4]["content"], self.DISTINCTIVE_USER)
            self.assertEqual(loaded.conversation[5]["content"], self.DISTINCTIVE_ASSISTANT)

            tools = ChatIndexTools(loaded)
            search_result = tools.vector_search("zephyr quartz closure marker", top_k=1)

            self.assertNotIn("error", search_result)
            self.assertEqual(search_result["result_count"], 1)

            top_match = search_result["results"][0]
            self.assertEqual(top_match["message_index"], 4)
            self.assertEqual(top_match["start_index"], 4)
            self.assertEqual(top_match["end_index"], 6)

            messages = tools.get_node_messages(
                top_match["start_index"],
                top_match["end_index"],
            )

            self.assertNotIn("error", messages)
            self.assertEqual(messages["message_count"], 2)
            self.assertEqual(messages["messages"][0]["content"], self.DISTINCTIVE_USER)
            self.assertEqual(messages["messages"][1]["content"], self.DISTINCTIVE_ASSISTANT)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
