import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import tempfile
import base64
from transformers import pipeline

st.title("Video Upload and Frame Extraction")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

def extract_frames(video_path, frame_rate=2):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    for i in range(0, frame_count, fps * frame_rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames

description_model = pipeline("text2text-generation", model="gpt-3.5-turbo")

def describe_frame(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    prompt = f"Describe the persons and their actions in the following image: {img_str}"
    description = description_model(prompt)[0]['generated_text']
    return description

def summarize_descriptions(descriptions):
    combined_text = " ".join(descriptions)
    summary_prompt = f"Summarize the following descriptions: {combined_text}"
    summary = description_model(summary_prompt)[0]['generated_text']
    return summary

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        video_path = temp_file.name

    frames = extract_frames(video_path)
    st.write(f"Extracted {len(frames)} frames.")

    descriptions = []
    for i, frame in enumerate(frames):
        description = describe_frame(frame)
        descriptions.append(description)
        st.write(f"Description for Frame {i * 2} seconds: {description}")

    summary = summarize_descriptions(descriptions)
    st.write(f"Summary of the video: {summary}")
