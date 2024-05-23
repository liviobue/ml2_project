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
from keys import API_KEY

openai.api_key = API_KEY

messages = []

def _openai():
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
    )
    return response.choices[0].message.content

def imageRequest(imagebase64, promt):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": promt
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

def textRequest(promt):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": promt
                },
            ],
        }
    )
    return _openai()

def describe_frame(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    imagebase64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    description = imageRequest(imagebase64, "Describe the persons and their actions in the following image")
    return description

def summarize_descriptions(descriptions):
    combined_text = " ".join(descriptions)
    summary = textRequest("Here is a list of image describtions. let the user think that you are describing a video. Summarize me this text in a continuous text" + combined_text)
    return summary