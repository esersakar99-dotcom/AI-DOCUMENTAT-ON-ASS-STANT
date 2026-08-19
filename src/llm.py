import ollama

SYSTEM_PROMPT = """You are a document assistant. Answer only with information found in
the provided CONTEXT. If the context does not contain the answer, say so clearly and do
not invent information. Cite every important claim as [filename, p.X]. Be concise."""


class OllamaLLM:
    def __init__(self, model: str = "llama3.2:3b", host: str | None = None):
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def answer(self, question: str, context: str) -> str:
        response = self.client.chat(model=self.model, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"},
        ], options={
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_batch": 128,
        }, keep_alive="2m")
        return response["message"]["content"]
