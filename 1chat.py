from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get the API key from the environment variable
api_key = os.environ.get("API_KEY")  # Use get() to avoid KeyError

# Initialize the OpenAI client
if api_key:
    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully.")
else:
    print("Error: API key not found. Please ensure it is set in your environment.")

client = OpenAI(api_key=os.environ["API_KEY"])

system_prompt = ("you are a instructor for cs50")
user_prompt = input("How can I help you? ")

chat_response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    model="gpt-3.5-turbo"
)

response_text = chat_response.choices[0].message.content
print(response_text)
