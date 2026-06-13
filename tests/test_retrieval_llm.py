import json
import os
import unittest
from types import SimpleNamespace

from ctree.ctree import CTree, MessageNode, TopicNode
from retrieval.llm_tools import (
    AnthropicRetrievalClient,
    ChatIndexTools,
    OpenAIRetrievalClient,
    RetrievalResponse,
    TextBlock,
    ToolUseBlock,
    TOOLS,
    build_retrieval_client,
    query_ctree,
    query_ctree_streaming,
)
from retrieval.vector_index import VectorIndex, _exchange_range, deterministic_embed


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


def make_multi_exchange_tree():
    exchanges = [
        ("What is the plan?", "Create a baseline first."),
        ("How do we deploy?", "Use container orchestration with Kubernetes."),
        ("What about testing?", "Write unit tests for each module."),
    ]

    conversation = []
    root = TopicNode(
        topic_name="ROOT",
        summary="Virtual root",
        start_index=0,
        end_index=0,
    )
    topic = TopicNode(
        topic_name="Project",
        summary="Project discussion",
        start_index=0,
        end_index=0,
        parent=root,
    )

    for user_text, assistant_text in exchanges:
        user_message = {"role": "user", "content": user_text}
        assistant_message = {"role": "assistant", "content": assistant_text}
        start_index = len(conversation)
        conversation.extend([user_message, assistant_message])
        topic.children.append(MessageNode(
            user_message=user_message,
            assistant_message=assistant_message,
            message_index=start_index,
            parent=topic,
        ))

    topic.end_index = len(conversation)
    root.children.append(topic)
    root.end_index = len(conversation)
    root.update_sub_node_count()

    return SimpleNamespace(root=root, conversation=conversation)


class VectorIndexTests(unittest.TestCase):
    def test_deterministic_embedding_is_stable(self):
        text = "kubernetes deployment orchestration"
        first = deterministic_embed(text)
        second = deterministic_embed(text)

        self.assertEqual(first, second)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0, places=6)

    def test_vector_search_ranks_most_relevant_exchange_first(self):
        index = VectorIndex.from_ctree(make_multi_exchange_tree())
        results = index.search("kubernetes deployment orchestration", top_k=3)

        self.assertGreaterEqual(len(results), 2)
        top_result = results[0]
        self.assertEqual(top_result["message_index"], 2)
        self.assertIn("deploy", top_result["text_preview"])
        self.assertIn("Kubernetes", top_result["assistant_preview"])
        self.assertNotIn("source_text", top_result)
        self.assertEqual(top_result["start_index"], 2)
        self.assertEqual(top_result["end_index"], 4)
        self.assertGreater(top_result["score"], results[1]["score"])

    def test_vector_search_bounds_top_k_and_preserves_stable_order(self):
        index = VectorIndex.from_ctree(make_multi_exchange_tree())

        bounded = index.search("project planning testing deploy", top_k=2)
        self.assertEqual(len(bounded), 2)

        string_top_k = index.search("project planning testing deploy", top_k="2")
        self.assertEqual(len(string_top_k), 2)

        excessive = index.search("project planning testing deploy", top_k=100)
        self.assertEqual(len(excessive), 3)

        repeated = index.search("project planning testing deploy", top_k=3)
        self.assertEqual(
            [result["message_index"] for result in repeated],
            [result["message_index"] for result in excessive],
        )

    def test_system_message_exchange_range_matches_conversation_slice(self):
        tree = CTree(api_key="test-key")
        tree._llm_generate_topic_from_message = lambda *args, **kwargs: "System Setup"
        tree.add([
            {"role": "system", "content": "Use concise deployment answers."},
            {"role": "user", "content": "How do we deploy?"},
            {"role": "assistant", "content": "Deploy with Kubernetes."},
        ])

        message_node = tree.root.children[0].children[0]
        self.assertIsInstance(message_node, MessageNode)
        self.assertEqual(_exchange_range(message_node), (0, 3))

        tools = ChatIndexTools(tree)
        messages = tools.get_node_messages(0, 3)
        self.assertEqual(messages["message_count"], 3)
        self.assertEqual(
            [message["role"] for message in messages["messages"]],
            ["system", "user", "assistant"],
        )

        vector_result = tools.vector_search("kubernetes deployment", top_k=1)
        self.assertEqual(vector_result["results"][0]["start_index"], 0)
        self.assertEqual(vector_result["results"][0]["end_index"], 3)


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

    def test_openai_provider_accepts_openai_compatible_base_url(self):
        client = build_retrieval_client(
            provider="openai",
            model="qwen-test",
            base_url="https://example.invalid/compatible-mode/v1",
            **{"api_key": "test-openai-compatible-key"},
        )

        self.assertIsInstance(client, OpenAIRetrievalClient)
        self.assertEqual(client.config.model, "qwen-test")
        self.assertEqual(
            client.config.base_url,
            "https://example.invalid/compatible-mode/v1",
        )

    def test_openai_provider_reads_base_url_from_environment(self):
        previous_base_url = os.environ.get("OPENAI_BASE_URL")
        previous_api_base = os.environ.get("OPENAI_API_BASE")
        try:
            os.environ["OPENAI_BASE_URL"] = "https://example.invalid/v1"
            os.environ.pop("OPENAI_API_BASE", None)

            client = build_retrieval_client(
                provider="openai",
                model="qwen-test",
                **{"api_key": "test-openai-compatible-key"},
            )

            self.assertEqual(client.config.base_url, "https://example.invalid/v1")
        finally:
            if previous_base_url is None:
                os.environ.pop("OPENAI_BASE_URL", None)
            else:
                os.environ["OPENAI_BASE_URL"] = previous_base_url
            if previous_api_base is None:
                os.environ.pop("OPENAI_API_BASE", None)
            else:
                os.environ["OPENAI_API_BASE"] = previous_api_base

    def test_unsupported_provider_fails_before_retrieval_loop(self):
        with self.assertRaisesRegex(ValueError, "Unsupported retrieval provider"):
            query_ctree(
                api_key="test-key",
                ctree=make_tree(),
                user_query="What happened?",
                provider="local-llm",
                max_turns=1,
            )

    def test_vector_search_tool_is_exposed_in_shared_tool_list(self):
        tool_names = {tool["name"] for tool in TOOLS}
        self.assertIn("vector_search", tool_names)
        self.assertIn("view_node_and_children", tool_names)
        self.assertIn("get_node_messages", tool_names)

    def test_fake_client_runs_vector_search_tool_loop_without_api_key(self):
        fake_client = FakeRetrievalClient([
            RetrievalResponse(
                stop_reason="tool_use",
                content=[
                    ToolUseBlock(
                        id="tool-1",
                        name="vector_search",
                        input={"query": "kubernetes container orchestration", "top_k": 1},
                    )
                ],
            ),
            RetrievalResponse(
                stop_reason="end_turn",
                content=[TextBlock("Deployment uses Kubernetes.")],
            ),
        ])

        result = query_ctree(
            api_key=None,
            ctree=make_multi_exchange_tree(),
            user_query="How do we deploy?",
            max_turns=2,
            llm_client=fake_client,
        )

        self.assertTrue(result["success"])
        tool_result = json.loads(
            fake_client.calls[1]["messages"][-1]["content"][0]["content"]
        )
        self.assertEqual(tool_result["top_k"], 1)
        self.assertEqual(tool_result["result_count"], 1)
        self.assertEqual(tool_result["results"][0]["message_index"], 2)
        self.assertEqual(tool_result["results"][0]["start_index"], 2)
        self.assertEqual(tool_result["results"][0]["end_index"], 4)

        tools = ChatIndexTools(make_multi_exchange_tree())
        messages = tools.get_node_messages(
            tool_result["results"][0]["start_index"],
            tool_result["results"][0]["end_index"],
        )
        self.assertEqual(messages["message_count"], 2)
        self.assertIn("Kubernetes", messages["messages"][1]["content"])

    def test_view_node_rejects_negative_root_index(self):
        tools = ChatIndexTools(make_tree())

        result = tools.view_node_and_children([-1])

        self.assertIn("error", result)
        self.assertEqual(result["valid_indices"], [0])
        self.assertIn("-1", result["error"])

    def test_view_node_rejects_nested_negative_index(self):
        tools = ChatIndexTools(make_tree())

        result = tools.view_node_and_children([0, -1])

        self.assertIn("error", result)
        self.assertEqual(result["valid_indices"], [0])
        self.assertIn("-1", result["error"])

    def test_view_node_rejects_boolean_root_index(self):
        tools = ChatIndexTools(make_tree())

        result = tools.view_node_and_children([True])

        self.assertIn("error", result)
        self.assertEqual(result["valid_indices"], [0])
        self.assertIn("True", result["error"])

    def test_view_node_rejects_nested_boolean_index(self):
        tools = ChatIndexTools(make_tree())

        result = tools.view_node_and_children([0, False])

        self.assertIn("error", result)
        self.assertEqual(result["valid_indices"], [0])
        self.assertIn("False", result["error"])

    def test_view_node_valid_path_still_navigates(self):
        tools = ChatIndexTools(make_tree())

        result = tools.view_node_and_children([0])

        self.assertNotIn("error", result)
        self.assertEqual(result["node_type"], "topic")
        self.assertEqual(result["topic_name"], "Planning")


if __name__ == "__main__":
    unittest.main()
