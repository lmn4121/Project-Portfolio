"""Landon Nguyen digital twin — agent + RAG (production API core).

Gradio UI lives on the Digital-Twin branch for local demos only.
This module is consumed by api.py (FastAPI + SSE).
"""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock
from typing import AsyncIterator
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, SQLiteSession, function_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pypdf import PdfReader

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"
MODEL_NAME = os.getenv("TWIN_MODEL", "gpt-5.4-mini")

DB_NAME = str(BASE_DIR / "twin_db")
MEMORY_DB = str(BASE_DIR / "memory.db")
RESUME_PATH = BASE_DIR / "Nguyen_Landon_CV.pdf"

embedding_model = "text-embedding-3-large"
embeddings = OpenAIEmbeddings(model=embedding_model)
vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)
retriever = vectorstore.as_retriever()

# Per-visitor session store (replaces shared SQLiteSession("12345"))
_sessions: dict[str, SQLiteSession] = {}
_sessions_lock = Lock()


def get_session(session_id: str) -> SQLiteSession:
    """Return an isolated SQLite session for this visitor id."""
    sid = (session_id or "").strip() or "anonymous"
    with _sessions_lock:
        if sid not in _sessions:
            _sessions[sid] = SQLiteSession(sid, MEMORY_DB)
        return _sessions[sid]


def push(message: str) -> None:
    """Send a Pushover notification when credentials are configured."""
    print(f"Push: {message}")
    if not pushover_user or not pushover_token:
        print("Pushover skipped: PUSHOVER_USER / PUSHOVER_TOKEN not set")
        return
    payload = urlencode(
        {"user": pushover_user, "token": pushover_token, "message": message}
    ).encode("utf-8")
    req = Request(pushover_url, data=payload, method="POST")
    try:
        with urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                print(f"Pushover HTTP {resp.status}")
    except Exception as exc:  # noqa: BLE001 — notify path must not break tools
        print(f"Pushover failed: {exc}")


async def clear_history(session_id: str) -> str:
    session = get_session(session_id)
    await session.clear_session()
    return "History cleared"


@function_tool
def record_email(email: str, name: str = "Unknown", notes: str = "No notes") -> str:
    """Record the user's email address and name if they provided it
    Args:
        email: str - The user's email address
        name: str - The user's name
        notes: str - Any additional info about the conversation that's worth recording to give context
    """
    push(f"{name} would like to get in touch. Email: {email}. Notes: {notes}")
    return f"Email recorded: {email}"


@function_tool
def record_unknown_question(question: str) -> str:
    """Record the user's question if it couldn't be answered"""
    push(f"Could not answer: {question}")
    return f"Question recorded: {question}"


@function_tool
def retrieve_knowledge(query: str) -> str:
    """
    Retrieve additional information about my projects, skills and experience
    to better answer the user's question.
    Args:
        query: str - A short, concise, and direct question about my projects, skills or experience.
    """
    print(f"Answering question: {query}")
    docs = retriever.invoke(query)
    context = "\n\n".join([d.page_content for d in docs])
    return context


reader = PdfReader(str(RESUME_PATH))
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

instructions = f"""
# Your role
You are a digital twin of Landon Nguyen, a prospective data scientist and AI
engineer student at the University of Texas at Arlington. Your job is to interact
with visitors to the website and answer questions about your background, skills,
and experience that are listed in your resume.

# Context
Here is your resume:
{resume}

Another project that is not listed in your resume:
- You completed a kaggle project for predicting metastatic TNBC

# Rules
Engage with the user. Be professional and engaging, as if talking to a
potential employer. Only answer questions related to your background, skills,
and experience. If the user asks about something unrelated, then steer the
conversation back to professional topics.

Whenever the user asks a question, you must use your tool to retrieve information
that might be relevant to the question.

Always stay in character as the digital twin of the person you are representing.

If the user would like to get in touch, then ask for their email, and use your tool
to record their email for follow-up.

IMPORTANT:
If you don't know the answer, use your tool to record the question,
and then tell the user that you don't know. Never make up an answer.
"""

tools = [record_email, record_unknown_question, retrieve_knowledge]
twin = Agent(
    name="Landon Nguyen's digital twin",
    instructions=instructions,
    model=MODEL_NAME,
    tools=tools,
)


async def chat(message: str, session_id: str) -> AsyncIterator[str]:
    """Yield text deltas for the given visitor session."""
    session = get_session(session_id)
    result = Runner.run_streamed(twin, message, session=session)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            if event.data.delta:
                yield event.data.delta
