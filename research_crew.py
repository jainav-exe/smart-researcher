"""Shared Smart Researcher crew logic for CLI and web UI."""

from __future__ import annotations

# Must run before CrewAI/Chroma imports on Streamlit Cloud.
import sys

if sys.platform != "win32":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import os
from textwrap import dedent
import certifi
from dotenv import load_dotenv

from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import SerperDevTool

REQUIRED_ENV_VARS = ("GEMINI_API_KEY", "SERPER_API_KEY")
DEFAULT_TOPIC = "Latest breakthroughs in local LLMs this week"


def bootstrap() -> None:
    """Load env vars and fix SSL on Windows before HTTP clients initialize."""
    load_dotenv()
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")


def missing_env_vars() -> list[str]:
    """Return names of required environment variables that are not set."""
    bootstrap()
    return [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]


def build_llm() -> LLM:
    return LLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.7,
        api_key=os.environ["GEMINI_API_KEY"],
    )


def run_research(topic: str, *, verbose: bool = False) -> str:
    """Run the two-agent research crew and return the Markdown report."""
    missing = missing_env_vars()
    if missing:
        raise RuntimeError(
            "Missing API keys: "
            + ", ".join(missing)
            + ". Set them in .env locally or Streamlit secrets when deployed."
        )

    llm = build_llm()
    search_tool = SerperDevTool()

    researcher = Agent(
        role="Senior Research Analyst",
        goal=(
            "Find accurate, up-to-date information on the assigned topic "
            "and compile a concise set of verified facts."
        ),
        backstory=dedent(
            """
            You are a meticulous research analyst with a talent for cutting
            through hype and noise. You use web search to gather primary sources,
            cross-check claims, and distill findings into clear, factual bullet
            points with source context where possible.
            """
        ).strip(),
        tools=[search_tool],
        llm=llm,
        verbose=verbose,
    )

    writer = Agent(
        role="Technical Report Writer",
        goal=(
            "Transform raw research notes into a polished, professional "
            "Markdown report that is easy to scan and act on."
        ),
        backstory=dedent(
            """
            You are an award-winning technical writer who excels at structure,
            clarity, and readability. You turn dense research into reports with
            compelling headings, tight bullet points, and a logical narrative —
            never fluff, always substance.
            """
        ).strip(),
        llm=llm,
        verbose=verbose,
    )

    research_task = Task(
        description=dedent(
            f"""
            Research the following topic thoroughly using web search:

            TOPIC: {topic}

            Your job:
            1. Run multiple targeted searches to cover key subtopics and recent developments.
            2. Filter out noise, duplicates, and low-quality sources.
            3. Compile a structured set of raw facts: key findings, names, dates,
               metrics, and short source notes.

            Do NOT write the final report — deliver research notes only.
            """
        ).strip(),
        expected_output=dedent(
            """
            A structured research brief containing:
            - 8–15 bullet points of verified facts
            - Brief source attribution per fact where available
            - A short "Key Themes" section (3–5 themes)
            - A "Gaps / Open Questions" section if information is incomplete
            """
        ).strip(),
        agent=researcher,
    )

    writing_task = Task(
        description=dedent(
            f"""
            Using the research brief from the previous task, write a professional
            Markdown report on:

            TOPIC: {topic}

            Requirements:
            - Start with a one-paragraph executive summary
            - Use clear H2/H3 headings
            - Use bullet points for scannable detail
            - Include a "Sources & References" section at the end
            - Keep tone professional, concise, and informative
            """
        ).strip(),
        expected_output=dedent(
            """
            A complete Markdown report with:
            - Title (H1)
            - Executive Summary
            - Main sections with headings and bullet points
            - Conclusion or "What to Watch Next"
            - Sources & References section
            """
        ).strip(),
        agent=writer,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=verbose,
    )

    result = crew.kickoff()
    return result.raw
