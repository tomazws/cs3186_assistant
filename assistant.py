import json
import uuid
import time
import streamlit as st
import graphviz
from openai import OpenAI

# Create title and subheader for the Streamlit page
st.title('CS 3186 Student Assistant Chatbot')
st.subheader('Ask me anything about CS 3186')

# Initialize OpenAI Assistant API
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.assistant = client.beta.assistants.retrieve(st.secrets['OPENAI_ASSISTANT'])
    st.session_state.thread = client.beta.threads.create(metadata={'session_id': st.session_state.session_id})
    st.session_state.messages = []
    st.session_state.run = {'status': None}
    st.session_state.retry_error = 0

# Display chat messages
elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == 'completed':
    st.session_state.messages = client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
    st.write(st.session_state.messages.data)
    # for message in reversed(st.session_state.messages.data):
    #     if message.role in ['user', 'assistant']:
    #         for content_part in message.content:
    #             st.markdown(content_part.text.value)

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    with st.chat_message('user'):
        st.markdown(prompt)
    
    message_data = {
        'thread_id': st.session_state.thread.id,
        'role': 'user',
        'content': prompt
    }

    st.session_state.messages = client.beta.threads.messages.create(**message_data)

    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id
    )
    if st.session_state.retry_error < 3:
        time.sleep(1)
        st.rerun()

# Handle run status
if hasattr(st.session_state.run, 'status') and st.session_state.run.status != 'completed':
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id
        )
        if st.session_state.retry_error < 3:
            time.sleep(3)
            st.rerun()

