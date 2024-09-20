import os
import logging
import streamlit as st
from streamlit_cookies_controller import CookieController
import uuid
import mimetypes
import tempfile
from pathlib import Path

from data_intake import DataIntakeService
from retriever import DataIntakeRetriever
from chatgpt import ChatGPT

streamlit_root_logger = logging.getLogger(st.__name__)
logging.captureWarnings(False)
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_icon=os.environ["CHAT_FAVICON"], 
    page_title=os.environ["CHAT_TITLE"],
)
st.image(os.environ["CHAT_LOGO"], width=200)

st.markdown("""
    <style>
        * {
            overflow-anchor: none !important;
        }
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        div[data-testid="stDecoration"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        div[data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        #MainMenu {
            visibility: hidden;
            height: 0%;
        }
        header {
            visibility: hidden;
            height: 0%;
        }
        footer {
            visibility: hidden;
            height: 0%;
        }
        .block-container {
            padding: 0rem 1rem 1rem;
        }
        div.stChatMessage:has(div[data-testid="chatAvatarIcon-user"]) {
            flex-direction: row-reverse;
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True) 

client = DataIntakeService()
if os.environ["DATA_INTAKE_ACCESS_TOKEN"] == '':
    client.request_oauth2_token()

upload_mimetypes = ['pdf']
uploader = st.file_uploader("Upload file",upload_mimetypes)
if uploader is not None:
    logging.info("ATTEMPTING TO UPLOAD")
    trace_id = uuid.uuid4().hex
    filename = uploader.name
    suffix = Path(uploader.name).suffix
    mime = mimetypes.guess_type(uploader.name)[0]

    with tempfile.NamedTemporaryFile(suffix=suffix) as temp_file:
        temp_file.write(uploader.getvalue())

        client.request_create_upload_cloudevent(trace_id, filename, mime, temp_file.name)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": os.environ["CHAT_INITIAL_QUESTION"]}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input(os.environ["CHAT_PROMPT_LABEL"])
if prompt:
    logging.info("############################")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    retriever = DataIntakeRetriever(client=client, k=3, similarityThreshold=0)
    chatbot = ChatGPT(retriever)
    ai_resp = chatbot.ask_llm(prompt)
    with st.chat_message("assistant"):
        st.write(ai_resp)
        message = {"role": "assistant", "content": ai_resp}
        st.session_state.messages.append(message)
