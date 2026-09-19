import streamlit as st
from core.memory_db import get_subjects, get_grey_areas, add_subject, delete_subject

def render_sidebar():
    st.sidebar.header("📚 Your Subjects")
    existing_subjects = get_subjects()
    
    new_subject = st.sidebar.text_input("Add a New Subject:")
    if st.sidebar.button("Add Subject") and new_subject:
        if new_subject not in existing_subjects:
            if add_subject(new_subject):
                st.sidebar.success(f"Added {new_subject}!")
                st.rerun()
            else:
                st.sidebar.error("Failed to add subject.")

    active_subject = st.sidebar.selectbox("Active Workspace:", [""] + existing_subjects)
    grey_topics = []
    
    if active_subject:
        st.sidebar.header(f"🧠 Weaknesses: {active_subject}")
        grey_topics = get_grey_areas(active_subject)
        
        if grey_topics:
            for topic in grey_topics:
                st.sidebar.warning(f"⚠️ {topic}")
        else:
            st.sidebar.success("No weak areas yet in this subject!")
            
        st.sidebar.divider()
        if st.sidebar.button(f"🗑️ Delete '{active_subject}'"):
            delete_subject(active_subject)
            chat_key = f"chat_messages_{active_subject}"
            if chat_key in st.session_state:
                del st.session_state[chat_key]
            st.rerun()
            
    return active_subject, grey_topics
