from openai import OpenAI, AuthenticationError
import streamlit as st
import re


def start_sidebar(client):
    with st.sidebar:
        # Constants
        SIDEBAR_TITLE = "API Settings"
        GET_API_LINK = "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        API_KEY_PATTERN = "^sk-[a-zA-Z0-9]{48}$"
        GPT_MODEL_CHOICES = {
            "GPT 3.5 Turbo": "gpt-3.5-turbo-1106",
            "GPT 4 Preview": "gpt-4-1106-preview",
        }
        OWNER_PASSCODE = st.secrets["OWNER_PASSCODE"]
        PASSCODE_INPUT_LABEL = "Enter Passcode  🔑"
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        API_INPUT_LABEL = "OpenAI API Key  🔑"
        OWNER_LABEL = "Owner?"
        LOCK_TOGGLE_LABEL = "🔒 Lock Key"

        st.sidebar.title(SIDEBAR_TITLE)

        f"{GET_API_LINK}"

        model = st.radio("Select GPT Model", list(GPT_MODEL_CHOICES.keys()))
        st.session_state.openai_model = GPT_MODEL_CHOICES[model]

        owner = st.toggle(OWNER_LABEL)
        if owner:
            st.session_state.toggled = False
            owner_code = st.text_input(PASSCODE_INPUT_LABEL,
                                       type="password")
            if owner_code == OWNER_PASSCODE:
                st.success('Welcome', icon="✅")
                st.session_state.openai_api_key = OPENAI_API_KEY
                st.session_state.owner_good = True

            else:
                st.error('Invalid Passcode', icon="🚨")

        else:
            st.session_state.owner_good = False
            confirm_api = st.toggle(LOCK_TOGGLE_LABEL, disabled=st.session_state.toggle_disable)

            if confirm_api:
                st.session_state.disabled = True
                st.session_state.toggled = True
            else:
                st.session_state.toggled = False
                st.session_state.disabled = False

            st.session_state.openai_api_key = st.text_input(API_INPUT_LABEL,
                                                            type="password",
                                                            disabled=st.session_state.disabled)

            if st.session_state.toggled:

                if re.match(API_KEY_PATTERN, st.session_state.openai_api_key):

                    try:
                        response = client.models.list()
                        st.success('Valid API Key', icon="✅")
                        st.session_state.good_api_key = True
                    except AuthenticationError:
                        st.error("API Key Authentication Failed", icon="🚨")
                        st.session_state.good_api_key = False
                else:
                    st.warning("Incorrect API Key Format", icon="🚨")
                    st.session_state.good_api_key = False

            else:
                if st.session_state.openai_api_key:
                    st.info('Select the Lock Key Toggle located above.', icon="ℹ️")

        st.divider()
        st.subheader("👨‍💻 Author: **Bilal Akhtar**", anchor=False)

        st.subheader("🔗 Contact:", anchor=False)
        st.markdown(
            """
            - [Email](mailto:bilalakhtar268@gmail.com)
            - [LinkedIn](https://www.linkedin.com/in/iambilalakhtar/)
            - [Github](https://github.com/itsBillyZee)
            """
        )
