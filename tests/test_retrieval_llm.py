import unittest
from types import SimpleNamespace

from ctree.ctree import MessageNode, TopicNode
from retrieval.llm_tools import (
    AnthropicRetrievalClient,
    OpenAIRetrievalClient,
    RetrievalResponse,
    TextBlock,
    ToolUseBlock,
    build_retrieval_client,
    query_ctree,
    query_ctree_streaming,
)


class FakeRetrievalClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create_message(self, system, tools, messages):
        self.calls.append({
            "system": system,
            "tools": tools,
            "messages": messages,
        })
        return self.responses.pop(0)

    def stream_message(self, system, tools, messages, on_text_chunk=None):
        response = self.create_message(system, tools, messages)
        if on_text_chunk:
            for block in response.content:
                if block.type == "text":
                    on_text_chunk(block.text)
        return response


def make_tree():
    user_message = {"role": "user", "content": "What is the plan?"}
    assistant_message = {"role": "assistant", "content": "Create a baseline first."}

    root = TopicNode(
        topic_name="ROOT",
        summary="Virtual root",
        start_index=0,
        end_index=2,
    )
    topic = TopicNode(
        topic_name="Planning",
        summary="Discussion about project planning",
        start_index=0,
        end_index=2,
        parent=root,
    )
    message = MessageNode(
        user_message=user_message,
        assistant_message=assistant_message,
        message_index=0,
        parent=topic,
    )

    topic.children.append(message)
    root.children.append(topic)
    root.update_sub_node_count()

    return SimpleNamespace(
        root=root,
        conversation=[user_message, assistant_message],
    )


class RetrievalProviderTests(unittest.TestCase):
    def test_fake_client_runs_tool_loop_without_api_key(self):
        fake_client = FakeRetrievalClient([
            RetrievalResponse(
                stop_reason="tool_use",
                content=[
                    ToolUseBlock(
                        id="tool-1",
                        name="view_node_and_children",
                        input={"node_path": []},
                    )
                ],
            ),
            RetrievalResponse(
                stop_reason="end_turn",
                content=[TextBlock("The plan was to create a baseline first.")],
            ),
        ])

        result = query_ctree(
            api_key=None,
            ctree=make_tree(),
            user_query="What was the plan?",
            max_turns=2,
            llm_client=fake_client,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["turns_used"], 2)
        self.assertIn("baseline", result["final_response"])
        self.assertEqual(len(fake_client.calls), 2)
        self.assertEqual(
            fake_client.calls[1]["messages"][-1]["content"][0]["type"],
            "tool_result",
        )

    def test_streaming_fake_client_uses_shared_provider_interface(self):
        chunks = []
        fake_client = FakeRetrievalClient([
            RetrievalResponse(
                stop_reason="end_turn",
                content=[TextBlock("Streaming answer")],
            ),
        ])

        result = query_ctree_streaming(
            api_key=None,
            ctree=make_tree(),
            user_query="Summarize",
            max_turns=1,
            llm_client=fake_client,
            on_text_chunk=chunks.append,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["final_response"], "Streaming answer")
        self.assertEqual(chunks, ["Streaming answer"])

    def test_provider_selection_sets_explicit_models(self):
        anthropic_client = build_retrieval_client(
            api_key="test-anthropic-key",
            provider="anthropic",
            model="claude-test",
            max_tokens=123,
        )
        openai_client = build_retrieval_client(
            api_key="test-openai-key",
            provider="openai",
            model="gpt-test",
            max_tokens=456,
        )

        self.assertIsInstance(anthropic_client, AnthropicRetrievalClient)
        self.assertEqual(anthropic_client.config.model, "claude-test")
        self.assertEqual(anthropic_client.config.max_tokens, 123)

        self.assertIsInstance(openai_client, OpenAIRetrievalClient)
        self.assertEqual(openai_client.config.model, "gpt-test")
        self.assertEqual(openai_client.config.max_tokens, 456)

    def test_unsupported_provider_fails_before_retrieval_loop(self):
        with self.assertRaisesRegex(ValueError, "Unsupported retrieval provider"):
            query_ctree(
                api_key="test-key",
                ctree=make_tree(),
                user_query="What happened?",
                provider="local-llm",
                max_turns=1,
            )


if __name__ == "__main__":
    unittest.main()
