import streamlit as st
from supabase import create_client

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def get_subjects():
    try:
        data = supabase.table("topic_analytics").select("subject").execute()
        return list(set([row["subject"] for row in data.data]))
    except:
        return []

def get_grey_areas(subject):
    try:
        data = supabase.table("topic_analytics").select("*").eq("subject", subject).eq("is_grey_area", True).execute()
        return [item['topic_name'] for item in data.data[-5:]] if data.data else []
    except:
        return []

def save_grading_result(subject, topic, score, feedback, is_grey):
    supabase.table("topic_analytics").insert({
        "subject": subject,
        "topic_name": topic,
        "score": score,
        "feedback": feedback,
        "is_grey_area": is_grey
    }).execute()
