import streamlit as st
from supabase import create_client

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def get_subjects():
    try:
        data = supabase.table("subjects").select("name").execute()
        return [row["name"] for row in data.data]
    except:
        return []

def add_subject(subject_name):
    try:
        supabase.table("subjects").insert({"name": subject_name}).execute()
        return True
    except:
        return False

def delete_subject(subject_name):
    try:
        supabase.table("topic_analytics").delete().eq("subject", subject_name).execute()
        supabase.table("subjects").delete().eq("name", subject_name).execute()
        return True
    except:
        return False

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
