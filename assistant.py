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
assistant = client.beta.assistants.retrieve(st.secrets['OPENAI_ASSISTANT'])

# Initialize session state variables
if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()
    st.session_state.messages = []

# Initialize chat messages
for message in st.session_state.messages:
    if message['role'] in ['user', 'assistant']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    # Send user message to OpenAI Assistant API
    client.beta.threads.messages.create(
        thread_id = st.session_state.thread.id,
        role = 'user',
        content = prompt
    )

    with st.spinner('Thinking ...'):
        # Create a run to process the user message
        run = client.beta.threads.runs.create(
            thread_id = st.session_state.thread.id,
            assistant_id = assistant.id
        )

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id = st.session_state.thread.id,
                run_id = run.id
            )
        
        # Retrieve message added by the assistant
        response = client.beta.threads.messages.list(
            thread_id = st.session_state.thread.id
        )
        message = response.data[0].content[0].text.value

        # Display assistant message in chat message container
        with st.chat_message('assistant'):
            st.markdown(message)
    
        # Add assistant message to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': message})