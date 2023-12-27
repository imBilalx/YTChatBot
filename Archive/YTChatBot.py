import streamlit as st
import re


class YTChatBot:

    def __init__(self):
        super().__init__()

    def startup(self):
        st.markdown("Hello, please enter a YouTube URL to begin!")

    def user_url(self):
        st.chat_input("YouTube URL (https://www.youtube.com/watch?v=dQw4w9WgXcQ)")


