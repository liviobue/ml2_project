import openai
import base64
import requests
from keys import API_KEY

openai.api_key = API_KEY

messages = []

def _openai():
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
    )
    return response.choices[0]

def request(image_url, promt):
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
                        "url": image_url,
                    },
                },
            ],
        }
    )
    return _openai()

def extract(image_url):
    image_url = image_url,
    promt = """
        Identify a social situation observable in this picture. 
        Please respond with a description of the social situation, 
        he people involved, including their activities and what they
        look like. Format your response as a JSON object. Besides 
        the general descriptions of the social situation, the 
        resulting JSON object should contain an attribute named
        persons containing a list of person object. Make sure 
        that every person object not only contains information 
        about their activity, but also everything observable that 
        can be used to recognise the same person in another picture.
    """
    return request(image_url, promt)

def recognize(image_url, person_description):
    image_url = image_url,
    promt = f"""
        Analyse this picture and decide if you can detect a person that corresponds
        to the following description: {person_description}. If the person is present, 
        provide additional details about their activity in this picture.
    """
    return request(image_url, promt)

social_situation = extract("https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg")
person_tobe_detected = social_situation.persons[0]
recognition = recognize("https://chunntguet.xyz/pics/eliott-reyna-5KrZ3UoDKC4-unsplash.jpg", person_tobe_detected)