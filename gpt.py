from prompts import *
from openai import OpenAI
import streamlit as st

from sidebar import start_sidebar
from split import *
from transcript import *

TITLE = "💬 YouTube Chatbot"
FIRST_CAPTION = ("🚀 A Streamlit chatbot powered by OpenAI LLM. Provide a YouTube link below and get a quick summary. "
                 "You can ask follow-up questions about the video, or ask to summarize another one anytime.")


def assistant_message(prompt):
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    messages.append({"role": "system", "content": prompt})

    # Print or log the message history here
    for message in messages:
        print(f"{message['role']}: {message['content']}")

    response = client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=messages)
    return response.choices[0].message.content


def further_assistant_message(prompt, role):
    st.session_state.messages.append({"role": f"{role}", "content": prompt})
    # The messages array should include the whole conversation history

    all_messages = [{"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages]

    messages = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages if m['role'] != 'user' and m['role'] != 'modelID']

    # Print or log the message history here
    for message in all_messages:
        print(f"{message['role']}: {message['content']}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Now the API call includes the entire conversation history
        for response in client.chat.completions.create(
                model=st.session_state.openai_model,
                messages=messages,
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")

    message_placeholder.markdown(full_response)

    # Remember to update your conversation history in session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append({"role": "modelID", "content": f"{st.session_state.openai_model}"})


youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.*'


# Utility functions
def init_streamlit_session_state():
    """Ensure all necessary session state variables are initialized."""
    session_variables = {
        "openai_model": None,
        "disabled": False,
        "good_api_key": False,
        "toggled": False,
        "toggle_disable": False,
        "openai_api_key": '',
        "owner_good": False,
        "messages": [],
        "new_yt": False,
        "tldr": False,
        "explain_more": False,
        "url_received": False
    }
    for key, value in session_variables.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_streamlit_session_state()
client = OpenAI(api_key=st.session_state.openai_api_key)
start_sidebar(client)

st.title(TITLE)
st.caption(FIRST_CAPTION)

if st.session_state.owner_good:
    st.session_state.all_good = True
else:
    if not (st.session_state.toggled and st.session_state.good_api_key):
        st.warning("To proceed, please add a valid OpenAI API key and lock it.", icon="⚠️️")
        st.session_state.all_good = False
    else:
        st.session_state.all_good = True

if "video_url" in st.session_state:
    st.video(st.session_state.video_url)

next_message_is_model = False
for message in st.session_state.messages:
    if message["role"] == "assistant":
        assistant_text = message["content"]
        next_message_is_model = True
    elif message["role"] == "modelID" and next_message_is_model:
        assistant_text += f'  \n<span style="font-size: 11px; color:gray"> Model: {message["content"]} </span>'
        with st.chat_message("assistant"):
            st.markdown(assistant_text, unsafe_allow_html=True)
        next_message_is_model = False
    elif message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat_mode():
    st.session_state.url_received = True
    st.session_state.tldr = True
    st.session_state.explain_more = True
    st.session_state.new_yt = True
    st.rerun()


if not st.session_state.url_received and st.session_state.all_good:
    st.info("Please enter a YouTube URL below to begin.", icon="ℹ️")
    if prompt := st.chat_input("https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        if not re.match(youtube_regex, str(prompt)):
            st.error('Please enter a valid YouTube URL.', icon="🚨")
        else:
            st.video(prompt)
            st.session_state.video_url = prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            with st.status("Summarizing...") as status:
                st.write("Fetching and processing transcript...")
                text = get_transcript(prompt)
                st.write("Got the transcript!")
                st.write("Now summarizing with gpt...")
                status.update(label="Got the transcript!", state="complete")
            if words_to_tokens(text) > 3277:
                with st.status("Using GPT...") as status:
                    status.update(label="Video is long, splitting in parts...", state="running")
                    chunks = split_text_into_chunks(text, 3277)
                    total_chunks = len(chunks)
                    status.update(label=f"Total {total_chunks} Parts", state="running")
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    for i, chunk in enumerate(chunks):
                        status.update(label=f"Summarizing Transcript Part {i + 1}/{total_chunks}...",
                                      state="running")
                        progress_bar.progress(i / total_chunks)
                        chunk_resp = assistant_message(
                            summarize_each_chunk(f"Raw Transcript {i + 1}/{total_chunks}:\n{chunk}"))
                        st.session_state.messages.append({"role": "system", "content":
                            f"Transcript Part {i + 1}/{total_chunks} Summary:\n{chunk_resp}"})
                        progress_text.text(f"Transcript Part {i + 1}/{total_chunks} summarized.")
                    progress_bar.progress(total_chunks / total_chunks)
                    progress_text.text(f"Transcript Part {i + 1}/{total_chunks} summarized.")
                    status.update(label="Summarized!", state="complete")
                further_assistant_message(last_message(total_chunks), "system")
                chat_mode()
            else:
                further_assistant_message(summary_request(text), "system")
                chat_mode()


elif st.session_state.url_received and st.session_state.all_good:
    def hide_buttons():
        for button_name in st.session_state['buttons_clicked']:
            st.session_state[button_name] = False


    def hide_all_buttons():
        st.session_state.tldr = False
        st.session_state.explain_more = False
        st.session_state.new_yt = False


    # The default is that no button has been clicked yet
    if 'buttons_clicked' not in st.session_state:
        st.session_state['buttons_clicked'] = []

    # TL;DR button
    if 'tldr' not in st.session_state['buttons_clicked'] and st.button("TL;DR List"):
        st.session_state['buttons_clicked'].append('tldr')
        hide_buttons()
        further_assistant_message(answer_only_from(emoji_list()), "system")
        st.rerun()

    # The Explain Further button
    if 'explain_more' not in st.session_state['buttons_clicked'] and st.button("Explain Further"):
        st.session_state['buttons_clicked'].append('explain_more')
        hide_buttons()
        further_assistant_message(answer_only_from(explain_more()), "system")
        st.rerun()

    # The Summarize Another Video button
    if 'new_yt' not in st.session_state['buttons_clicked'] and st.button("Summarize Another Video"):
        st.session_state.url_received = False
        st.session_state['buttons_clicked'] = []  # Reset the buttons clicked list
        hide_all_buttons()
        st.session_state.messages = []
        if 'video_url' in st.session_state:
            del st.session_state['video_url']
        st.rerun()

    video_chat_only = st.toggle("Answer Only From The Video's Summary/Transcript", value=True)

    if prompt := st.chat_input("Ask Further Questions?"):
        if video_chat_only:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            further_assistant_message(answer_only_from(prompt), "system")
            st.rerun()
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            further_assistant_message(answer_with_outside_info(prompt), "system")
            st.rerun()

st.caption(
    f"To modify API settings, click on the arrow in the top left corner to open the sidebar.  \n(Selected Model: {st.session_state.openai_model})")
