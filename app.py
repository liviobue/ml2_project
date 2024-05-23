import streamlit as st
from commands import describe_frame, summarize_descriptions, textRequest
import cv2
import tempfile
import time

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

# Streamlit app
def main():
    st.title("Video Description Chatbot")

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

    # Reset button to clear the session state
    if st.button("Reset Chat"):
        reset_session()
        st.rerun()

    # Video upload area
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"], key=st.session_state['uploader_key'])

    # Frame rate input in sidebar
    st.sidebar.title("Settings")
    st.session_state['frame_rate'] = st.sidebar.number_input("Set frame rate (seconds between frame):", min_value=1, max_value=60, value=20)

    if uploaded_file and st.button("Send Video"):
        with st.spinner('Bot is processing...'):
            st.session_state['loading'] = True
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                video_path = temp_file.name

            frames = extract_frames(video_path, st.session_state['frame_rate'])
            st.write(f"Extracted {len(frames)} frames.")

            descriptions = []
            for frame in frames:
                description = describe_frame(frame)
                descriptions.append(description)

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
                response = textRequest(user_input)
                st.session_state['messages'].append({"role": "user", "content": user_input})
                st.session_state['messages'].append({"role": "bot", "content": response})
                st.session_state['loading'] = False
                st.rerun()

if __name__ == "__main__":
    main()
