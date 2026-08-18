import ollama

SYSTEM_PROMPT = """Sen bir Türkçe doküman asistanısın. Yalnızca verilen BAĞLAM içindeki
bilgilerle cevap ver. Bağlamda cevap yoksa bunu açıkça söyle; bilgi uydurma.
Her önemli iddianın ardından [dosya, s.X] biçiminde kaynak göster. Kısa ve anlaşılır ol."""


class OllamaLLM:
    def __init__(self, model: str = "llama3.2:3b", host: str | None = None):
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def answer(self, question: str, context: str) -> str:
        response = self.client.chat(model=self.model, messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"BAĞLAM:\n{context}\n\nSORU:\n{question}"},
        ], options={
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_batch": 128,
        }, keep_alive="2m")
        return response["message"]["content"]
