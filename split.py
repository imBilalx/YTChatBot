def words_to_tokens(text):
    num_words = len(text.split())
    tokens = (num_words * 2048) / 1500
    return round(tokens)


def split_text_into_chunks(text, max_tokens):
    words = text.split()
    chunk_size = int((max_tokens * 1500) / 2048)  # Convert tokens to words
    text_chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return text_chunks

