import streamlit as st
import openai
from commands import recognize, extract 

# Set up OpenAI API key
openai.api_key = API_KEY

messages = []

# Streamlit app
def main():
    st.title("Video Description Chatbot")
    
    # User input area
    user_input = st.text_area("Enter your message or upload a video frame:")
    uploaded_file = st.file_uploader("Upload a video frame", type=["jpg", "png"])
    
    if st.button("Send"):
        if uploaded_file:
            # Process text input
            recognize(user_input)
        else:
            st.warning("Please enter some text or upload an image.")


if __name__ == "__main__":
    main()
