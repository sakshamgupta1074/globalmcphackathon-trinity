import asyncio
import streamlit as st
from agents.team import Team

st.set_page_config(page_title="Chatbot", page_icon="🤖")

if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

def run_async(coro):
    return st.session_state.loop.run_until_complete(coro)

if "team" not in st.session_state:
    st.session_state.team = Team()

user_input = st.chat_input("Type your message...")
if user_input:
    run_async(st.session_state.team.send(user_input))

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        async def render():
            buffer = ""
            async for msg in st.session_state.team.stream_responses():
                if msg.type == "TextMessage":
                    buffer += msg.content + "\n\n"
                    response_placeholder.write(buffer)

        run_async(render())