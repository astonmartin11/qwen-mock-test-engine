import streamlit as st
from core.ai_engines import extract_course_context, generate_mock_test, transcribe_and_grade
from core.pdf_utils import generate_pdf
from core.memory_db import save_grading_result

def render_mock_test_engine(active_subject, grey_topics):
    st.subheader("1. Upload Study Materials")
    col1, col2, col3 = st.columns(3)
    with col1:
        syllabus = st.file_uploader("📑 Syllabus", type=['pdf'])
    with col2:
        notes = st.file_uploader("📖 Slides & Notes", accept_multiple_files=True)
    with col3:
        pyqs = st.file_uploader("📝 PYQs", accept_multiple_files=True)

    st.subheader("2. Exam Configuration")
    cfg_col1, cfg_col2, cfg_col3 = st.columns(3)
    num_num = cfg_col1.number_input("Numericals", min_value=0, max_value=10, value=2)
    num_deriv = cfg_col2.number_input("Derivations", min_value=0, max_value=10, value=1)
    num_theory = cfg_col3.number_input("Conceptual/Theory", min_value=0, max_value=20, value=3)

    custom_steering = st.text_area(
        "Direct the AI (e.g., 'Make a numerical on back propagation instead of forward'):"
    )

    test_key = f"generated_test_{active_subject}"

    if st.button("Generate Exam Paper"):
        if not notes:
            st.error("Please upload at least your class notes.")
            return
            
        with st.spinner("Phase 1: Digesting Syllabus, Notes, and PYQs..."):
            all_uploads = (notes or []) + (pyqs or [])
            if syllabus: all_uploads.append(syllabus)
            condensed_notes = extract_course_context(all_uploads)
            
        with st.spinner(f"Phase 2: Generating {num_num} numericals, {num_deriv} derivations, and {num_theory} theory questions..."):
            st.session_state[test_key] = generate_mock_test(
                active_subject, condensed_notes, grey_topics, custom_steering, num_num, num_deriv, num_theory
            )
            st.success("Test Ready!")

    if test_key in st.session_state:
        st.divider()
        st.markdown(st.session_state[test_key])
        
        pdf_bytes = generate_pdf(st.session_state[test_key])
        st.download_button(
            label="📥 Download Test as PDF",
            data=pdf_bytes,
            file_name=f"{active_subject}_Mock_Test.pdf",
            mime="application/pdf"
        )
        
        st.divider()
        st.subheader("3. Submit Your Answers")
        
        user_text = st.text_area("Type text answer (optional):")
        camera_image = st.camera_input("Take a photo of your notebook:")
        answer_file = st.file_uploader("Upload Scanned PDF or Image Answer Sheet:", type=["pdf", "png", "jpg", "jpeg"])
        
        if st.button("Evaluate Submission"):
            with st.spinner("Analyzing handwritten math and grading..."):
                active_file = camera_image if camera_image else answer_file
                eval_data = transcribe_and_grade(st.session_state[test_key], user_text, active_file)
                st.json(eval_data)
                
                save_grading_result(
                    active_subject, 
                    eval_data["topic_name"], 
                    eval_data["score_out_of_10"], 
                    eval_data["feedback"], 
                    eval_data["is_grey_area"]
                )
                st.success("Scores saved to memory! Ask the Tutor tab if you need help with the feedback.")
