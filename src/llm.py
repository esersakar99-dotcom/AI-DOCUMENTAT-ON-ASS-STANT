import json
from abc import ABC, abstractmethod
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import ollama

SYSTEM_PROMPT = """You are a document assistant. Review context from every provided document
before answering. Answer only with information found in the provided CONTEXT. If the context
does not contain the answer, say so clearly and do not invent information. When documents
differ, distinguish them explicitly. For numerical questions, clearly distinguish the initial,
excluded, and final included counts. Cite every important claim as [filename, p.X]. Be concise."""


PROVIDERS = ("Ollama", "OpenAI", "Anthropic", "Gemini")
FREE_PROVIDERS = ("Ollama", "Gemini")
UI_PROVIDERS = ("Ollama", "Gemini", "OpenAI")
DEFAULT_MODELS = {"ollama": "llama3.2:3b", "openai": "gpt-4.1-mini",
                  "anthropic": "claude-3-5-haiku-latest", "gemini": "gemini-3.6-flash"}


def _user_prompt(question: str, context: str) -> str:
    return f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"


class LLM(ABC):
    @abstractmethod
    def answer(self, question: str, context: str) -> str:
        """Return a grounded answer for the supplied context."""


class OllamaLLM(LLM):
    def __init__(self, model: str = "llama3.2:3b", host: str | None = None):
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def answer(self, question: str, context: str) -> str:
        response = self.client.chat(model=self.model, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(question, context)},
        ], options={
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_batch": 128,
        }, keep_alive="2m")
        return response["message"]["content"]


class HTTPJSONLLM(LLM):
    def __init__(self, model: str, api_key: str, base_url: str):
        if not api_key:
            raise ValueError("An API key is required for this provider.")
        self.model, self.api_key, self.base_url = model, api_key, base_url.rstrip("/")

    def _post(self, url: str, payload: dict, headers: dict[str, str]) -> dict:
        request = Request(url, data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json", **headers}, method="POST")
        try:
            with urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode())
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            if exc.code == 429:
                raise RuntimeError("The provider's free quota or rate limit has been reached. "
                                   "Wait for the quota to reset or switch to Ollama.") from exc
            raise RuntimeError(f"Provider returned HTTP {exc.code}: {detail[:500]}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to the provider: {exc.reason}") from exc


class OpenAILLM(HTTPJSONLLM):
    def answer(self, question: str, context: str) -> str:
        data = self._post(f"{self.base_url}/chat/completions", {
            "model": self.model, "temperature": 0.1,
            "messages": [{"role": "developer", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": _user_prompt(question, context)}],
        }, {"Authorization": f"Bearer {self.api_key}"})
        return data["choices"][0]["message"]["content"]


class AnthropicLLM(HTTPJSONLLM):
    def answer(self, question: str, context: str) -> str:
        data = self._post(f"{self.base_url}/messages", {
            "model": self.model, "max_tokens": 1200, "temperature": 0.1, "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": _user_prompt(question, context)}],
        }, {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"})
        return "".join(block["text"] for block in data["content"] if block.get("type") == "text")


class GeminiLLM(HTTPJSONLLM):
    def answer(self, question: str, context: str) -> str:
        data = self._post(f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}", {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": _user_prompt(question, context)}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1200},
        }, {})
        return "".join(part.get("text", "") for part in data["candidates"][0]["content"]["parts"])


def create_llm(provider: str, model: str, api_key: str = "", host: str | None = None,
               base_url: str | None = None) -> LLM:
    name = provider.strip().lower()
    if name == "ollama":
        return OllamaLLM(model, host)
    classes = {"openai": (OpenAILLM, "https://api.openai.com/v1"),
               "anthropic": (AnthropicLLM, "https://api.anthropic.com/v1"),
               "gemini": (GeminiLLM, "https://generativelanguage.googleapis.com/v1beta")}
    if name not in classes:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    provider_class, default_url = classes[name]
    return provider_class(model, api_key, base_url or default_url)
