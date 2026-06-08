import unittest

from ctree.ctree import CTree, MessageNode, TopicNode


class OfflineTreeOptimizationTests(unittest.TestCase):
    def make_tree(self, max_children=2):
        return CTree(max_children=max_children, api_key="test-openai-key")

    def test_get_ancestors_keeps_root_to_leaf_order(self):
        tree = self.make_tree()
        root = tree.root
        topic = TopicNode(topic_name="Topic", parent=root)
        subtopic = TopicNode(topic_name="Subtopic", parent=topic)
        root.children.append(topic)
        topic.children.append(subtopic)

        self.assertEqual(
            [node.topic_name for node in tree.get_ancestors(subtopic)],
            ["ROOT", "Topic", "Subtopic"],
        )
        self.assertEqual(
            [node.topic_name for node in tree.get_ancestors(subtopic, include_self=False)],
            ["ROOT", "Topic"],
        )
        self.assertEqual(
            [node.topic_name for node in tree.get_ancestors(subtopic, exclude_root=True)],
            ["Topic", "Subtopic"],
        )

    def test_path_local_reorganization_ignores_unrelated_overflow(self):
        tree = self.make_tree(max_children=2)
        changed = TopicNode(topic_name="Changed", parent=tree.root)
        unrelated = TopicNode(topic_name="Unrelated", parent=tree.root)
        unrelated.children.extend([
            MessageNode(message_index=1, parent=unrelated),
            MessageNode(message_index=2, parent=unrelated),
            MessageNode(message_index=3, parent=unrelated),
        ])
        tree.root.children.extend([changed, unrelated])

        expanded = []

        def record_expand(node):
            expanded.append(node.topic_name)

        tree._expand_node = record_expand

        tree._check_and_reorganize_nodes(start_node=changed)

        self.assertEqual(expanded, [])

    def test_path_local_reorganization_rechecks_parent_after_split(self):
        tree = self.make_tree(max_children=2)
        parent = TopicNode(topic_name="Parent", parent=tree.root)
        overflowing_child = TopicNode(topic_name="Child", parent=parent)
        sibling = TopicNode(topic_name="Sibling", parent=parent)
        overflowing_child.children.extend([
            TopicNode(topic_name="Child A", parent=overflowing_child),
            TopicNode(topic_name="Child B", parent=overflowing_child),
            TopicNode(topic_name="Child C", parent=overflowing_child),
        ])
        parent.children.extend([overflowing_child, sibling])
        tree.root.children.append(parent)

        split_order = []

        def fake_split(node):
            split_order.append(node.topic_name)
            if node.parent is None:
                return
            first = TopicNode(topic_name=f"{node.topic_name} 1", parent=node.parent)
            second = TopicNode(topic_name=f"{node.topic_name} 2", parent=node.parent)
            node.parent.children.remove(node)
            node.parent.children.extend([first, second])

        tree._split_node = fake_split

        tree._check_and_reorganize_nodes(start_node=overflowing_child)

        self.assertEqual(split_order, ["Child", "Parent"])

    def test_split_node_preserves_direct_message_children(self):
        tree = self.make_tree(max_children=2)
        parent = TopicNode(topic_name="Parent", parent=tree.root)
        node = TopicNode(topic_name="Mixed", parent=parent)
        topic_a = TopicNode(topic_name="A", start_index=0, end_index=1, parent=node)
        topic_b = TopicNode(topic_name="B", start_index=1, end_index=2, parent=node)
        topic_c = TopicNode(topic_name="C", start_index=3, end_index=4, parent=node)
        message_between = MessageNode(message_index=2, parent=node)
        message_after = MessageNode(message_index=4, parent=node)
        node.children.extend([topic_a, topic_b, message_between, topic_c, message_after])
        parent.children.append(node)
        tree.root.children.append(parent)

        tree._llm_find_split_point = lambda topic_children, parent_node: 2
        tree._llm_generate_topic_from_children = (
            lambda topic_children, parent_node: " / ".join(
                topic.topic_name for topic in topic_children
            )
        )

        tree._split_node(node)

        first_node, second_node = parent.children
        self.assertIn(message_between, first_node.children)
        self.assertIn(message_after, second_node.children)
        self.assertIs(message_between.parent, first_node)
        self.assertIs(message_after.parent, second_node)
        self.assertEqual((first_node.start_index, first_node.end_index), (0, 3))
        self.assertEqual((second_node.start_index, second_node.end_index), (3, 5))


if __name__ == "__main__":
    unittest.main()
