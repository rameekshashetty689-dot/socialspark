"""SocialSpark – Social Media Content Planner (Streamlit + Gemini API)."""
import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from services.calendar_service import build_calendar, calendar_to_csv  # noqa: E402
from services.gemini_service import generate_post_ideas  # noqa: E402

PLATFORMS = ["Instagram", "Facebook", "LinkedIn", "X (Twitter)", "YouTube", "TikTok"]
TONES = ["Professional", "Friendly", "Witty", "Inspirational", "Bold", "Educational"]

st.set_page_config(page_title="SocialSpark", page_icon="✨", layout="wide")

# ---------- Session state ----------
st.session_state.setdefault("ideas", [])
st.session_state.setdefault("calendar", None)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("✨ SocialSpark")
    st.caption("Social Media Content Planner")
    api_key = st.text_input(
        "Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Get a free key at https://aistudio.google.com/apikey",
    )
    st.divider()
    st.markdown(
        "**Workflow**\n\n"
        "1. Enter campaign objective\n"
        "2. Generate post ideas\n"
        "3. Create content calendar\n"
        "4. Edit before publishing"
    )

st.title("Social Media Content Planner")

# ---------- Step 1: Campaign objective ----------
st.header("1. Campaign objective")
with st.form("campaign_form"):
    objective = st.text_area(
        "What do you want to achieve?",
        placeholder="e.g. Launch our new eco-friendly water bottle and get 500 pre-orders",
    )
    col1, col2 = st.columns(2)
    brand = col1.text_input("Brand / business", placeholder="e.g. GreenSip")
    audience = col2.text_input("Target audience", placeholder="e.g. college students, 18-25")

    col3, col4 = st.columns(2)
    platforms = col3.multiselect("Platforms", PLATFORMS, default=["Instagram", "LinkedIn"])
    tone = col4.selectbox("Tone of voice", TONES)

    col5, col6 = st.columns(2)
    num_ideas = col5.slider("Number of post ideas", 3, 20, 8)
    posts_per_week = col6.slider("Posts per week", 1, 7, 3)

    submitted = st.form_submit_button("Generate post ideas", type="primary")

if submitted:
    if not objective.strip():
        st.warning("Please enter a campaign objective.")
    elif not platforms:
        st.warning("Select at least one platform.")
    else:
        with st.spinner("Gemini is brainstorming post ideas..."):
            try:
                st.session_state.ideas = generate_post_ideas(
                    api_key, objective, brand, audience, platforms, tone, num_ideas
                )
                st.session_state.calendar = None
                st.session_state.posts_per_week = posts_per_week
            except Exception as e:
                st.error(f"Could not generate ideas: {e}")

# ---------- Step 2: Post ideas ----------
if st.session_state.ideas:
    st.header("2. Post ideas")
    for i, idea in enumerate(st.session_state.ideas, start=1):
        with st.expander(f"{i}. {idea['title']}  ·  {idea['platform']}  ·  {idea['content_type']}"):
            st.write(idea["caption"])
            st.caption(idea["hashtags"])

    st.header("3. Content calendar")
    start = st.date_input("Start date", value=date.today())
    if st.button("Create content calendar", type="primary"):
        st.session_state.calendar = build_calendar(
            st.session_state.ideas,
            start,
            st.session_state.get("posts_per_week", 3),
        )

# ---------- Step 4: Edit calendar ----------
if st.session_state.calendar is not None:
    st.header("4. Edit before publishing")
    st.caption("Click any cell to edit. Change dates, captions, platforms, or status.")
    edited = st.data_editor(
        st.session_state.calendar,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "Platform": st.column_config.SelectboxColumn("Platform", options=PLATFORMS),
            "Status": st.column_config.SelectboxColumn(
                "Status", options=["Draft", "Approved", "Published"]
            ),
            "Caption": st.column_config.TextColumn("Caption", width="large"),
        },
        key="calendar_editor",
    )
    st.session_state.calendar = edited

    st.download_button(
        "⬇️ Download calendar (CSV)",
        data=calendar_to_csv(edited),
        file_name="socialspark_content_calendar.csv",
        mime="text/csv",
    )
