import openai
import base64
import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import tempfile
import base64
from transformers import pipeline
from pymongo import MongoClient
from keys import API_KEY
from keys import CONNECTION_STRING

openai.api_key = API_KEY

# MongoDB setup
mongo_client = MongoClient(CONNECTION_STRING)  # Adjust the connection string as needed
db = mongo_client["ML2-Project"]
collection = db["chats"]

messages = [
    {
        "role": "system",
        "content": "You are an AI that helps to describe videos for blind people by summarizing a sequence of images into a coherent narrative."
    }
]

def _openai():
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
    )
    return response.choices[0].message.content

def imageRequest(imagebase64, prompt):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imagebase64}",
                    },
                },
            ],
        }
    )
    return _openai()

def textRequest(prompt):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
            ],
        }
    )
    return _openai()

def describe_frame(frame, previous_description=""):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    imagebase64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    prompt = "Describe the persons and their actions in the following image. Previous frame description: " + previous_description
    description = imageRequest(imagebase64, prompt)
    return description

def summarize_descriptions(descriptions):
    combined_text = " ".join(descriptions)
    summary = textRequest("Here is a list of image descriptions. Let the user think that you are describing a video. Summarize this text in a continuous narrative: " + combined_text)
    return summary

def store_chat_in_mongodb(chat_data):
    collection.insert_one(chat_data)