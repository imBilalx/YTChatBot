def summary_request(text):
    return (f'Provide a detailed summary of the following content. Your summary should identify and '
            f'explain the central themes and main messages involved. It should also describe any key '
            f'narrative or structural elements unfolding in the course of the material. If there are any '
            f'significant phrases, points or moments, include them in your summary. Remember to start your '
            f'summary without referring to the content as a "transcript".\n"{text}"')


def first_message(total_chunks):
    _ = (f"The total length of the transcript that I want to send you is too large to "
         f"send in only one piece.\n\nFor sending you that transcript, I will follow "
         f"this rule:\n\n[START PART 0/{total_chunks}]\nSome text here\n[END PART {total_chunks}/"
         f"{total_chunks}]\n\nThen you just answer: 'Received part 0/"
         f"{total_chunks}'\n\nAnd when I tell you 'ALL PARTS SENT', then you can continue "
         f"processing the data and answering my requests. Understood?")
    # print(_)
    return _


def mid_message(i, chunk, total_chunks):
    _ = (f"Do not answer yet. This is just another part of the text I want to send you. "
         f"Just receive and acknowledge as 'Part {i}/{total_chunks} received' and wait for "
         f"the next part.\n[START PART {i}/{total_chunks}]\n{chunk}\n[END PART {i}/"
         f"{total_chunks}]\nRemember not answering yet. Just acknowledge you received this "
         f"part with the message 'Part {i}/{total_chunks} received' and wait for the next "
         f"part.")
    # print(_)
    return _


def last_message(total_chunks):
    _ = (
        f"Based on the previously provided {total_chunks} summaries in the conversation history, create a coherent "
        f"and succinct summary. This final summary should encapsulate the primary themes and key points from the "
        f"entire content, projecting an overall narrative drawn from the individual summaries of the complete "
        f"transcript.")
    # print(_)
    return _


def summarize_each_chunk(chunk):
    _ = (f"Create a concise summary of the following section of the transcript, highlighting all key "
         f"events and major points. Keep in mind that this is one segment of a larger transcript, and this summary "
         f"will be merged with others to form an overarching succinct presentation of the entire transcript. Please "
         f"ensure the narrative flow and fidelity of the original content while optimizing for clarity and "
         f"brevity. If this is not the first transcript section, please refer to the previously summarized transcript "
         f"parts from the message history for better context and a more cohesive summary.\n'{chunk}'")
    # print(_)
    return _


def answer_only_from(question):
    _ = (f"Using only the summaries, the full transcript or both provided in our previous exchanges, please answer "
         f"the following question:\n'{question}'\nIt's crucial to note that your response "
         f"should solely rely on the "
         f"information contained "
         "within the message history. Refrain from introducing any additional data or outside information that wasn't "
         "part of the message history.")
    return _


def answer_with_outside_info(question):
    _ = (f"Along with the summaries, the full transcript or both provided in our previous exchanges, feel free to "
         f"incorporate "
         f"outside information to answer the following question:\n'{question}'.\nPlease note, while the provided material "
         f"should form the base of your response, enriching it with additional data or relevant outside information "
         "is acceptable and encouraged.")
    return _


def emoji_list():
    _ = ("Extract all facts from the text and summarize it in all relevant aspects in up to seven bullet points and a "
         "1-liner summary. Pick a good matching emoji for every bullet point.")
    return _


def explain_more():
    _ = (
        "Please provide a further detailed explanation of each point. Expand upon the main ideas, ensuring clarity "
        "and depth of understanding for each topic.")
    return _
