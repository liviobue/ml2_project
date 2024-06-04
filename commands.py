import openai
import base64
import cv2
from PIL import Image
from io import BytesIO
import base64
from pymongo import MongoClient
from keys import API_KEY
from keys import CONNECTION_STRING
from bson.objectid import ObjectId

openai.api_key = API_KEY

# MongoDB setup
mongo_client = MongoClient(CONNECTION_STRING)  # Adjust the connection string as needed
db = mongo_client["ML2-Project"]
collection = db["chats"]

messages = [
    {
        "role": "system",
        "content": "You are an AI designed to help describe videos for blind people by summarizing sequences of images into coherent narratives. I will provide you with some Zero/Few-Shot examples for reference, but your summaries should strictly adhere to the content of the initial video being described. Do not incorporate specific details or content from the examples provided, only use them to understand the format and style of the responses."
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
    if previous_description == "":
        previous_description = "There is no Previous frame. This is the first frame of the video."
    prompt = "Describe the persons and their actions in the following image. Previous frame description: " + previous_description
    description = imageRequest(imagebase64, prompt)
    return description

def summarize_descriptions(descriptions):
    combined_text = " ".join(descriptions)
    summary = textRequest("Here is a list of image descriptions. Let the user think that you are describing a video. Summarize this text in a continuous narrative: " + combined_text)
    return summary

def store_chat_in_mongodb(chat_data):
    collection.insert_one(chat_data)

def retrieve_past_interactions(limit=5, accurate_only=True):
    if limit ==0:
        return []
    query = [
        {
            '$match': {
                'accurate': accurate_only
            }
        },
        {
            '$sort': {
                'timestamp': -1
            }
        },
        {
            '$limit': limit
        }
    ]
    past_interactions = collection.aggregate(query)

    results = []
    for interaction in past_interactions:
        messages = interaction["messages"][-4:]  # Get the last 4 messages
        if len(messages) % 2 != 0:  # Ensure there are pairs of user and bot messages
            continue  # Skip if there is an odd number of messages
        pairs = []
        for i in range(0, len(messages), 2):
            if messages[i]["role"] == "user" and messages[i + 1]["role"] == "bot":
                pairs.append({"user": messages[i]["content"], "bot": messages[i + 1]["content"]})
        results.append(pairs)
    return results

# Restore session from MongoDB
def restore_session_from_mongodb(session_id):
    return collection.find_one({"_id": ObjectId(session_id)})