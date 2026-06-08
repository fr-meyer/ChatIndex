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


if __name__ == "__main__":
    unittest.main()
