import streamlit as st
import google.generativeai as genai
from groq import Groq
from supabase import create_client
import json

st.set_page_config(page_title="Qwen Mock Test Generator", layout="wide")

# 1. Initialize APIs from Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("⚙️ Adaptive Mock Test Engine (Powered by Qwen)")

# 2. Fetch User Memory (Grey Areas)
st.sidebar.header("🧠 Your Identified Weaknesses")
try:
    grey_data = supabase.table("topic_analytics").select("*").eq("is_grey_area", True).execute()
    grey_topics = [item['topic_name'] for item in grey_data.data[-5:]] if grey_data.data else []
    if grey_topics:
        for topic in grey_topics:
            st.sidebar.warning(f"⚠️ {topic}")
    else:
        st.sidebar.success("No weak areas yet. Generate a test to start learning!")
except Exception as e:
    st.sidebar.error("Database connecting...")

# 3. File Upload & Test Generation
uploaded_files = st.file_uploader("Upload PPTs, PDFs, and PYQs", accept_multiple_files=True)

if st.button("Generate Exam Paper") and uploaded_files:
    with st.spinner("Phase 1: Gemini is reading heavy documents..."):
        # Upload to Gemini File API
        gemini_files = []
        for file in uploaded_files:
            temp_path = f"/tmp/{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            gemini_files.append(genai.upload_file(path=temp_path))
        
        # Extract notes
        reader_model = genai.GenerativeModel("gemini-1.5-flash")
        condensed_notes = reader_model.generate_content([*gemini_files, "Extract all core engineering formulas, derivations, and concepts. Output a dense summary."]).text
        
    with st.spinner("Phase 2: Qwen is designing the rigorous math and derivations..."):
        groq_prompt = f"""
        You are an advanced engineering professor. Using these condensed notes, generate a rigorous mock test. 
        Focus heavily on these user weak areas: {grey_topics}.
        
        Include:
        - 2 multi-step numerical problems
        - 1 formal mathematical derivation
        - 3 conceptual design questions
        
        Include a hidden solution key at the end.
        
        NOTES: {condensed_notes}
        """
        
        # Call Qwen 2.5 32B on Groq for advanced math logic
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": groq_prompt}],
            model="qwen-2.5-32b",
            temperature=0.2, 
        )
        
        st.session_state["generated_test"] = chat_completion.choices[0].message.content
        st.success("Test Ready!")

# 4. Display Test & Grading Engine
if "generated_test" in st.session_state:
    st.markdown(st.session_state["generated_test"])
    
    st.subheader("📝 Submit Your Answers")
    user_answer = st.text_area("Type your derivations and numerical steps here:")
    
    if st.button("Evaluate Answers") and user_answer:
        with st.spinner("Qwen is strictly grading your logic..."):
            eval_prompt = f"""
            Grade this engineering submission. Be highly critical of mathematical steps.
            TEST & KEY: {st.session_state['generated_test']}
            STUDENT SUBMISSION: {user_answer}
            
            Return JSON in this format ONLY:
            {{
              "topic_name": "String",
              "score_out_of_10": float,
              "feedback": "String",
              "is_grey_area": boolean (True if score < 6.0)
            }}
            """
            
            # Using Qwen in JSON mode for structured grading
            eval_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": eval_prompt}],
                model="qwen-2.5-32b",
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            eval_data = json.loads(eval_completion.choices[0].message.content)
            st.json(eval_data)
            
            # Save weakness to Supabase
            supabase.table("topic_analytics").insert({
                "subject": "Core Subject",
                "topic_name": eval_data["topic_name"],
                "score": eval_data["score_out_of_10"],
                "feedback": eval_data["feedback"],
                "is_grey_area": eval_data["is_grey_area"]
            }).execute()
            
            st.success("Scores saved to memory!")
