"""Brightside Bikes support bot: answers customer questions from the FAQ pages in faq/."""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import medic_runtime as medic

load_dotenv()

FAQ_DIR = Path(__file__).parent / "faq"
MODEL = os.environ.get("CHAT_MODEL", "gpt-oss:120b")
TOP_K = 3              # FAQ sections given to the model per question
TEMPERATURE = 0.2

SYSTEM_PROMPT = """You are the support assistant for Brightside Bikes, an online bike shop.
Answer using the FAQ sections below only when they are relevant to the customer's question. Be brief.
If the FAQ doesn't cover the question, say you're not sure and suggest contacting support
at help@brightside.example."""

client = OpenAI()      # OPENAI_API_KEY and OPENAI_BASE_URL come from the environment

STOPWORDS = {"a", "an", "the", "is", "are", "do", "does", "i", "my", "you", "your", "to", "of", "on",
             "for", "in", "and", "or", "can", "how", "what", "when", "where", "who", "it", "if", "be"}


@medic.surface("bot._words")
def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9$]+", text.lower()) if w not in STOPWORDS}


def load_sections() -> list[str]:
    """Each '## question' heading of every FAQ page, with its answer."""
    sections = []
    for page in sorted(FAQ_DIR.glob("*.md")):
        title = page.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
        for block in page.read_text(encoding="utf-8").split("\n## ")[1:]:
            sections.append(f"[{title}] {block.strip()}")
    return sections


SECTIONS = load_sections()


@medic.surface("bot.retrieve")
def retrieve(question: str, k: int = medic.value("bot.top_k", TOP_K)) -> list[str]:
    """The k FAQ sections sharing the most words with the question."""
    q = _words(question)
    ranked = sorted(SECTIONS, key=lambda s: len(q & _words(s)), reverse=True)
    return ranked[:k]


@medic.surface("bot.build_messages")
def build_messages(question: str, sections: list[str]) -> list[dict]:
    faq = "\n\n".join(sections)
    return [{"role": "system", "content": f"{medic.value("bot.system_prompt", SYSTEM_PROMPT)}\n\nFAQ:\n{faq}"},
            {"role": "user", "content": question}]


@medic.surface("bot.answer")
def answer(question: str) -> str:
    sections = retrieve(question)
    reply = client.chat.completions.create(model=MODEL, temperature=medic.value("bot.temperature", TEMPERATURE),
                                           messages=build_messages(question, sections))
    return reply.choices[0].message["content"].strip()


if __name__ == "__main__":
    import sys
    print(answer(" ".join(sys.argv[1:]) or "How long do I have to return an item?"))
