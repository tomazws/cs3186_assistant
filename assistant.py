import streamlit as st
from openai import OpenAI
import graphviz
import time
import json

# Process the messsage and display it in the chat message container and also append message to chat history
def displayAppendMessage(role, content, append=True):
    with st.chat_message(role):
        # Split the message by code blocks
        messages = content.split('```')
        for message in messages:
            # If the message is a graphviz diagram, display it as a diagram
            if message.find('digraph DFA {') > -1 and message[-2] == '}':
                message = message[message.find('digraph DFA {'):]
                st.graphviz_chart(message)
            else:
                st.write(message)
        st.write('')

    if append:
        st.session_state.messages.append({'role': role, 'content': content})

def buttonClicked(content):
    #displayAppendMessage('user', 'WTF??')
    with st.chat_message('user'):
        st.write('Button clicked')

# Create title and subheader for the Streamlit page
st.title('CS 3186 Student Assistant Chatbot')
st.subheader('Ask me anything about CS 3186')
with st.sidebar:
    st.write('asdf')
    if st.button('Convert NFA to DFA'):
        st.write('Button clicked')

# Initialize OpenAI Assistant API
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
assistant = client.beta.assistants.retrieve(st.secrets['OPENAI_ASSISTANT2'])

# Initialize session state variables
if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()
    st.session_state.messages = []

# Initialize chat messages
for message in st.session_state.messages:
    displayAppendMessage(message['role'], message['content'], False)

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    # Display user message in chat message container and add to chat history
    displayAppendMessage('user', prompt)

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
        while run.status != 'completed':
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

        # Display assistant message in chat message container and add to chat history
        displayAppendMessage('assistant', message)