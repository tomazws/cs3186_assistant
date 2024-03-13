import streamlit as st
from openai import OpenAI
import graphviz
import time
import json

# Custom functions
# def createDiagram(dot_script):
#     with st.chat_message('dot_script'):
#         st.graphviz_chart(dot_script)
#     st.session_state.messages.append({'role': 'dot_script', 'content': dot_script})
#     return dot_script

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
    with st.chat_message(message['role']):
        if message['diagram'] != '':
            st.graphviz_chart(message['diagram'])
        st.markdown(message['content'])

# Chat input
if prompt := st.chat_input('Ask me anything about CS 3186'):
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt, 'diagram': ''})
    
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

    reponse_message = {
        'role': 'assistant',
        'content': '',
        'diagram': ''
    }

    # Wait for the run to complete
    with st.spinner('Thinking ...'):
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
            # function = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            reponse_message['diagram'] = args['dot_script']

            # Call function
            # response = globals()[function](**args)

            # Submit output from function call
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id = st.session_state.thread.id,
                run_id = run.id,
                tool_outputs = [
                    {
                        'tool_call_id': tool_call.id,
                        'output': 'An image of the state diagram is generated'
                    }
                ]
            )

    # Retrieve message added by the assistant
    response = client.beta.threads.messages.list(
        thread_id = st.session_state.thread.id
    )
    reponse_message['content'] = response.data[0].content[0].text.value

    # Display assistant message in chat message container
    with st.chat_message('assistant'):
        if reponse_message['diagram'] != '':
            st.graphviz_chart(reponse_message['diagram'])
        st.markdown(reponse_message['content'])

    # Add assistant message to chat history
    st.session_state.messages.append(reponse_message)