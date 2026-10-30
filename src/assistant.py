import os

from google import genai

from src.vector_store import VectorStoreManager

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""


class OptiBotAssistant:
    def __init__(self, vector_store: VectorStoreManager = None, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.vector_store = vector_store or VectorStoreManager(api_key=self.api_key)

    def ask(self, question: str) -> str:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured.")
        matches = self.vector_store.query(question, top_k=3)

        context_blocks = []
        citations = []
        for m in matches:
            url = m["metadata"].get("url")
            title = m["metadata"].get("title")
            context_blocks.append(f"Title: {title}\nURL: {url}\nContent:\n{m['text']}")
            if url and url not in citations:
                citations.append(url)

        context_str = "\n\n---\n\n".join(context_blocks)

        prompt = f"""Use the following documentation to answer the question.

DOCUMENTS:
{context_str}

QUESTION:
{question}

Provide the answer following the rules in your system instructions strictly.
Always include the Article URL lines at the bottom."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt, config={"system_instruction": SYSTEM_PROMPT}
        )
        return response.text
