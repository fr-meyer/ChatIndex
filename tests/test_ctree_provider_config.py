import json
import os
import tempfile
import unittest
from unittest.mock import patch

from ctree.ctree import CTree, CTreeBuildTimeoutError, TopicNode
from ctree.utils import ChatGPT_API


def make_candidate_nodes():
    root = TopicNode(
        topic_name="ROOT",
        summary="Virtual root",
        start_index=0,
        end_index=2,
    )
    current = TopicNode(
        topic_name="Current Topic",
        summary="Current conversation topic",
        start_index=0,
        end_index=2,
        parent=root,
    )
    root.children.append(current)
    return [root, current]


class CTreeProviderConfigTests(unittest.TestCase):
    def test_ctree_accepts_openai_compatible_base_url(self):
        tree = CTree(
            model="qwen-test",
            base_url="https://example.invalid/compatible-mode/v1",
            **{"api_key": "test-openai-compatible-key"},
        )

        self.assertEqual(tree.api_key, "test-openai-compatible-key")
        self.assertEqual(tree.model, "qwen-test")
        self.assertEqual(
            tree.base_url,
            "https://example.invalid/compatible-mode/v1",
        )

    def test_ctree_reads_base_url_from_environment(self):
        previous_base_url = os.environ.get("OPENAI_BASE_URL")
        previous_api_base = os.environ.get("OPENAI_API_BASE")
        try:
            os.environ["OPENAI_BASE_URL"] = "https://example.invalid/v1"
            os.environ.pop("OPENAI_API_BASE", None)

            tree = CTree(**{"api_key": "test-openai-compatible-key"})

            self.assertEqual(tree.base_url, "https://example.invalid/v1")
        finally:
            if previous_base_url is None:
                os.environ.pop("OPENAI_BASE_URL", None)
            else:
                os.environ["OPENAI_BASE_URL"] = previous_base_url
            if previous_api_base is None:
                os.environ.pop("OPENAI_API_BASE", None)
            else:
                os.environ["OPENAI_API_BASE"] = previous_api_base

    def test_load_accepts_openai_compatible_base_url(self):
        tree = CTree(**{"api_key": "test-openai-compatible-key"})
        payload = tree.to_dict()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            path = handle.name

        try:
            loaded = CTree.load(
                path,
                model="qwen-test",
                base_url="https://example.invalid/compatible-mode/v1",
                **{"api_key": "test-openai-compatible-key"},
            )

            self.assertEqual(loaded.model, "qwen-test")
            self.assertEqual(
                loaded.base_url,
                "https://example.invalid/compatible-mode/v1",
            )
        finally:
            os.unlink(path)

    def test_chatgpt_api_passes_base_url_to_openai_client(self):
        captured = {}

        class FakeMessage:
            content = "ok"

        class FakeChoice:
            message = FakeMessage()

        class FakeCompletions:
            def create(self, **kwargs):
                captured["request"] = kwargs
                return type("Response", (), {"choices": [FakeChoice()]})()

        class FakeChat:
            completions = FakeCompletions()

        class FakeOpenAI:
            def __init__(self, **kwargs):
                captured["client"] = kwargs
                self.chat = FakeChat()

        with patch("ctree.utils.openai.OpenAI", FakeOpenAI):
            response = ChatGPT_API(
                "qwen-test",
                "Say ok",
                base_url="https://example.invalid/v1",
                timeout=42,
                max_retries=1,
                **{"api_key": "test-key"},
            )

        self.assertEqual(response, "ok")
        self.assertEqual(
            captured["client"],
            {
                "api_key": "test-key",
                "base_url": "https://example.invalid/v1",
                "timeout": 42,
            },
        )
        self.assertEqual(captured["request"]["model"], "qwen-test")

    def test_ctree_passes_timeout_and_retry_policy_to_api_helper(self):
        captured = {}

        def fake_chatgpt_api(model, prompt, **kwargs):
            captured.update(kwargs)
            return "ok"

        tree = CTree(
            request_timeout_seconds=45,
            request_max_retries=3,
            **{"api_key": "test-openai-compatible-key"},
        )

        with patch("ctree.ctree.ChatGPT_API", fake_chatgpt_api):
            response = tree._chatgpt_api("Say ok")

        self.assertEqual(response, "ok")
        self.assertEqual(captured["timeout"], 45)
        self.assertEqual(captured["max_retries"], 4)
        self.assertEqual(captured["api_key"], "test-openai-compatible-key")

    def test_ctree_normalizes_request_timeout_and_zero_retries(self):
        captured = {}

        def fake_chatgpt_api(model, prompt, **kwargs):
            captured.update(kwargs)
            return "ok"

        tree = CTree(
            request_timeout_seconds=-5,
            request_max_retries=0,
            **{"api_key": "test-openai-compatible-key"},
        )

        with patch("ctree.ctree.ChatGPT_API", fake_chatgpt_api):
            response = tree._chatgpt_api("Say ok")

        self.assertEqual(response, "ok")
        self.assertEqual(tree.request_timeout_seconds, 0.0)
        self.assertEqual(tree.request_max_retries, 0)
        self.assertEqual(captured["timeout"], 0.0)
        self.assertEqual(captured["max_retries"], 1)

    def test_ctree_build_timeout_has_slice_guidance(self):
        tree = CTree(
            build_timeout_seconds=0,
            **{"api_key": "test-openai-compatible-key"},
        )

        with self.assertRaisesRegex(CTreeBuildTimeoutError, "smaller conversation slice"):
            tree.add([
                {"role": "user", "content": "What is the plan?"},
                {"role": "assistant", "content": "Create a baseline first."},
            ])

    def test_ctree_emits_safe_progress_events_for_build(self):
        events = []
        tree = CTree(
            progress_callback=events.append,
            progress_interval_seconds=999,
            **{"api_key": "test-openai-compatible-key"},
        )
        tree._chatgpt_api = lambda *args, **kwargs: "Planning"

        tree.add([
            {"role": "user", "content": "What is the plan?"},
            {"role": "assistant", "content": "Create a baseline first."},
        ])

        event_names = [event["event"] for event in events]
        self.assertIn("exchange_started", event_names)
        self.assertIn("exchange_completed", event_names)
        self.assertEqual(events[-1]["exchange_count"], 1)
        self.assertNotIn("prompt", events[-1])
        self.assertNotIn("messages", events[-1])

    def test_save_can_skip_summary_generation_for_bounded_dogfood(self):
        tree = CTree(**{"api_key": "test-openai-compatible-key"})
        tree._generate_summaries_for_frozen_nodes = lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("summary generation should not run")
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            path = handle.name

        try:
            tree.save(path, save_conversation=True, generate_summaries=False)
            with open(path, encoding="utf-8") as saved_file:
                saved = json.loads(saved_file.read())
            self.assertIn("conversation", saved)
        finally:
            os.unlink(path)

    def test_exchange_classification_accepts_null_parent_index(self):
        tree = CTree(**{"api_key": "test-openai-compatible-key"})
        tree.conversation = [
            {"role": "user", "content": "What budget applies?"},
            {"role": "assistant", "content": "Use the shared LiteLLM budget."},
        ]
        tree._chatgpt_api = lambda *args, **kwargs: json.dumps({
            "reasoning": "New topic under current topic",
            "belongs_to_current": False,
            "new_topic_name": "Provider budget",
            "new_topic_parent_index": None,
        })

        result = tree._llm_classify_message_exchange(
            {"role": "user", "content": "What about limits?"},
            {"role": "assistant", "content": "Keep shared rate limits."},
            make_candidate_nodes(),
        )

        self.assertFalse(result["belongs_to_current"])
        self.assertEqual(result["new_topic_parent_index"], 1)

    def test_message_classification_accepts_null_parent_index(self):
        tree = CTree(**{"api_key": "test-openai-compatible-key"})
        tree.conversation = [
            {"role": "user", "content": "What budget applies?"},
            {"role": "assistant", "content": "Use the shared LiteLLM budget."},
        ]
        tree._chatgpt_api = lambda *args, **kwargs: json.dumps({
            "reasoning": "New topic under current topic",
            "belongs_to_current": False,
            "new_topic_name": "Provider budget",
            "new_topic_parent_index": None,
        })

        result = tree._llm_classify_message(
            {"role": "user", "content": "What about limits?"},
            make_candidate_nodes(),
        )

        self.assertFalse(result["belongs_to_current"])
        self.assertEqual(result["parent_index"], 1)
        self.assertEqual(result["new_topic_parent_index"], 1)


if __name__ == "__main__":
    unittest.main()
