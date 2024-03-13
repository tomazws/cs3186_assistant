import json
import uuid
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
    st.session_state.assistant = client.beta.assistants.retrieve('asst_G8iILCF0d74d4y3IW4nKNRbn')
    st.session_state.messages = []
    st.session_state.run = {'status': None}
    st.session_state.thread = client.beta.threads.create(metadata={'session_id': st.session_state.session_id})

# Display chat messages
elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == 'completed':
    st.session_state.messages = client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
    for message in st.session_state.messages.data:
        st.markdown(message.content)