import streamlit as st
import re
from transcript import get_transcript
from openai import OpenAI
from split import *
from Prompts import *

# Initialize Streamlit UI components
st.title("YT Chatbot")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-1106"

# Initialize messages in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("Hello, please enter a YouTube URL to begin!")

youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'

st.session_state.debug_mode = True  # Set this to False to turn off debug information

# Processing YouTube URL
if prompt := st.chat_input("YouTube URL (https://www.youtube.com/watch?v=dQw4w9WgXcQ)"):
    if not re.match(youtube_regex, str(prompt)):
        st.error('Please enter a valid YouTube URL.')
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.status("Fetching and processing transcript...") as status:
            full_transcript_text = get_transcript(prompt)

            # Check if transcript exceeds token limit
            MAX_TOKENS = 16385
            if words_to_tokens(full_transcript_text) > MAX_TOKENS:
                chunks = split_text_into_chunks(full_transcript_text)
                total_chunks = len(chunks)

                # Send initial message about large transcript with the first part
                first_part_message = (f"The total length of the transcript that I want to send you is too large to "
                                      f"send in only one piece.\n\nFor sending you that transcript, I will follow "
                                      f"this rule:\n\n[START PART 0/{total_chunks}]\nSome text here\n[END PART {total_chunks}/"
                                      f"{total_chunks}]\n\nThen you just answer: 'Received part 0/"
                                      f"{total_chunks}'\n\nAnd when I tell you 'ALL PARTS SENT', then you can continue "
                                      f"processing the data and answering my requests. Understood?")
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": first_part_message}
                        for m in st.session_state.messages
                    ],
                )

                # Process the response and print to terminal
                if st.session_state.debug_mode:
                    st.write(first_part_message)
                    print(first_part_message)
                # Optionally display or skip displaying this response

                # Process and send remaining parts
                for i, chunk in enumerate(chunks):
                    part_message = (f"Do not answer yet. This is just another part of the text I want to send you. "
                                    f"Just receive and acknowledge as 'Part {i}/{total_chunks} received' and wait for "
                                    f"the next part.\n[START PART {i}/{total_chunks}]\n{chunk}\n[END PART {i}/"
                                    f"{total_chunks}]\nRemember not answering yet. Just acknowledge you received this "
                                    f"part with the message 'Part {i}/{total_chunks} received' and wait for the next "
                                    f"part.")
                    # st.session_state.messages.append({"role": "user", "content": part_message})
                    response = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": part_message}
                            for m in st.session_state.messages
                        ],
                    )
                    # Process the response and print to terminal
                    if st.session_state.debug_mode:
                        st.write(part_message)
                        print(part_message)
                    # Process the response
                    # Skip displaying these responses

                # Indicate all parts sent
                final_message = f"[START PART {total_chunks}/{total_chunks}]\nLast Part Content\n[END PART {total_chunks}/{total_chunks}]\nALL PARTS SENT. Now that you've received all parts, please provide a concise summary of the transcript that captures the main points and overall theme of the content."
                # st.session_state.messages.append({"role": "user", "content": final_message})
                # Send the summary request to OpenAI
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for response in client.chat.completions.create(
                            model=st.session_state["openai_model"],
                            messages=[
                                {"role": m["role"], "content": final_message}
                                for m in st.session_state.messages
                            ],
                            stream=True,
                    ):
                        full_response += (response.choices[0].delta.content or "")
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                # Process the response and print to terminal
                if st.session_state.debug_mode:
                    st.write(final_message)
                    print(final_message)


            else:
                summary_request = (f'The following text is a transcript from a video. Please provide a concise summary '
                                   f'that captures the main points and overall theme of the content.\n"{full_transcript_text}"')


                # Send the summary request to OpenAI
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for response in client.chat.completions.create(
                            model=st.session_state["openai_model"],
                            messages=[
                                {"role": m["role"], "content": summary_request}
                                for m in st.session_state.messages
                            ],
                            stream=True,
                    ):
                        full_response += (response.choices[0].delta.content or "")
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
