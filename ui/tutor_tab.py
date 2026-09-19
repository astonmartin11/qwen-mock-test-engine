import streamlit as st
from core.ai_engines import chat_with_tutor_model

def render_ai_tutor(active_subject, grey_topics):
    st.subheader(f"Chat with your {active_subject} Tutor")
    
    chat_key = f"chat_messages_{active_subject}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input(f"Ask a doubt about {active_subject}..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state[chat_key].append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                tutor_response = chat_with_tutor_model(
                    active_subject, 
                    grey_topics, 
                    st.session_state[chat_key]
                )
            message_placeholder.markdown(tutor_response)
            
        st.session_state[chat_key].append({"role": "assistant", "content": tutor_response})
