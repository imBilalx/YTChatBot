from openai import OpenAI
from prompts import summary_request
from split import *
from already_sum import text4 as already_sum_text
from rouge import Rouge

messages = []

client = OpenAI(api_key="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")


def assistant_message(prompt, append: bool = False):
    if append:
        messages.append({"role": "system", "content": prompt})

    message_contents = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    message_contents.append({"role": "system", "content": prompt})

    # Print or log the message history here
    # for message in messages:
    #     print(f"{message['role']}: {message['content']}")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=message_contents, )
    return response.choices[0].message.content


url = "https://www.youtube.com/watch?v=y-TPFKTnG_4"
text = get_transcript(url)
if words_to_tokens(text) > 3277:
    chunks = split_text_into_chunks(text, 3277)
    total_chunks = len(chunks) - 1
    for i, chunk in enumerate(chunks):
        chunk_resp = assistant_message(summarize_each_chunk(f"Raw Transcript {i}/{total_chunks}:\n{chunk}"))
        messages.append({"role": "system", "content": f"Transcript Part {i}/{total_chunks} Summary:\n{chunk_resp}"})

    final_resp = assistant_message(last_message(total_chunks), append=True)
    messages.append({"role": "assistant", "content": final_resp})
    # print("FINAL")
    # for message in messages:
    #     print(f"{message['role']}: {message['content']}")
else:
    final_resp = assistant_message(summary_request(text))




# rouge = Rouge()
print("AI Summary: " + final_resp)
# print("Summary from Author: " + already_sum_text)
#
# scores = rouge.get_scores(final_resp, already_sum_text, avg=True)
#
# print("ROUGE Scores:", scores)
