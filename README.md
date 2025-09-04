# Streamlit Agentic Chatbot

This project is a **Streamlit app** that provides an interactive chatbot interface for users.  
Behind the scenes, it connects with an **agentic workflow** that powers the chatbot’s reasoning and responses.

## Features
- Chat-like interface powered by Streamlit  
- Agentic workflow backend for dynamic chatbot responses  
- Azure OpenAI integration via environment configuration

## Setup

1. Clone this repository  

2. Create a file named **`model_client.env`** in the root directory with the following structure:

   ```env
   MODEL="gpt-5-mini"
   AZURE_ENDPOINT="https://{resource}.openai.azure.com/"
   AZURE_DEPLOYMENT="gpt-5-mini"
   API_VERSION="2025-04-01-preview"
   API_KEY="{api_key}"

   Replace {resource} and {api_key} with your own Azure OpenAI values.

3. Install dependencies:
    
    pip install -r requirements.txt

4. Run the app from the root directory:

    streamlit run app.py