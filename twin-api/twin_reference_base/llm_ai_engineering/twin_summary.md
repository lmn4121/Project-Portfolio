# Digital Twin — Resume Chatbot

## Contents
- [The Problem](#the-problem)
- [Project Overview](#project-overview)
- [System Components](#system-components)
- [Techniques](#techniques)
- [Results](#results)
- [How to Run](#how-to-run)
- [Repository Structure](#repository-structure)

## The Problem
Visitors (for example recruiters or collaborators) often want to ask about skills and experience listed on a resume, but a static PDF cannot answer follow-ups or pull project detail on demand.

This project builds a **chatbot digital twin of Landon Nguyen** that discusses background, skills, and experience from the resume, with retrieval over project write-ups for richer answers.

## Project Overview
**Goal:**
- Present a conversational interface that stays in character as Landon’s digital twin
- Ground answers in resume text plus a searchable knowledge base of project documents
- Capture visitor emails for follow-up and log questions the twin cannot answer

**Approach:**
1. Ingest markdown project notes into a Chroma vector store with LLM-assisted semantic chunking (`ingest.py`)
2. Define an OpenAI Agents SDK agent with tools for RAG, email capture, and unknown-question logging (`twin.py`)
3. Serve a Gradio chat UI with streaming replies (`app.py`)

## System Components

### `ingest.py` — Knowledge base build
- Loads `**/*.md` from `twin_reference_base/` via LangChain `DirectoryLoader` / `TextLoader`
- Uses a **custom semantic chunking** strategy: `gpt-4.1-nano` (via LiteLLM) returns structured chunks (`headline`, `summary`, exact `content`) with intended overlap
- Parallelizes chunking across documents with a multiprocessing pool
- Embeds chunks with OpenAI **`text-embedding-3-large`** into a persistent Chroma store (`twin_db`)

### `twin.py` — Agent digital twin
- OpenAI Agents SDK agent (`gpt-5.4-mini`) instructed to role-play as Landon’s twin for professional Q&A
- Resume text is loaded from `Nguyen_Landon_CV.pdf` into the system instructions
- **Tools:**
  - `retrieve_knowledge` — RAG over the Chroma store for project/skills context (required on user questions)
  - `record_email` — capture visitor contact for follow-up (Pushover notification path)
  - `record_unknown_question` — log questions that cannot be answered honestly
- Streaming chat via `Runner.run_streamed` and SQLite session memory (`memory.db`)

### `app.py` — Gradio UI
- Main runner and chat interface (dark-themed Gradio Blocks)
- Streams twin responses with a “Thinking” indicator; supports **New Chat** (clears session)
- Gradio UI work was heavily assisted by Cursor Agent

## Techniques
- **RAG** over a project/experience knowledge base
- **Semantic chunking** (LLM-structured chunks with headlines and summaries, not fixed-size splits alone)
- **Agent tooling** (retrieval + side-effect tools for leads and coverage gaps)
- **Streaming** agent responses into a Gradio chatbot
- **Session memory** via OpenAI Agents `SQLiteSession`

## Results
- End-to-end twin chatbot that answers resume- and project-oriented questions using RAG when needed
- Lead-capture and unknown-question tools so unanswered or off-resume gaps can be recorded instead of invented
- Interactive Gradio demo for local (and future hosted) use
- Prebuilt `twin_db/` Chroma store included so the twin can run without re-ingesting from scratch

## How to Run
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in a `.env` (at minimum OpenAI credentials; Pushover user/token for notification tools)
3. Ensure `Nguyen_Landon_CV.pdf`, `twin_reference_base/`, and `twin_db/` are present (as in this branch)
4. *(Optional)* Rebuild the vector store after editing reference docs:
   ```bash
   python ingest.py
   ```
5. Launch the UI:
   ```bash
   python app.py
   ```

## Repository Structure
- `app.py` — Gradio digital-twin chat UI
- `twin.py` — agent, tools, and streaming chat
- `ingest.py` — semantic chunking + Chroma ingest
- `requirements.txt` — pinned Python dependencies
- `Nguyen_Landon_CV.pdf` — resume loaded into twin instructions
- `twin_reference_base/` — markdown knowledge sources by topic (`capstone_project/`, `computer_vision/`, `general/`, `llm_ai_engineering/`, `other_projects/`)
  - includes `llm_ai_engineering/twin_summary.md` (copy of this README for the twin’s knowledge base)
- `twin_db/` — prebuilt Chroma persistence directory used by the twin (can be rebuilt with `ingest.py`)
- `memory.db` — chat session store created at runtime
