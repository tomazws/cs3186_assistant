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

# Initialize chat messages
for message in st.session_state.messages:
    if message.role in ['user', 'assistant']:
        with st.chat_message(message.role):
            st.markdown(message.content[0].text.value)

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    # Send user message to OpenAI Assistant API
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role='user',
        content=prompt
    )

    width st.spinner('Thinking ...'):
        # Run the assistant API
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )
        
        # Retrieve messages added by the assistant
        response = client.beta.threads.messages.list(
            thread_id=st.session_state.thread.id
        )

        messages = response.data
        message = messages[0].content[0].text.value

        # Display assistant message in chat message container
        with st.chat_message('assistant'):
            st.markdown(message)
    
        # Add assistant message to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': message})