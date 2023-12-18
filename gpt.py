import re
from Prompts import *
from openai import OpenAI
import streamlit as st
from split import *


def assistant_message(prompt):
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    messages.append({"role": "system", "content": prompt})

    # Print or log the message history here
    for message in messages:
        print(f"{message['role']}: {message['content']}")

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages)
        return response.choices[0].message.content


def further_assistant_message(prompt, role):
    st.session_state.messages.append({"role": f"{role}", "content": prompt})
    # The messages array should include the whole conversation history

    all_messages = [{"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages]

    messages = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages if m['role'] != 'user']

    # Print or log the message history here
    for message in all_messages:
        print(f"{message['role']}: {message['content']}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Now the API call includes the entire conversation history
        for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages,
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")

    message_placeholder.markdown(full_response)

    # Remember to update your conversation history in session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})


youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'

if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "good_api_key" not in st.session_state:
    st.session_state.good_api_key = False

with st.sidebar:

    openai_api_key = st.text_input("OpenAI API Key",
                                   type="password",
                                   disabled=st.session_state.disabled)

    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

    confirm_api = st.toggle("Apply")

    if confirm_api:
        st.session_state.disabled = False
        if re.match("^sk-[a-zA-Z0-9]{48}$", openai_api_key):
            st.success('Valid API Key', icon="✅")
            st.session_state.good_api_key = True
        else:
            st.error("Invalid API Key", icon="🚨")
    else:
        st.session_state.disabled = True

st.title("💬 YouTube Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

client = OpenAI(api_key=openai_api_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-1106"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "new_yt" not in st.session_state:
    st.session_state.new_yt = False

if "tldr" not in st.session_state:
    st.session_state.tldr = False

if "explain_more" not in st.session_state:
    st.session_state.explain_more = False

if "video_url" in st.session_state:
    st.video(st.session_state["video_url"])

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Check if the "url_received" state variable exists; if not, initialize it
if "url_received" not in st.session_state:
    st.session_state.url_received = False

if not st.session_state.url_received:
    if not st.session_state.good_api_key:
        st.info("Please add your OpenAI API key first to continue.", icon="ℹ️")
    else:
        st.info("Please enter a YouTube URL below to begin.", icon="ℹ️")
        if prompt := st.chat_input("https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
            if not re.match(youtube_regex, str(prompt)):
                st.error('Please enter a valid YouTube URL.', icon="🚨")
            else:
                st.video(prompt)
                st.session_state["video_url"] = prompt
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.status("Summarizing...") as status:
                    st.write("Fetching and processing transcript...")
                    text = get_transcript(prompt)
                    st.write("Got the transcript!")
                    st.write("Now summarizing with gpt...")
                    status.update(label="Done!", state="complete")
                if words_to_tokens(text) > 3277:
                    with st.status("Using GPT...") as status:
                        st.write("Video is long, splitting in parts...")
                        chunks = split_text_into_chunks(text, 3277)
                        total_chunks = len(chunks) - 1
                        st.write(f"Total {total_chunks} Parts")
                        for i, chunk in enumerate(chunks):
                            chunk_resp = assistant_message(
                                summarize_each_chunk(f"Raw Transcript {i}/{total_chunks}:\n{chunk}"))
                            st.session_state.messages.append({"role": "system", "content":
                                f"Transcript Part {i}/{total_chunks} Summary:\n{chunk_resp}"})
                            st.write(f"Part {i}/{total_chunks} summarized...")

                        status.update(label="Done!", state="complete")
                    further_assistant_message(last_message(total_chunks), "system")
                    # After processing the URL, set "url_received" to True
                    st.session_state.url_received = True
                    st.session_state.tldr = True
                    st.session_state.explain_more = True
                    st.session_state.new_yt = True
                    st.rerun()
                else:
                    further_assistant_message(summary_request(text), "system")
                    # After processing the URL, set "url_received" to True
                    st.session_state.url_received = True
                    st.session_state.tldr = True
                    st.session_state.explain_more = True
                    st.session_state.new_yt = True
                    st.rerun()

else:
    def hide_buttons():
        for button_name in st.session_state['buttons_clicked']:
            st.session_state[button_name] = False


    def hide_all_buttons():
        st.session_state.tldr = False
        st.session_state.explain_more = False
        st.session_state.new_yt = False


    def show_buttons():
        for button_name in st.session_state['buttons_clicked']:
            st.session_state[button_name] = True


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

    # # Display button if not clicked before
    # if not st.session_state.tldr and st.button("TL;DR List"):
    #     further_assistant_message(answer_only_from(emoji_list()))
    #     st.session_state.tldr = True  # Update the clicked state
    #
    # elif st.session_state.new_yt and st.button("Enter a new YouTube URL"):
    #     st.session_state.messages = []
    #     st.session_state.url_received = False
    #     st.session_state.tldr = False  # Reset the clicked state
    #     st.rerun()
    # else:
    #     prompt = st.chat_input("Ask Further Questions?")
    #
    # if prompt := st.chat_input("Ask Further Questions?"):
    #     # Append the user's input to the chat history
    #     st.session_state.messages.append({"role": "user", "content": prompt})
    #     with st.chat_message("user"):
    #         st.markdown(prompt)
    #     st.session_state.new_yt = False  # Hide button
    #     # Display the assistant's reply
    #     further_assistant_message(answer_only_from(prompt))
    #     st.session_state.new_yt = True  # Show button
    #     st.rerun()
