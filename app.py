import streamlit as st
from commands import describe_frame, summarize_descriptions, textRequest, store_chat_in_mongodb, retrieve_past_interactions
import cv2
import tempfile
import time
from gtts import gTTS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# Extract frame of video
def extract_frames(video_path, frame_rate=20):
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

# Function to reset the session state
def reset_session():
    uploader_key = st.session_state.get('uploader_key', 0) + 1
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['uploader_key'] = uploader_key  # Reinitialize uploader_key

# Convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts_bytes = tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        audio_bytes = f.read()
    return audio_bytes

# Similarity Calculation Function
def calculate_similarity(human_desc, ai_desc):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([human_desc, ai_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return similarity[0][0]

# Streamlit app
def main():
    st.title("Video Description Chatbot")

    # Tabs
    tab1, tab2 = st.tabs(["Chat", "Evaluation"])

    with tab1:
        st.header("Chat")

        # Check if session state variables are initialized
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
        if 'video_processed' not in st.session_state:
            st.session_state['video_processed'] = False
        if 'loading' not in st.session_state:
            st.session_state['loading'] = False
        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ""
        if 'uploader_key' not in st.session_state:
            st.session_state['uploader_key'] = 0
        if 'frame_rate' not in st.session_state:
            st.session_state['frame_rate'] = 20
        if 'few_shot_limit' not in st.session_state:
            st.session_state['few_shot_limit'] = 5
        if 'accurate_only' not in st.session_state:
            st.session_state['accurate_only'] = True
        if 'feedback_requested' not in st.session_state:
            st.session_state['feedback_requested'] = False
        if 'pending_feedback' not in st.session_state:
            st.session_state['pending_feedback'] = None

        # Reset button to clear the session state
        if st.button("Reset Chat"):
            reset_session()
            st.rerun()

        # Video upload area
        uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"], key=st.session_state['uploader_key'])

        # Frame rate input in sidebar
        st.sidebar.title("Settings")
        st.session_state['frame_rate'] = st.sidebar.number_input("Set frame rate (seconds between frame):", min_value=1, max_value=60, value=20)
        st.session_state['few_shot_limit'] = st.sidebar.number_input("Set number of few-shot examples:", min_value=0, max_value=20, value=5)
        st.session_state['accurate_only'] = st.sidebar.radio("Use only accurate chats for few-shot prompting?", ('Yes', 'No')) == 'Yes'

        # Button to check if the few_shot_limit is working
        if st.sidebar.button("Check Few-Shot Limit"):
            try:
                # Retrieve relevant past interactions from MongoDB
                past_interactions = retrieve_past_interactions(
                    limit=st.session_state['few_shot_limit'],
                    accurate_only=st.session_state['accurate_only']
                )
                st.sidebar.success(f"Successfully retrieved {len(past_interactions)} interactions.")
                # Format the few-shot prompt
                few_shot_prompt_ = "\n\n".join([
                    "\n\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in interaction])
                    for interaction in past_interactions
                ])

                print(few_shot_prompt_)
            except Exception as e:
                st.sidebar.warning(f"Error retrieving interactions: {str(e)}")

        if st.session_state['video_processed']:
            if st.sidebar.button("Export Chat to MongoDB"):
                chat_data = {
                    "timestamp": time.time(),
                    "messages": st.session_state['messages'],
                    "accurate": False  # Default to False until user confirms
                }
                st.session_state['pending_feedback'] = chat_data
                st.session_state['feedback_requested'] = True
        
        # Feedback mechanism
        if st.session_state['feedback_requested']:
            st.sidebar.write("Did the ChatBot provide accurate answers?")
            if st.sidebar.button("Yes"):
                st.session_state['pending_feedback']['accurate'] = True
                store_chat_in_mongodb(st.session_state['pending_feedback'])
                del st.session_state['pending_feedback']
                st.session_state['feedback_requested'] = False
                st.sidebar.success("Chat data exported to MongoDB with accurate flag!")
            elif st.sidebar.button("No"):
                store_chat_in_mongodb(st.session_state['pending_feedback'])
                del st.session_state['pending_feedback']
                st.session_state['feedback_requested'] = False
                st.sidebar.warning("Chat data exported to MongoDB without accurate flag.")


        if uploaded_file and st.button("Send Video"):
            with st.spinner('Bot is processing...'):
                st.session_state['loading'] = True
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(uploaded_file.read())
                    video_path = temp_file.name

                frames = extract_frames(video_path, st.session_state['frame_rate'])
                st.write(f"Extracted {len(frames)} frames.")

                descriptions = []
                previous_description = ""

                for frame in frames:
                    description = describe_frame(frame, previous_description)
                    descriptions.append(description)
                    previous_description = description

                summary = summarize_descriptions(descriptions)
                st.session_state['messages'].append({"role": "bot", "content": summary})
                st.session_state['video_processed'] = True
                st.session_state['loading'] = False
                st.rerun()

        # Display chat messages from the session state
        for msg in st.session_state['messages']:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style="background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px 0; color: black;">
                    <b>You:</b> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #E1F5FE; padding: 10px; border-radius: 10px; margin: 5px 0; color: black;">
                    <b>Bot:</b> {msg['content']}
                </div>
                """, unsafe_allow_html=True)

        # Show text input field
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("You:", value="", key='user_input', disabled=not st.session_state['video_processed'])
            submit_button = st.form_submit_button("Send Message", disabled=not st.session_state['video_processed'])

        if submit_button:
            if user_input:
                with st.spinner('Bot is processing...'):
                    st.session_state['loading'] = True

                    try:
                        # Retrieve relevant past interactions from MongoDB
                        past_interactions = retrieve_past_interactions(
                            limit=st.session_state['few_shot_limit'],
                            accurate_only=st.session_state['accurate_only']
                        )

                        # Format the few-shot prompt
                        few_shot_prompt = "\n\n".join([
                            "\n\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in interaction])
                            for interaction in past_interactions
                        ])
                    except Exception as e:
                        few_shot_prompt = ""
                        st.sidebar.warning(f"Error retrieving interactions: {str(e)}. Will send request with without additional Shots")
                    
                    prompt = f"{few_shot_prompt}\n\nUser: {user_input}\nBot:"
                    print(prompt)
                    
                    # Generate response
                    response = textRequest(prompt)
                    st.session_state['messages'].append({"role": "user", "content": user_input})
                    st.session_state['messages'].append({"role": "bot", "content": response})
                    st.session_state['loading'] = False
                    st.rerun()

        if st.sidebar.button("Listen to Chat Messages"):
            # Get chat messages
            chat_messages = st.session_state.get("messages", [])
            chat_text = ""
            for msg in chat_messages:
                if msg["role"] == "bot":
                    chat_text += "Next message form AI Bot.\n"
                chat_text += msg["content"] + "\n"

            # Convert chat text to speech
            audio_bytes = text_to_speech(chat_text)

            # Display audio player
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # Evaluation Tab
    with tab2:
        st.header("Evaluation")

        # Input fields for human description
        human_description = st.text_area("Enter human-written description of the video")

        if st.button("Calculate Similarity"):
            try:
                if human_description and st.session_state['messages']:
                    ai_description = st.session_state['messages'][0]["content"]
                    
                    # Calculate Similarity
                    similarity = calculate_similarity(human_description, ai_description)

                    # Display Similarity
                    st.write(f"Similarity Score: {similarity}")

                else:
                    st.warning("Please enter a human description and ensure the AI description is available.")
            
            except Exception as e:
                st.error(f"An error occurred during the evaluation: {e}")

if __name__ == "__main__":
    main()
