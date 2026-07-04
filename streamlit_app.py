import streamlit as st

from research_crew import missing_env_vars, run_research

st.set_page_config(
    page_title="Smart Researcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            background: linear-gradient(90deg, #818cf8, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sub-header {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }
        .agent-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
        }
        .agent-card h4 {
            margin: 0 0 0.35rem 0;
            color: #e2e8f0;
        }
        .agent-card p {
            margin: 0;
            color: #94a3b8;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_secrets_into_env() -> None:
    """Map Streamlit Cloud secrets into os.environ for CrewAI."""
    import os

    for key in ("GEMINI_API_KEY", "SERPER_API_KEY"):
        if not os.environ.get(key):
            try:
                value = st.secrets.get(key)
                if value:
                    os.environ[key] = value
            except (FileNotFoundError, KeyError, AttributeError):
                pass


load_secrets_into_env()

if "topic" not in st.session_state:
    st.session_state.topic = ""

with st.sidebar:
    st.markdown("### How it works")
    st.markdown(
        """
        **Smart Researcher** is a two-agent AI crew:

        1. **Researcher** searches the web (Serper)
        2. **Writer** turns facts into a Markdown report

        Powered by **Gemini 2.5 Flash** (free tier).
        """
    )
    st.divider()
    st.markdown("#### Agents")
    st.markdown(
        """
        <div class="agent-card">
            <h4>🔎 Research Analyst</h4>
            <p>Searches the web, filters noise, compiles verified facts.</p>
        </div>
        <div class="agent-card">
            <h4>✍️ Report Writer</h4>
            <p>Structures findings into a professional Markdown report.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Built with CrewAI · Gemini · Serper")

st.markdown('<p class="main-header">Smart Researcher</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Enter any topic — two AI agents will research it and write a report for you.</p>',
    unsafe_allow_html=True,
)

missing = missing_env_vars()
if missing:
    st.error(
        "API keys missing: **"
        + "**, **".join(missing)
        + "**. Add them to `.env` locally or Streamlit **Secrets** when deployed."
    )
    st.stop()

col_input, col_action = st.columns([4, 1])

with col_input:
    st.session_state.topic = st.text_input(
        "Research topic",
        value=st.session_state.topic,
        placeholder="e.g. Latest breakthroughs in local LLMs this week",
        label_visibility="collapsed",
    )

with col_action:
    run_clicked = st.button("Research", type="primary", use_container_width=True)

example_topics = [
    "Latest breakthroughs in local LLMs this week",
    "Top AI agent frameworks in 2026",
    "Recent advances in renewable energy storage",
]
st.caption("Try an example:")
example_cols = st.columns(len(example_topics))
for col, example in zip(example_cols, example_topics):
    if col.button(example, use_container_width=True, key=f"ex_{example[:20]}"):
        st.session_state.topic = example
        st.rerun()

if run_clicked:
    topic = st.session_state.topic.strip()
    if not topic:
        st.warning("Please enter a research topic.")
    else:
        with st.status("Running research crew…", expanded=True) as status:
            st.write("Agent 1 — Research Analyst is searching the web…")
            try:
                report = run_research(topic, verbose=False)
            except Exception as exc:
                status.update(label="Research failed", state="error")
                st.error(f"Something went wrong: {exc}")
                st.stop()

            st.write("Agent 2 — Report Writer is drafting the report…")
            status.update(label="Report ready!", state="complete")

        st.markdown("---")
        st.markdown("### Your Report")
        st.download_button(
            label="Download Markdown",
            data=report,
            file_name="research_report.md",
            mime="text/markdown",
        )
        st.markdown(report)

else:
    st.info("Enter a topic above and click **Research** to generate a report.")
