import streamlit as st
import re
from transcript import get_transcript

st.markdown("""
# YT Chatbot
""")

st.markdown("Hello, please enter a YouTube URL to begin!")

prompt = st.chat_input("YouTube URL (https://www.youtube.com/watch?v=dQw4w9WgXcQ)")

youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'

if prompt:
    if not re.match(youtube_regex, str(prompt)):
        st.error('Please enter a valid YouTube URL.')
    else:
        with st.status("Thank you. Proceeding..."):
            st.write("Getting transcript...")
            full_transcript_text = get_transcript(prompt)
            st.write("Downloaded Transcript!")
            st.write("Reading transcript and summarizing...")
        st.markdown(full_transcript_text)


