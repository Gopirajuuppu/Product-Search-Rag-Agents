import os
from pathlib import Path
import openai
from openai import OpenAI

openAI__api_key = "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"
os.environ["OPENAI_API_KEY"] = openAI__api_key
openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])



def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def get_answer(messages):
    system_message = [{"role": "system", "content": "You are an helpful AI chatbot, that answers questions asked by User."}]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    return response.choices[0].message.content