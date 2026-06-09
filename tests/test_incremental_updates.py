import os
import tempfile
import unittest

from ctree.ctree import CTree, MessageNode, TopicNode


class IncrementalUpdateTests(unittest.TestCase):
    def make_tree(self, max_children=5):
        return CTree(max_children=max_children, api_key="test-openai-key")

    def exchange(self, index):
        return [
            {"role": "user", "content": f"user message {index}"},
            {"role": "assistant", "content": f"assistant message {index}"},
        ]

    def stub_llm_for_append(self, tree, *, belongs_to_current=True, topic_name="Appended Topic"):
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

    def collect_message_indexes(self, node):
        indexes = []
        if isinstance(node, MessageNode):
            indexes.append(node.message_index)
        for child in node.children:
            indexes.extend(self.collect_message_indexes(child))
        return sorted(indexes)

    def find_topic_by_name(self, node, topic_name):
        if isinstance(node, TopicNode) and node.topic_name == topic_name:
            return node
        for child in node.children:
            found = self.find_topic_by_name(child, topic_name)
            if found is not None:
                return found
        return None

    def test_append_after_load_preserves_message_index_continuity(self):
        tree = self.make_tree()
        self.stub_llm_for_append(tree, topic_name="Initial Topic")
        tree.add(self.exchange(0))
        tree.add(self.exchange(1))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True)
            loaded = CTree.load(path, api_key="test-openai-key")

            self.assertEqual(len(loaded.conversation), 4)
            self.assertEqual(self.collect_message_indexes(loaded.root), [0, 2])

            self.stub_llm_for_append(loaded, belongs_to_current=True)
            loaded.add(self.exchange(2))

            self.assertEqual(len(loaded.conversation), 6)
            self.assertEqual(self.collect_message_indexes(loaded.root), [0, 2, 4])
            self.assertEqual(loaded.conversation[4]["content"], "user message 2")
            self.assertEqual(loaded.conversation[5]["content"], "assistant message 2")
        finally:
            os.unlink(path)

    def test_loaded_current_node_is_append_target(self):
        tree = self.make_tree()
        tree._llm_generate_topic_from_message = lambda *args, **kwargs: "First Topic"
        classifications = [{
            "belongs_to_current": False,
            "new_topic_name": "Second Topic",
            "new_topic_parent_index": 1,
        }]

        def classify(*args, **kwargs):
            return classifications.pop(0)

        tree._llm_classify_message_exchange = classify
        tree.add(self.exchange(0))
        tree.add(self.exchange(1))
        expected_current = tree.current_node.topic_name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True)
            loaded = CTree.load(path, api_key="test-openai-key")

            self.assertEqual(loaded.current_node.topic_name, expected_current)
            self.stub_llm_for_append(loaded, belongs_to_current=True)
            loaded.add(self.exchange(2))

            appended_messages = [
                child for child in loaded.current_node.children
                if isinstance(child, MessageNode) and child.message_index == 4
            ]
            self.assertEqual(len(appended_messages), 1)
            self.assertEqual(appended_messages[0].message_index, 4)
            self.assertEqual(appended_messages[0].user_message["content"], "user message 2")
        finally:
            os.unlink(path)

    def test_append_updates_ancestor_and_root_end_indices(self):
        tree = self.make_tree()
        self.stub_llm_for_append(tree, topic_name="Topic")
        tree.add(self.exchange(0))
        tree.add(self.exchange(1))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True)
            loaded = CTree.load(path, api_key="test-openai-key")
            self.stub_llm_for_append(loaded, belongs_to_current=True)
            loaded.add(self.exchange(2))

            ancestors = loaded.get_ancestors(loaded.current_node, include_self=True)
            for ancestor in ancestors:
                self.assertEqual(ancestor.end_index, len(loaded.conversation))
            self.assertEqual(loaded.root.end_index, 6)
        finally:
            os.unlink(path)

    def test_append_uses_path_local_reorganization(self):
        tree = self.make_tree(max_children=2)
        active = TopicNode(topic_name="Active", start_index=0, end_index=4, parent=tree.root)
        unrelated = TopicNode(
            topic_name="Unrelated",
            summary="frozen branch",
            start_index=0,
            end_index=6,
            parent=tree.root,
        )
        active.children.extend([
            MessageNode(
                user_message={"content": "active user 0"},
                assistant_message={"content": "active assistant 0"},
                message_index=0,
                parent=active,
            ),
            MessageNode(
                user_message={"content": "active user 1"},
                assistant_message={"content": "active assistant 1"},
                message_index=2,
                parent=active,
            ),
        ])
        unrelated.children.extend([
            MessageNode(message_index=0, parent=unrelated),
            MessageNode(message_index=2, parent=unrelated),
            MessageNode(message_index=4, parent=unrelated),
        ])
        tree.root.children.extend([unrelated, active])
        tree.root.end_index = 4
        tree.conversation = [
            {"role": "user", "content": "active user 0"},
            {"role": "assistant", "content": "active assistant 0"},
            {"role": "user", "content": "active user 1"},
            {"role": "assistant", "content": "active assistant 1"},
        ]
        tree.current_node = active

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True)
            loaded = CTree.load(path, api_key="test-openai-key")
            loaded.current_node = self.find_topic_by_name(loaded.root, "Active")
            expanded = []

            def record_expand(node):
                expanded.append(node.topic_name)

            loaded._expand_node = record_expand
            self.stub_llm_for_append(loaded, belongs_to_current=True)
            loaded.add(self.exchange(2))

            self.assertEqual(expanded, ["Active"])
            self.assertEqual(len(self.find_topic_by_name(loaded.root, "Unrelated").children), 3)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
