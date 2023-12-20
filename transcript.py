from youtube_transcript_api import YouTubeTranscriptApi


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

    return full_transcript_text
