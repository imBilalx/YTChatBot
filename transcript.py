from youtube_transcript_api import YouTubeTranscriptApi
import re


def get_transcript(video_url):
    # Extract video id from the URL
    if 'youtu.be' in video_url:
        video_id = video_url.split('https://youtu.be/')[1].split('?')[0]
    elif 'youtube.com' in video_url:
        video_id = video_url.split("watch?v=")[1].split('&')[0]

    # Fetch the list of all available transcripts of video
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try and get English transcript if available, else take the first available one
    try:
        transcript = transcript_list.find_transcript(['en'])
    except:
        transcript = transcript_list.find_transcript([t.language_code for t in transcript_list])

    # Fetch the transcript
    transcript_fetched = transcript.fetch()

    # Concatenate all the text fields
    full_transcript_text = " ".join([t['text'] for t in transcript_fetched])

    # Remove special characters without adding spaces and remove any extra spaces
    full_transcript_text = re.sub(r'\W+', ' ', full_transcript_text)
    full_transcript_text = " ".join(full_transcript_text.split())

    return full_transcript_text


# print(get_transcript("https://www.youtube.com/watch?v=7YuAzR2XVAM"))
