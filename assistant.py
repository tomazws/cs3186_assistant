from openai import OpenAI
import streamlit as st
import graphviz
import uuid
import time
import json
import re
import base64
import io
from functions import nfa_to_dfa

################################################################################
##                           INITIALIZE APPLICATION                           ##
################################################################################
# Initialize OpenAI Assistant API
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
assistant = client.beta.assistants.retrieve(st.secrets['OPENAI_ASSISTANT'])

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create(
        metadata={
            'session_id': st.session_state.session_id,
        }
    )



if 'messages' not in st.session_state:
    st.session_state.messages = []

################################################################################
##                                 FUNCTIONS                                  ##
################################################################################
# Process the messsage and display it in the chat message container and also append message to chat history
def displayMessage(role, content):
    st.text(content)
    with st.chat_message(role):

        latex_expr = 'V = \{S, A, B\}'
        st.write(f"The pythagorean theorem is given by the equation ${latex_expr}$.")
        
        # Split the message by code blocks
        messages = content.split('```')
        for message in messages:
            # If the message is a graphviz diagram, display it as a diagram
            match = re.search('digraph .* {', message)
            if match and message[-2] == '}':
                message = message[match.start():]
                st.graphviz_chart(message)
            else:
                st.write(message)
    st.write('')

def getCompletion(prompt):
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

    # # Wait for the run to complete
    with st.spinner('Thinking ...'):
        # Check the status of the run
        while run.status != 'completed':
            # Check the status of the run
            while run.status == 'queued' or run.status == 'in_progress':
                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(
                    thread_id = st.session_state.thread.id,
                    run_id = run.id
                )
        
            if run.status == 'requires_action':
                # Retrieve tool call
                tool_call = run.required_action.submit_tool_outputs.tool_calls[0]

                # Extract function name and arguments
                function = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # Call function
                response = globals()[function](**args)
                # st.text('Response from function:')
                # st.text(response)

                # Submit output from function call
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id = st.session_state.thread.id,
                    run_id = run.id,
                    tool_outputs = [
                        {
                            'tool_call_id': tool_call.id,
                            'output': response
                        }
                    ]
                )
            
            if run.status == 'failed':
                break

        # Retrieve message added by the assistant
        response = client.beta.threads.messages.list(
            thread_id = st.session_state.thread.id
        )
        message = response.data[0].content[0].text.value

        # Display assistant message in chat message container and add to chat history
        displayMessage('assistant', message)
        st.session_state.messages.append({'role': 'assistant', 'content': message})

################################################################################
##                                  LAYOUTS                                   ##
################################################################################
# Create title and subheader for the Streamlit page
st.title('CS 3186 Student Assistant Chatbot')
# st.subheader('Using OpenAI Assistant API (gpt-4-0613)')

# Display chat messages
for message in st.session_state.messages:
    displayMessage(message['role'], message['content'])

with st.sidebar:
    st.write('Features')
    
if st.sidebar.button('Convert NFA to DFA'):
    message = 'I would like to convert NFA to DFA'
    displayMessage('user', message)
    st.session_state.messages.append({'role': 'user', 'content': message})
    getCompletion(message)
    
if st.sidebar.button('Generate a DFA diagram'):
    message = 'I would like to generate a DFA from regular expression or langage'
    displayMessage('user', message)
    st.session_state.messages.append({'role': 'user', 'content': message})
    getCompletion(message)
    
if st.sidebar.button('Question about this course'):
    message = 'I have a question about the class syllabus'
    displayMessage('user', message)
    st.session_state.messages.append({'role': 'user', 'content': message})
    getCompletion(message)
    
if st.sidebar.button('Question on Assignment 1'):
    message = 'I have a question on assignment #1'
    displayMessage('user', message)
    st.session_state.messages.append({'role': 'user', 'content': message})
    getCompletion(message)

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    # Display user message in chat message container and add to chat history
    displayMessage('user', prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    getCompletion(prompt)