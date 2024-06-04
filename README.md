# ML2 Project

## How to Get Started

1. **Clone the GitHub Repository**:
    ```bash
    git clone https://github.com/liviobue/ml2_project.git
    cd ml2_project
    ```

2. **Set Keys and MongoDB Connection**:
    - Rename `keys-template.py` to `keys.py`.
    - Add your API keys and MongoDB connection details to `keys.py`.

3. **Run the Streamlit Application**:
    ```bash
    streamlit run app.py
    ```

## Motivation

### Background

In today's digital age, the ability to access and interpret visual content is crucial. However, for visually impaired individuals, this remains a significant challenge. My motivation for this project stems from a personal connection—my neighbors are blind, and I have witnessed firsthand the difficulties they face in accessing and understanding video content.

### Problem Statement

Blind individuals often miss out on the valuable information and entertainment that videos provide. While there are existing solutions for converting text to speech and providing audio descriptions, these are often not integrated into a seamless, user-friendly platform that allows for interactive and dynamic video summarization.

### Project Relevance

This project aims to bridge this gap by developing an interactive chatbot that summarizes videos and provides audio descriptions for the visually impaired. The solution leverages advanced machine learning models and natural language processing to generate detailed and coherent summaries of video content. Additionally, the project includes functionality for users to listen to these summaries, ensuring the solution is accessible to those who need it the most.

### Key Features

1. **Interactive Video Summarization**:
    - Upload video files and receive a summarized description of the content.
    - The chatbot processes frames from the video and generates descriptive text.

2. **User Feedback Integration**:
    - Users can provide feedback on the accuracy of the summaries, ensuring continuous improvement of the system.

3. **Audio Playback**:
    - Convert text summaries into speech, allowing users to listen to the descriptions.
    - Automatically play the audio upon generation for ease of use.

4. **Customization and Flexibility**:
    - Users can set parameters such as frame rate for processing videos.
    - Option to use accurate summaries from the database for improved responses.

5. **Accessability for Blind Users**:
    - Added Help lables to button and input fields
    - Use aria-label attributes or similar alternatives to ensure each interactive element is properly described.
    

By combining these features, the project not only provides a practical tool for the visually impaired but also creates an inclusive platform that encourages user interaction and feedback. This ensures that the system evolves to better meet the needs of its users, making video content more accessible and enjoyable for everyone.

## Evaluation

### Embedding Comparison

The application includes an evaluation feature to compare AI-generated descriptions with human-written descriptions using cosine similarity of word embeddings.

- Human Description Input: Users can input a human-written description of the video.
- AI Description: The AI-generated description is taken from the first content element of the messages array.

Similarity Calculation: The cosine similarity between the human and AI descriptions is calculated using TF-IDF vectors.

### Few-Shot prompting

Few-shot prompting is used to improve the accuracy and relevance of the AI's responses. By incorporating examples of correct responses from past interactions, the AI learns to generate better responses.

### Example

Initially, the AI might respond to a user's "thank you" with an image description. After adding few-shot examples where the AI correctly responds to "thank you" with an appropriate reply, the AI learns to handle such inputs correctly.

However, new problems arose with the few/zero-shot examples. The AI began incorporating scenes from other videos. Therefore, the project owner tried to keep the chatbot under control with some prompt engineering techniques. 

### How to Use Few-Shot Prompting

- Accurate Interactions Storage: Interactions that are flagged as accurate by users are stored in a MongoDB database.
- Few-Shot Limit: Users can set the number of few-shot examples to be used in the sidebar settings.
- Accurate Only: Users can choose to use only accurate interactions for few-shot prompting.
- Check Few-Shot Limit: A button on the sidebar allows users to check if the current few-shot limit is working correctly.

### How to Evaluate

1. Go to the "Evaluation" tab in the Streamlit app.
2. Enter the human-written description in the provided text area.
3. Click the "Calculate Similarity" button to see the similarity score and visualization.

### Example Videos

https://www.pexels.com/search/videos/

## Contributing

We welcome contributions to improve this project. Please feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.