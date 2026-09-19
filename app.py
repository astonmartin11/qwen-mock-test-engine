import streamlit as st

# Configure page at the root level before any UI is rendered
st.set_page_config(page_title="Advanced Exam Engine", layout="wide")

from ui.sidebar import render_sidebar
from ui.mock_test_tab import render_mock_test_engine
from ui.tutor_tab import render_ai_tutor

st.title("⚙️ Advanced Exam Engine & AI Tutor")

# 1. Render Sidebar to manage subjects and memory
active_subject, grey_topics = render_sidebar()

# 2. Block the main screen if no subject is selected
if not active_subject:
    st.warning("Please select or add a subject in the sidebar to start your session.")
    st.stop()

# 3. Setup Tabs
tab_exam, tab_tutor = st.tabs(["📝 Mock Test Engine", "🤖 Personal Tutor"])

# 4. Route to UI modules
with tab_exam:
    render_mock_test_engine(active_subject, grey_topics)

with tab_tutor:
    render_ai_tutor(active_subject, grey_topics)
