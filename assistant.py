import streamlit as st
from openai import OpenAI
import graphviz
import time
import json

def displayMessage(role, content):
    messages = content.split('```')

# Create title and subheader for the Streamlit page
st.title('CS 3186 Student Assistant Chatbot')
st.subheader('Ask me anything about CS 3186')

# Initialize OpenAI Assistant API
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
assistant = client.beta.assistants.retrieve(st.secrets['OPENAI_ASSISTANT2'])

# Initialize session state variables
if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()
    st.session_state.messages = []

# Initialize chat messages
for message in st.session_state.messages:
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

    # Create a run to process the user message
    run = client.beta.threads.runs.create(
        thread_id = st.session_state.thread.id,
        assistant_id = assistant.id
    )

    # Wait for the run to complete
    with st.spinner('Thinking ...'):
        # Check the status of the run
        while run.status == 'queued' or run.status == 'in_progress':
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id = st.session_state.thread.id,
                run_id = run.id
            )

        # Retrieve message added by the assistant
        response = client.beta.threads.messages.list(
            thread_id = st.session_state.thread.id
        )
        message = response.data[0].content[0].text.value

        st.text(response.data[0].content[0].text)

        message_blocks = message.split('```')

        for message_block in message_blocks:
            st.text('---------')
            st.text(len(message_block))
            st.text(f'Message begins with plaintext: {message_block[:9] == "plaintext"}')
            if message_block[:9] == 'plaintext':
                message_block = message_block[10:]

            st.text(f'Message begins with digraph: {message_block[:7] == "digraph"}')
            st.text(f'Message ends with {'}'}\n: {message_block[-3] == "}\n"}')
            if message_block[:7] == 'digraph' and message_block[-3] == '}\n':
                st.text('graphviz')
                st.graphviz_chart(message_block)
            else:
                st.text(message_block)
            st.text('---------')

        # Display assistant message in chat message container
        with st.chat_message('assistant'):
            st.markdown(message)
            
        # Add assistant message to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': message})