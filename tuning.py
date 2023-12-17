from openai import OpenAI
from split import *
from transcript_example import text
import streamlit as st

temperatures = [0.8, 1, 1.2]

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def assistant_message(prompt, temperature, append: bool = False, messages=None):
    if messages is None:
        messages = []

    if append:
        messages.append({"role": "system", "content": prompt})

    message_contents = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    message_contents.append({"role": "system", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=message_contents,
        temperature=temperature
    )

    return response.choices[0].message.content, messages

summary_storage = []

for run in range(5):
    print(f"-------Start of Run {run+1}/{5}-------")
    for temp in temperatures:
        chunks = split_text_into_chunks(text, 3277)
        total_chunks = len(chunks) - 1
        messages = []
        for i, chunk in enumerate(chunks):
            chunk_resp, messages = assistant_message(summarize_each_chunk(f"Raw Transcript {i}/{total_chunks}:\n{chunk}"),
                                                     temp,
                                                     messages=messages)
            messages.append({"role": "system", "content": f"Transcript Part {i}/{total_chunks} Summary:\n{chunk_resp}"})
            if i == 5:
                summary_storage.append(f"Transcript Part {i}/{total_chunks} Summary:\n{chunk_resp}")

        final_resp, messages = assistant_message(last_message(total_chunks), temp, append=True, messages=messages)
        messages.append({"role": "assistant", "content": final_resp})

        print(f"\nFINAL for Temperature {temp}")
        for message in messages:
            # Check for specific message content
            if "Transcript Part 5/8 Summary" in message['content']:
                print(f"{message['role']}: {message['content']}")
    print(f"-------End of Run {run+1}/{5}-------")

# Print stored summaries
print("\nStored summaries:")
for summary in summary_storage:
    print(summary)
