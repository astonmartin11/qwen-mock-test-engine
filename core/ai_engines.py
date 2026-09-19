import google.generativeai as genai
from groq import Groq
import streamlit as st
import json

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extract_course_context(files_list):
    gemini_files = []
    for file in files_list:
        temp_path = f"/tmp/{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        gemini_files.append(genai.upload_file(path=temp_path))
    
    reader_model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "Extract all core engineering formulas, derivations, and concepts. Output a dense academic summary."
    return reader_model.generate_content([*gemini_files, prompt]).text

def generate_mock_test(subject, condensed_notes, grey_areas, custom_steering, num_num, num_deriv, num_theory):
    prompt = f"""
    You are an advanced engineering professor. Using these condensed notes for {subject}, generate a rigorous mock test. 
    Target these user weak areas: {grey_areas}.
    
    CRITICAL OVERRIDE INSTRUCTIONS FROM THE EXAMINER:
    {custom_steering if custom_steering else "None provided. Follow standard distribution."}
    
    EXAM STRUCTURE:
    Include EXACTLY:
    - {num_num} numerical problems requiring multi-step calculations.
    - {num_deriv} formal mathematical derivations.
    - {num_theory} conceptual/theory questions.
    
    Include a hidden solution key at the end.
    NOTES: {condensed_notes}
    """
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="qwen-2.5-32b",
        temperature=0.2, 
    )
    return completion.choices[0].message.content

def transcribe_and_grade(test_content, typed_text, uploaded_file):
    transcribed_text = typed_text if typed_text else ""
    
    if uploaded_file:
        temp_ans_path = f"/tmp/submission_file"
        with open(temp_ans_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        uploaded_ans = genai.upload_file(path=temp_ans_path)
        
        vision_model = genai.GenerativeModel("gemini-1.5-flash")
        transcribed_text += "\n" + vision_model.generate_content([
            uploaded_ans, 
            "Transcribe this engineering answer sheet perfectly. Include all mathematical steps."
        ]).text

    eval_prompt = f"""
    Grade this engineering submission. Be highly critical of mathematical steps.
    TEST & KEY: {test_content}
    STUDENT SUBMISSION: {transcribed_text}
    
    Return JSON in this format ONLY:
    {{
      "topic_name": "String",
      "score_out_of_10": float,
      "feedback": "String",
      "is_grey_area": boolean
    }}
    """
    eval_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": eval_prompt}],
        model="qwen-2.5-32b",
        response_format={"type": "json_object"},
        temperature=0.0
    )
    return json.loads(eval_completion.choices[0].message.content)

def chat_with_tutor_model(subject, grey_areas, messages_history):
    system_prompt = f"""
    You are a personalized academic tutor for a postgraduate engineering student. 
    Current Subject: {subject}
    The student's known weak topics (Grey Areas) in this subject are: {grey_areas}.
    
    INSTRUCTIONS:
    - Proactively connect concepts to their known weak areas to help them improve.
    - Keep answers concise, highly technical, and mathematical where appropriate.
    """
    
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages_history:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    completion = groq_client.chat.completions.create(
        messages=api_messages,
        model="qwen-2.5-32b",
        temperature=0.5,
    )
    return completion.choices[0].message.content
