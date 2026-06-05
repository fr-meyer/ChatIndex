import unittest

from ctree.ctree import MessageNode, TopicNode


class BaselineStructureTests(unittest.TestCase):
    def test_topic_node_counts_message_children(self):
        topic = TopicNode(
            topic_name="Planning",
            summary="Discussion about project planning",
            start_index=0,
            end_index=1,
        )
        message = MessageNode(
            user_message={"content": "What is the plan?"},
            assistant_message={"content": "Create a baseline first."},
            message_index=0,
        )
        message.parent = topic
        topic.children.append(message)
        topic.update_sub_node_count()

        self.assertEqual(topic.sub_node_count, 1)
        self.assertEqual(topic.get_message_count(), 1)

    def test_message_node_serializes_preview_without_provider_keys(self):
        message = MessageNode(
            user_message={"content": "u" * 250},
            assistant_message={"content": "a" * 250},
            message_index=3,
        )

        serialized = message.to_dict()

        self.assertEqual(serialized["type"], "message")
        self.assertEqual(serialized["message_index"], 3)
        self.assertEqual(len(serialized["user"]), 200)
        self.assertEqual(len(serialized["assistant"]), 200)


if __name__ == "__main__":
    unittest.main()
