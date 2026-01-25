import streamlit as st
from chatot_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage
import uuid
#*************utilites function**********
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id,"New Chat")
    st.session_state['message_history']= []

def add_thread(thread_id,title="New Chat"):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'][thread_id] = title

def load_coversation(thread_id):
    return chatbot.get_state(config={'configurable' : {'thread_id':thread_id}}).values.get('messages',[])

#*****************session setup************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = {}

add_thread(st.session_state['thread_id'])

#************sidebar-ui**************
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations') 


for thread_id, title in list(st.session_state['chat_threads'].items())[::-1]:
    if st.sidebar.button(title,key=str(thread_id)): 
        st.session_state['thread_id'] = thread_id
        messages = load_coversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role='user'
            else:
                role='ai'    

            temp_messages.append({'role':role,'content':message.content})    
        st.session_state['message_history'] = temp_messages    




#loading the coversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')  


if user_input:
     # Update title with first message
    if st.session_state['chat_threads'][st.session_state['thread_id']] == "New Chat":
        title = user_input[:50] + " ..." if len(user_input)>50 else user_input
        st.session_state['chat_threads'][st.session_state['thread_id']] = title

    #fisrt add the messagr to message histrory
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG= {'configurable' : {'thread_id':st.session_state['thread_id']}}    
    
    with st.chat_message('ai'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
    st.session_state['message_history'].append({'role':'ai','content':ai_message})    
