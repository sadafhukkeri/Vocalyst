import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import os
import google.generativeai as genai

# Load all environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for generating detailed notes
prompt = """You are a YouTube video summarizer.Create a detailed summary of the video, including all major topics and key insights.
Summarize the video in a way that highlights its main ideas and any actionable advice. : """

# Extract video_id from the YouTube URL
def extract_video_id(youtube_video_url):
    try:
        parsed_url = urlparse(youtube_video_url)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            query = parse_qs(parsed_url.query)
            return query.get("v", [None])[0]  # Extract 'v' parameter
        elif parsed_url.hostname == "youtu.be":
            return parsed_url.path.lstrip("/")  # Extract path for shortened URLs
        return None
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {e}")

# Get transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            raise ValueError("Invalid YouTube video link!")

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([item["text"] for item in transcript_text])
        return transcript

    except Exception as e:
        raise ValueError(f"Error fetching transcript: {e}")

# Get the summary based on the prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        raise ValueError(f"Error generating content: {e}")

# Streamlit App
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube video link:")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)
        if video_id:
            # Display video thumbnail
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        else:
            st.error("Invalid YouTube link. Please provide a valid URL!")
    except ValueError as e:
        st.error(str(e))

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
    except ValueError as e:
        st.error(str(e))
