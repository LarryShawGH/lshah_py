import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")

# Check if the API key exists
if api_key:
    genai.configure(api_key=api_key)
    print("Gemini client initialized successfully.")
else:
    print("Error: GEMINI_API_KEY not found in environment.")

# Define system prompt and get user input
system_prompt = "You are an instructor for CS50."
user_prompt = input("How can I help you? ")

# Create Gemini Pro model
model = genai.GenerativeModel('gemini-pro')

# Start the chat with context
chat = model.start_chat(history=[
    {"role": "user", "parts": [system_prompt]}  # Use this as a pseudo system message
])

# Send the user's prompt
response = chat.send_message(user_prompt)

# Print the response
print(response.text)
