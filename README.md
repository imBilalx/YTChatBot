# YouTube Summarization Chatbot

This project encompasses a chatbot, powered by [OpenAI's GPT-3.5-turbo or GPT-4](https://platform.openai.com/) model, and hosted on a [Streamlit](https://streamlit.io/) application. This chatbot is designed to generate summaries for YouTube videos provided by the user via a textual link.

Once you've received the quick summary, you also have the option to ask follow-up questions about the video. Moreover, you can ask the chatbot to summarize another video anytime.

The chatbot interfaces with the YouTube Transcript API to retrieve video transcripts which it then summarizes, presenting a transcription that distills the key points and main content of the video.

Explore the live application here: https://ytchatbot.streamlit.app/

## Installation and Setup

### Prerequisites

The main libraries this project is based on are:

-  Streamlit
-  OpenAI
-  Youtube Transcript API

Additional detailed dependencies are listed in the `requirements.txt` file.

### Setup

Follow these steps to setup the chatbot:

#### Clone the Repository

Firstly, clone the repository to your local machine:

```shell
git clone https://github.com/itsBillyZee/YTChatBot.git
```

This will create a new directory in your current location named `YTChatBot`.

#### Setup a Virtual Environment 

It's good practice to create a virtual environment for each of your projects. 

-  For macOS/Linux:

    ```shell
    cd YTChatBot                     # Move into the cloned directory
    python3 -m venv env              # Create a new virtual environment
    source env/bin/activate          # Activate the virtual environment
    ```

-  For Windows:

    ```shell
    cd YTChatBot                     # Move into the cloned directory
    py -m venv env                   # Create a new virtual environment
    .\env\Scripts\activate           # Activate the virtual environment
    ```

#### Install Dependencies

After setting up the environment and activating it, install the required dependencies:

```shell
pip install -r requirements.txt
```

#### Setup Streamlit Secrets

To enable the owner toggle and prevent entering the API keys every time, you should create a secrets file:

1. Create a new directory `.streamlit` if it doesn't exist already, and within it create a new file called `secrets.toml`.

2. Open `secrets.toml` with a text editor and add the following:

```toml
OWNER_PASSCODE = "your_owner_passcode"
OPENAI_API_KEY = "your_openai_api_key"
```

Replace `"your_owner_passcode"` and `"your_openai_api_key"` with your desired passcode and your OpenAI API key, respectively.

#### Running the application

You can start the application using the below command in the terminal:

```shell
streamlit run app.py
```
Open a web browser and go to `http://localhost:8501` where you should see the application running.

### Usage

Provide a YouTube link in the text box and receive a quick summary. You can also ask follow-up questions about the video, or ask to summarize a different video. The application is also live and can be used directly without any installation at https://ytchatbot.streamlit.app/
