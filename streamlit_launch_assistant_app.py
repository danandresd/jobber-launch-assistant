"""
Jobber Recruiting Launch Assistant — Streamlit UI

Assembles a structured prompt from editable source inputs (instructions, brand
rules, outreach template, job description, intake notes).  The output is a
recruiter-ready prompt package that can be pasted into an LLM to generate the
full launch pack.
"""

from pathlib import Path
from textwrap import dedent

import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Jobber Launch Pack Generator",
    page_icon=":compass:",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

SOURCE_FILES = {
    "instructions":      "instructions.md",
    "brand_rules":       "employer_brand_rules.md",
    "outreach_template": "outreach_template.md",
    "jd":                "job_description.md",
    "intake":            "intake_notes.md",
}


def _read(filename: str) -> str:
    path = PROJECT_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _load_defaults() -> dict[str, str]:
    return {key: _read(fname) for key, fname in SOURCE_FILES.items()}


# ---------------------------------------------------------------------------
# Prompt builder (mirrors launch_pack_generator.py)
# ---------------------------------------------------------------------------

def build_prompt(sources: dict[str, str]) -> str:
    return dedent(f"""\
You are **Jobber Recruiting Launch Assistant**.

Your job is to produce a polished, role-specific **Launch Pack** that a recruiter can immediately paste into docs, an ATS, or an interview plan. Follow every instruction below precisely.

---

## SYSTEM INSTRUCTIONS

{sources["instructions"]}

---

## EMPLOYER BRAND RULES

{sources["brand_rules"]}

---

## OUTREACH EMAIL TEMPLATE (required structural baseline)

{sources["outreach_template"]}

---

## JOB DESCRIPTION

{sources["jd"]}

---

## INTAKE NOTES (recruiter & hiring manager context)

{sources["intake"]}

---

## YOUR TASK

Using **all** of the context above, generate the full launch pack in clean, recruiter-ready markdown with the sections below.

### Output Structure

Produce each of these sections with clear markdown headings:

**1. Role Summary**
- 8-10 concise bullets covering: mission, team context, first-90-day outcomes, key skills, key traits, non-negotiables, nice-to-haves, seniority level, and hiring manager expectations.
- Use the intake notes to sharpen level, scope, and what the hiring manager actually cares about.
- If important details are missing, note them under section 6 -- do not invent them.

**2. Application Questions**

*Multiple Choice (3-5 questions)*
- Each question: 4 options (A-D), exactly ONE correct answer clearly labeled.
- Balance answer lengths so the correct answer is not always the longest.
- Difficulty: moderately challenging -- filter for role readiness, not surface knowledge.
- Assess: technical fundamentals relevant to this role, practical judgment in realistic scenarios, and core non-negotiables from the JD.
- For each question include: the question, answer options, correct answer, what it assesses, and why the correct answer is correct.

*Short Written (1-2 questions)*
- Designed to reveal depth, ownership, and hands-on experience relevant to this specific role.
- Instruct candidates to limit responses to 4-5 sentences.
- For each question include: the question, what it assesses, strong-answer signals, and red flags.

**3. Interview Questions (Structured & Evidence-Based)**
- 4-6 competency areas directly relevant to this role.
- For each competency: 2 primary behavioral questions requiring a real past example, plus 1 follow-up probe to push past surface-level responses.
- Questions must demand concrete context, actions, decisions, constraints, and measurable results.
- Include a scoring rubric per competency (1 = vague, 2 = solid but limited ownership, 3 = strong with outcomes, 4 = exceptional depth and impact).
- Include at least one role-relevant case exercise or work sample prompt.
- If a question can be answered credibly without a real example, rewrite it.
- Use the intake interview questions as a reference, but improve and expand them -- don't just copy them.

**4. Role Sales Pitch**

*A) Internal Pitch (for recruiters & hiring team)*
- 6-8 outcome-oriented bullet points: why this role exists now, the problems it solves, what success looks like in 6-12 months, cross-functional impact, and the level of ownership expected.
- Ground every bullet in the JD and intake -- avoid restating the JD verbatim.

*B) Candidate Pitch (for TA interviews, 120-180 words)*
- Tone: confident, human, specific, energetic -- aligned to Jobber brand voice.
- Must include: Jobber's mission in context of this role, the team and how it contributes, real-world impact, what kind of person thrives here, and growth opportunities.
- Must NOT sound like it could apply to any analytics role at any company. Make it unmistakably about this role at Jobber.
- Do not invent compensation, benefits, or policies.

**5. Outreach Email Sequence (3 emails)**
- Follow the outreach template structure exactly -- do not invent a new format.
- Customize content to reflect this specific role, team, responsibilities, and impact.
- Email 1: clear hook + concise role pitch + why Jobber + why this role + CTA with [Calendar Link].
- Email 2: one new angle (team context, problem space, growth, or visibility) + [Calendar Link].
- Email 3: polite close-the-loop + short reminder of scope/impact + [Calendar Link].
- Maintain placeholders: [Candidate Name], [Calendar Link], [Recruiter Name], [Hiring Manager].
- Tone: conversational, human, Jobber-branded. No false familiarity.
- Do not include compensation details.

**6. Open Questions / Missing Info**
- Flag anything missing from the JD or intake that would materially improve the launch pack.
- Include specific questions, not vague placeholders.

---

## QUALITY RULES (apply everywhere)

- Make every section specific to **this role** -- if it could apply generically to another role, rewrite it.
- Use the intake notes to sharpen scope, expectations, and selling points. Where JD and intake conflict, prefer intake for recruiter-facing nuance and JD for formal role expectations.
- Do not invent missing details -- use bracketed placeholders like [TBD] or [Confirm with HM].
- Keep output structured, skimmable, and recruiter-friendly (headings, bullets, numbered lists).
- Use inclusive, job-relevant language. Avoid proxies for protected classes.
- Avoid jargon, corporate speak, and generic platitudes.
- Do not invent or embellish compensation, benefits, or policies beyond what the intake provides.
- Return the full launch pack in clean markdown.""")


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "generated" not in st.session_state:
    st.session_state.generated = False
if "output_md" not in st.session_state:
    st.session_state.output_md = ""
if "defaults_loaded" not in st.session_state:
    st.session_state.defaults_loaded = False

defaults = _load_defaults()

if not st.session_state.defaults_loaded:
    for key in defaults:
        st.session_state[f"src_{key}"] = defaults[key]
    st.session_state.defaults_loaded = True


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='margin-bottom:0'>Jobber Launch Pack Generator</h1>",
    unsafe_allow_html=True,
)
st.caption(
    "Assemble a structured prompt from your source files, then paste into an LLM to generate the full launch pack."
)
st.divider()

input_col, output_col = st.columns([1, 1.2], gap="large")

# ---- LEFT: Inputs --------------------------------------------------------

with input_col:
    st.subheader("Source Inputs")

    tab_jd, tab_intake, tab_instructions, tab_brand, tab_outreach = st.tabs([
        "Job Description",
        "Intake Notes",
        "Instructions",
        "Brand Rules",
        "Outreach Template",
    ])

    with tab_jd:
        st.text_area(
            "Job description",
            key="src_jd",
            height=400,
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
        )

    with tab_intake:
        st.text_area(
            "Intake / kickoff notes",
            key="src_intake",
            height=400,
            placeholder="Paste recruiter and hiring manager notes here...",
            label_visibility="collapsed",
        )

    with tab_instructions:
        st.text_area(
            "System instructions",
            key="src_instructions",
            height=400,
            label_visibility="collapsed",
        )

    with tab_brand:
        st.text_area(
            "Employer brand rules",
            key="src_brand_rules",
            height=400,
            label_visibility="collapsed",
        )

    with tab_outreach:
        st.text_area(
            "Outreach email template",
            key="src_outreach_template",
            height=400,
            label_visibility="collapsed",
        )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        generate = st.button("Generate prompt package", type="primary", use_container_width=True)
    with btn_col2:
        reload = st.button("Reload files from disk", use_container_width=True)

    if reload:
        fresh = _load_defaults()
        for key in fresh:
            st.session_state[f"src_{key}"] = fresh[key]
        st.session_state.generated = False
        st.session_state.output_md = ""
        st.rerun()

    if generate:
        sources = {key: st.session_state.get(f"src_{key}", "") for key in defaults}
        st.session_state.output_md = build_prompt(sources)
        st.session_state.generated = True

# ---- RIGHT: Output -------------------------------------------------------

with output_col:
    st.subheader("Prompt Package")

    if not st.session_state.generated:
        st.info(
            "Edit the source inputs on the left (your files are pre-loaded), "
            "then click **Generate prompt package**."
        )
    else:
        preview_tab, raw_tab = st.tabs(["Preview", "Raw Markdown"])

        with preview_tab:
            st.markdown(st.session_state.output_md)

        with raw_tab:
            st.code(st.session_state.output_md, language="markdown")

        st.divider()

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="Download as .md",
                data=st.session_state.output_md,
                file_name="launch_pack_prompt.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl_col2:
            save = st.button("Save to output.md", use_container_width=True)
            if save:
                (PROJECT_DIR / "output.md").write_text(
                    st.session_state.output_md, encoding="utf-8"
                )
                st.success("Saved to output.md")

# ---- Footer ---------------------------------------------------------------

st.divider()
st.caption(
    "**How to use:** Generate the prompt package here, then paste it into "
    "Cursor Chat (or any LLM) and ask it to produce the full launch pack. "
    "The output will be a recruiter-ready markdown document with all 6 sections."
)
