import unittest
from unittest.mock import patch

from src.llm import AnthropicLLM, GeminiLLM, OpenAILLM, OllamaLLM, create_llm


class LLMFactoryTests(unittest.TestCase):
    def test_creates_ollama_provider_without_api_key(self):
        with patch("src.llm.ollama.Client"):
            self.assertIsInstance(create_llm("Ollama", "test"), OllamaLLM)

    def test_creates_hosted_providers(self):
        self.assertIsInstance(create_llm("OpenAI", "test", "key"), OpenAILLM)
        self.assertIsInstance(create_llm("Anthropic", "test", "key"), AnthropicLLM)
        self.assertIsInstance(create_llm("Gemini", "test", "key"), GeminiLLM)

    def test_hosted_provider_requires_api_key(self):
        with self.assertRaisesRegex(ValueError, "API key"):
            create_llm("OpenAI", "test")

    def test_rejects_unknown_provider(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            create_llm("unknown", "test")


if __name__ == "__main__":
    unittest.main()
